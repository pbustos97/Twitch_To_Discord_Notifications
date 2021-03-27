import requests
import json
import asyncio
from flask import Flask, request, abort, render_template, session, url_for, redirect
from flask_sslify import SSLify
from app import app, db
from app.secret.discord_id import discord_webhook_url, discord_redirect_url, discord_guilds_url, discord_id
from app.routes_controller import Callback_Verify, Discord_Login_Controller, Discord_Logout_Controller
from app.secret import secret_key
from app.discord_async import Discord_Async
from app.models import Channel, Guild, User, Webhook, Notification

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

bot = Discord_Async(db=db)
#bot.start()

@app.route('/', methods=['POST', 'GET'])
def index():
    if 'user' in session:
        header_auth = session['user']['token_type'] + ' ' + session['user']['access_token']
        headers = {'client-id': discord_id,
                   'Authorization': header_auth,
                   'Scope': session['user']['scope']}
        r = requests.get('https://discord.com/api/users/@me', headers=headers)
    return render_template('index.html')

# Website index for Signing in to add bot to server
@app.route('/login')
def login():
    return redirect(discord_redirect_url)

# Sign in with Discord to login
@app.route('/api/discord/redirect', methods=['POST','GET'])
def discord_login():
    user = Discord_Login_Controller(request)
    print(session['user'])
    
    bot.discordBot.addUserToTable(user)
    return redirect(url_for('index'))

# Drops the session linked to a user that requests to logout
@app.route('/logout')
def logout():
    if 'user' in session:
        res = Discord_Logout_Controller()
        if res == True:
            return redirect(url_for('index'))
        else:
            return res
    else:
        return 'No user found', 500

# Should only be called when user is logged in
@app.route('/guilds')
def guilds():
    if 'user' not in session:
        return 'You need to be logged in to see your guilds', 400
    
    headers = {'Authorization': session['user']['token_type'] + ' ' + session['user']['access_token']}
    r = requests.get(discord_guilds_url, headers=headers)
    guilds = json.loads(r.text)
    g = []
    for guild in guilds:
        bot.discordBot.addGuildToTable(guild['id'], guild['name'])
        if bot.discordBot.isMember(int(guild['id'])):
            g.append(guild)
    return render_template('guilds.html', guilds=g)

# Should only be called when user is logged in
@app.route('/guilds/<id>')
def guild_channels(id):
    if 'user' not in session:
        return 'You need to be logged in to see the guild channels', 400
    
    headers = {'Authorization': session['user']['token_type'] + ' ' + session['user']['access_token']}

    asyncio.run(bot.discordBot.get_channels(guildId=int(id)))

    channels = Channel.query.filter_by(guildId=int(id))
    return render_template('channels.html', channels=channels)

@app.route('/channels/<id>')
def channels(id):
    if 'user' not in session:
        return 'You need to be logged in to see the guild channels', 400
    
    headers = {'Authorization': session['user']['token_type'] + ' ' + session['user']['access_token']}

    webhooks = asyncio.run_coroutine_threadsafe(bot.discordBot.get_webhooks(channelId=int(id)), bot.discordLoop).result()

    for webhook in webhooks:
        bot.discordBot.addWebhookToTable(webhook, int(id))

    webhooks = Webhook.query.filter_by(channelId=int(id))
    return render_template('webhooks.html', webhooks=webhooks)

@app.route('/webhooks/<id>')
def webhooks(id):
    if 'user' not in session:
        return 'You need to be logged in to see the channel webhooks', 400
    
    headers = {'Authorization': session['user']['token_type'] + ' ' + session['user']['access_token']}

    return render_template('notifications.html')

# Receives the Twitch Challenge and sends recieved data to discord webhook
@app.route('/api/webhooks/callback', methods=['POST'])
def callback():
    if request.method == 'POST':
        verified = Callback_Verify(request)

        # If verified, return challenge to Twitch if it exists

        if verified:
            if request.json.get('challenge'):
                #print('Challenge sent to twitch')
                return request.json['challenge']

            else:
                #print('Post is not a challenge')
                # Check if there is event inside payload
                if request.json['event']:
                    discord_data = {}
                    # Check if subscription type is stream.online
                    if request.headers['Twitch-Eventsub-Subscription-Type'] == 'stream.online':
                        username = request.json['event']['broadcaster_user_name']
                        link = 'https://twitch.tv/' + request.json['event']['broadcaster_user_login']
                        discord_data['content'] = '{username} has gone live! {link}'.format(username=username, link=link)
                        notification = Notification.query.filter_by(notificationId=request.json['subscription']['id'])
                        r = requests.post(discord_webhook_url, json=discord_data)
                        #webhook = Webhook.query.filter_by(webhookId=notification.webhookId)
                        #r = requests.post(webhook.webhookURL, json=discord_data)
                        if not r.ok:
                            return 'Failed to send webhook', 500
            return 'Ok', 200
        else:
            abort(400)
        return 'Ok', 200
    else:
        abort(400)

# Deletes the webhook ID and linked notifications
@app.route('/api/delete/<id>', methods=['DELETE'])
def deleteWebhook(id):
    if Webhook.query.filter_by(webhookId=id):
        return 200
    else:
        abort(400)