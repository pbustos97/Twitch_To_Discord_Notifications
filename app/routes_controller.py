import requests
import json
import hmac
import hashlib
import base64
from flask import Flask, request, session
from app.secret.discord_id import discord_id, discord_secret, discord_token_url, discord_revoke_url
from app.secret.http_urls import http_base, http_api, http_discord, http_redirect, http_secret_bytes

# Used to verify callback requests from twitch
def Callback_Verify(request):
    msgId = bytes(request.headers['Twitch-Eventsub-Message-Id'], request.charset)
    msgTimestamp = bytes(request.headers['Twitch-Eventsub-Message-Timestamp'], request.charset)
    msgHash = bytes(request.headers['Twitch-Eventsub-Message-Signature'], request.charset)
    msgHash = msgHash.split(b'=')
    msgHash[0] = msgHash[0].decode('ascii')
    msgHash[1] = msgHash[1].decode('ascii')
    msgData = request.data
    msg = b"".join([msgId, msgTimestamp, msgData])

    digest = None
    if msgHash[0] == 'sha256':
        digest = hmac.new(key=http_secret_bytes, msg=msg, digestmod=hashlib.sha256)
    elif msgHash[0] == 'md5':
        digest = hmac.new(key=http_secret_bytes, msg=msg, digestmod=hashlib.md5)

    # Verifies the message came from Twitch. Compare digest function requires ascii string
    if hmac.compare_digest(msgHash[1], digest.hexdigest()):
        return True
    return False

# Called if user is not logged in
def Discord_Login_Controller(request):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'client_id': discord_id,
            'client_secret': discord_secret,
            'grant_type': 'authorization_code',
            'code': request.args['code'],
            'redirect_uri': http_base + http_api + http_discord + http_redirect,
            'scope': 'identify email guilds'}
    r = requests.post(discord_token_url, data=data, headers=headers)

    # Link tokens to current session
    data = r.json()
    access_token = data['access_token']
    token_type = data['token_type']
    scope = data['scope']
    token_expiration = data['expires_in']
    refresh_token = data['refresh_token']
    session['user'] = data

    headers = {'Authorization': session['user']['token_type'] + ' ' + session['user']['access_token']}
    r = requests.get('https://discord.com/api/users/@me')
    user = json.loads(r.text)
    username = user['username']
    discriminator = user['discriminator']
    discordId = user['id']
    email = user['email']
    avatarURL = 'https://cdn.discordapp.com/avatars/{}/{}.png'.format(discordId, user['avatar'])

    userDict = {}
    userDict['discordId'] = discordId
    userDict['username'] = username
    userDict['discriminator'] = discriminator
    userDict['email'] = email
    userDict['avatarURL'] = avatarURL

    return userDict

# Called when user requests to logout
def Discord_Logout_Controller():
    b64encode = base64.b64encode((discord_id + ':' + discord_secret).encode('utf-8'))
    headers = {'Authorization': 'Basic ' + str(b64encode, "utf-8")}
    data = {'token': session['user']['refresh_token']}
    r = requests.post(discord_revoke_url, headers=headers, data=data)
    refresh_token_check = True
    if not r.ok:
        refresh_token_check = False
    data['token'] = session['user']['access_token']
    r = requests.post(discord_revoke_url, headers=headers, data=data)
    access_token_check = True
    if r.ok:
        session.pop('user', None)
    else:
        access_token_check = False
    if not refresh_token_check or not access_token_check:
        msg = ''
        if not refresh_token_check:
            msg += 'Refresh token,'
        if not access_token_check:
            msg += 'Access token,'
        return msg + ' token revocation failed', 500
    return True