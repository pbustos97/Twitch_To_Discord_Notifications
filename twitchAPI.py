import json
import requests
from requests.structures import CaseInsensitiveDict
from twitch_id import twitch_id, twitch_secret

# Class for authentication
class miniTwitchWrapper():
    def __init__(self):
        self.twitch_id = twitch_id
        self.twitch_secret = twitch_secret
        self.twitch_auth_payload = {'client_id': self.twitch_id, 'client_secret': self.twitch_secret, 'grant_type': 'client_credentials'}
        self.twitch_auth_base_url = 'https://id.twitch.tv/'
        self.twitch_oauth2_url = self.twitch_auth_base_url + 'oauth2/token'
        self.twitch_access_token = ''
        self.twitch_access_token_type = ''
        self.twitch_auth_headers = {}

    # Sets access token for the wrapper
    def setAccessToken(self):
        r = requests.post(self.twitch_oauth2_url, data=self.twitch_auth_payload, timeout=10)
        response = json.loads(r.text)
        self.twitch_access_token = response['access_token']
        self.twitch_access_token_type = str(response['token_type']).capitalize()
        self.twitch_auth_headers['Authorization'] = self.twitch_access_token_type + ' ' + self.twitch_access_token
        self.twitch_auth_headers['client-id'] = self.twitch_id
        print('New token set')

    # Checks if access token is valid before calling further functions
    def checkAccessToken(self, response):
        if 'error' in response or response.ok == False:
            print('An error has happened, getting a new token')
            print(response.text)
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
        self.twitch_user_id = ''
        self.twitch_user_follows = []

    # Gets the user's ID of the Twitch username passed through
    def setUserId(self, name):
        payload = {'login': str(name)}
        r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users', params=payload, headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r) == False:
            r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users', params=payload, headers=self.twitch_wrapper.twitch_auth_headers)
        response = json.loads(r.text)
        self.twitch_user_id = response['data'][0]['id']
        print(self.twitch_user_id)

    # Gets the assigned user's following list and stores their IDs
    def setUserFollows(self):
        payload = {'from_id': self.twitch_user_id}
        r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users/follows', params = payload, headers=self.twitch_wrapper.twitch_auth_headers)
        if self.twitch_wrapper.checkAccessToken(r) == False:
            r = requests.get(self.twitch_api_base_url + self.twitch_helix + 'users/follows', params = payload, headers=self.twitch_wrapper.twitch_auth_headers)
        response = json.loads(r.text)
        #print(response['data'])
        self.twitch_user_follows = []
        for followed in response['data']:
            self.twitch_user_follows.append(str(followed['to_id']))

    #def getFollowedOnline(self):
        

test = miniTwitchWrapper()
test.setAccessToken()
test2 = miniTwitchBot(test)
test2.setUserId('doublediscord')
test2.setUserFollows()
#print(test.twitch_access_token)
#print(test.twitch_access_token_type)