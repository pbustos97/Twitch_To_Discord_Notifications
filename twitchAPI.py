import json
import requests
from twitch_id import twitch_id, twitch_secret, http_secret, http_callback

# Class for authentication
class miniTwitchWrapper():
    def __init__(self):
        self.twitch_id = twitch_id
        self.twitch_secret = twitch_secret

        self.twitch_auth_payload = {'client_id': self.twitch_id, 
                                    'client_secret': self.twitch_secret, 
                                    'grant_type': 'client_credentials'}
        self.twitch_auth_base_url = 'https://id.twitch.tv/'
        self.twitch_auth_headers = {}

        self.twitch_oauth2_url = self.twitch_auth_base_url + 'oauth2/token'
        self.twitch_access_token = ''
        self.twitch_access_token_type = ''

        

    # Sets access token for the wrapper
    def setAccessToken(self):
        r = requests.post(self.twitch_oauth2_url, data=self.twitch_auth_payload, timeout=10)

        response = json.loads(r.text)
        self.twitch_access_token = response['access_token']

        # Capitalization required for Twitch Authentication
        self.twitch_access_token_type = str(response['token_type']).capitalize()
        self.twitch_auth_headers['Authorization'] = self.twitch_access_token_type + ' ' + self.twitch_access_token
        self.twitch_auth_headers['client-id'] = self.twitch_id
        print('New token set')

    # Checks if access token is valid before calling further functions
    def checkAccessToken(self, response, methodName):
        if 'error' in response or response.ok == False:
            print('An error has happened, getting a new token')
            print(methodName + ': ' + response.text + ' from ' + response.url)
            try:
                self.setAccessToken()
            except:
                print('Error getting new token')
            return False
        else:
            return True

# Class for accessing Twitch API
class miniTwitchBot():
    def __init__(self, wrapper):
        self.twitch_wrapper = wrapper
        self.twitch_api_base_url = 'https://api.twitch.tv/'
        self.twitch_helix = 'helix/'

        self.twitch_eventsub = 'eventsub/'
        self.twitch_eventsub_headers = {'client-id': self.twitch_wrapper.twitch_id,
                                        'Authorization': self.twitch_wrapper.twitch_access_token,
                                        'Content-Type': "application/json"}
        self.twitch_eventsub_data = {'type': 'stream.online', 
                                    'version': '1', 
                                    'condition': {'broadcaster_user_id': ''}, 
                                    'transport': {'method': 'webhook', 
                                                  'callback': http_callback, 
                                                  'secret': http_secret}}

        self.twitch_hub = 'hub/'
        self.twitch_hub_data = {}
        self.twitch_hub_headers = {}

        self.twitch_user_id = ''
        self.twitch_user_follows = []

    # Gets the user's ID of the Twitch username passed through
    def setUserId(self, name):
        payload = {'login': str(name)}
        r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users', params=payload, headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r, 'setUserId') == False:
            r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users', params=payload, headers=self.twitch_wrapper.twitch_auth_headers)
        response = json.loads(r.text)
        self.twitch_user_id = response['data'][0]['id']

    # Gets the assigned user's following list and stores their IDs
    def setUserFollows(self):
        payload = {'from_id': self.twitch_user_id}
        r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users/follows', params = payload, headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r, 'setUserFollows') == False:
            r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users/follows', params = payload, headers=self.twitch_wrapper.twitch_auth_headers)
        response = json.loads(r.text)
        self.twitch_user_follows = []
        for followed in response['data']:
            self.twitch_user_follows.append(str(followed['to_id']))
            print(followed['to_id'] + ': ' + followed['to_name'])

    # Creates an EventSub endpoint for webhook notifications
    def setEventSub(self, followedId):
        self.twitch_eventsub_data['condition']['broadcaster_user_id'] = str(followedId)
        r = requests.post(self.twitch_api_base_url + self.twitch_helix + self.twitch_eventsub + 'subscriptions/', json=self.twitch_eventsub_data, headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r, 'setEventSub') == False:
            r = requests.post(self.twitch_api_base_url + self.twitch_helix + self.twitch_eventsub + 'subscriptions/', json=self.twitch_eventsub_data, headers=self.twitch_wrapper.twitch_auth_headers)
        response = json.loads(r.text)
        print('setEventSub: ' + r.text)

    # Deletes an EventSub subscription
    def deleteEventSub(self, subscriptionId):
        r = requests.delete(self.twitch_api_base_url + self.twitch_helix + self.twitch_eventsub + 'subscriptions', data={'id':str(subscriptionId)}, headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r, 'deleteEventSub') == False:
            r = requests.delete(self.twitch_api_base_url + self.twitch_helix + self.twitch_eventsub + 'subscriptions', data={'id':str(subscriptionId)}, headers=self.twitch_wrapper.twitch_auth_headers)
        print('deleteEventSub: Deleted event notifications for ' + subscriptionId)

    # Gets EventSub subscriptions
    def getEventSub(self):
        response = self.getEventSubHelper('getEventSub')
        print('getEventSub: ' + r.text)

        # Deletes all webhooks that have failed callback verification or have revoked authorization
        for subscription in response['data']:
            if subscription['status'] == 'webhook_callback_verification_failed' or subscription['status'] == 'authorization_revoked':
                self.deleteEventSub(subscription['id'])
    
    def getEventSubHelper(self, methodName):
        r = requests.get(self.twitch_api_base_url + self.twitch_helix + self.twitch_eventsub + 'subscriptions', headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r, methodName) == False:
            r = request.get(self.twitch_api_base_url + self.twitch_helix + self.twitch_eventsub + 'subscriptions', headers=self.twitch_wrapper.twitch_auth_headers)
        return json.loads(r.text)

    def deleteAllEventSub(self):
        response = self.getEventSubHelper('deleteAllEventSub')
        for subscription in response['data']:
            self.deleteEventSub(subscription['id'])