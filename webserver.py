import requests
import json
from flask import Flask, request, abort
from flask_sslify import SSLify
from twitch_id import http_secret_bytes, discord_webhook_url
import hmac
import hashlib

app = Flask(__name__)
sslify = SSLify(app)

twitch_url = 'https://api.twitch.tv/helix/eventsub/subscriptions'

# Website index for 
@app.route('/', methods=['POST'])
def index():
    return 'success', 200

# Receives the Twitch Challenge and sends recieved data to discord webhook
@app.route('/webhooks/callback', methods=['POST'])
def callback():
    if request.method == 'POST':
        # Bytes requried for hmac class
        msgId = bytes(request.headers['Twitch-Eventsub-Message-Id'], request.charset)
        msgTimestamp = bytes(request.headers['Twitch-Eventsub-Message-Timestamp'], request.charset)
        msgHash = bytes(request.headers['Twitch-Eventsub-Message-Signature'], request.charset)
        msgHash = msgHash.split(b'=')
        msgHash[0] = msgHash[0].decode('ascii')
        msgHash[1] = msgHash[1].decode('ascii')
        msgData = request.data
        msg = b"".join([msgId, msgTimestamp, msgData])

        challenge = None
        if request.json.get('challenge'):
            challenge = request.json['challenge']
        digest = None
        if msgHash[0] == 'sha256':
            digest = hmac.new(key=http_secret_bytes, msg=msg, digestmod=hashlib.sha256)
        elif msgHash[0] == 'md5':
            digest = hmac.new(key=http_secret_bytes, msg=msg, digestmod=hashlib.md5)

        # Verifies the message came from Twitch. Compare digest function requires ascii string
        if hmac.compare_digest(msgHash[1], digest.hexdigest()):
            print('Message verified')
            if challenge != None:
                print('Returning challenge')
                return challenge
            else:
                # Throw webhook data to discord webhook
                print('Attempting to send webhook to discord')
                # Check if there is event inside payload
                if request.json['event']:
                    discord_data = {}
                    # Check if subscription type is stream.online
                    if request.headers['Twitch-Eventsub-Subscription-Type'] == 'stream.online':
                        username = request.json['event']['broadcaster_user_name']
                        link = 'https://twitch.tv/' + request.json['event']['broadcaster_user_login']
                        discord_data['content'] = '{username} has gone live! {link}'.format(username=username, link=link)
                    r = requests.post(discord_webhook_url, json=discord_data)
                    if r.ok:
                        print('Webhook sent to discord')
            return 'Ok', 200
        else:
            abort(400)
        return 'success', 200
    else:
        abort(400)

if __name__ == '__main__':
    app.run(port=80)