import requests
import json
import hmac
import hashlib
from flask import Flask, request, abort, render_template, session, url_for, redirect
from flask_sslify import SSLify
from secret.http_urls import http_secret_bytes, http_callback, http_base, http_login, http_api, http_discord, http_redirect
from secret.discord_id import discord_webhook_url, discord_token_url, discord_revoke_url, discord_redirect_url, discord_guilds_url, discord_id, discord_secret
from routes_controller import Callback_Verify, Discord_Login_Controller, Discord_Logout_Controller
from secret import secret_key

app = Flask(__name__)
sslify = SSLify(app)
app.config['SECRET_KEY'] = secret_key

twitch_url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

# Website index for Signing in to add bot to server
@app.route('/', methods=['POST', 'GET'])
def index():
    if 'user' in session:
        header_auth = session['user']['token_type'] + ' ' + session['user']['access_token']
        headers = {'client-id': discord_id,
                   'Authorization': header_auth,
                   'Scope': session['user']['scope']}
        r = requests.get('https://discord.com/api/users/@me', headers=headers)
        print(r)
        #print(r.data)
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect(discord_redirect_url)

# Sign in with Discord to login
@app.route('/api/discord/redirect', methods=['POST', 'GET'])
def discord_login():
    Discord_Login_Controller(request)
    print(session['user'])
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
    return render_template('guilds.html', guilds=guilds)

# Should only be called when user is logged in
@app.route('/guilds/<id>')
def channels():
    if 'user' not in session:
        return 'You need to be logged in to see the guild channels', 400
    
    headers = {'Authorization': session['user']['token_type'] + ' ' + session['user']['access_token']}
    channels = []
    return render_template('channels.html', channels=channels)

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
                        r = requests.post(discord_webhook_url, json=discord_data)
                        if not r.ok:
                            return 'Failed to send webhook', 400
            return 'Ok', 200
        else:
            abort(400)
        return 'Ok', 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run(port=80)