from twitch.api.base import TwitchAPI
from twitch.constants import STREAM_TYPES, STREAM_TYPE_LIVE

class SenServiceCore(TwitchAPI):
    def __init__(self, client_id, oauth_token=None, client_secret=None):
        super().__init__(client_id, oauth_token=oauth_token)

        self._client_secret = client_secret

    def _RefreshToken(self):
        OAuthResponse = self._request_post(
            'oauth2/token', 
            None,
            {
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'grant_type': 'client_credentials'
            },
            'https://id.twitch.tv/'
        )

        if OAuthResponse['access_token'] != '':
             return OAuthResponse['access_token']
        else:
            exit()

    def _checkToken(self):
        response = self._request_get('', None)

        if response['token']['valid']:
            if response['token']['expires_in'] <= 3600:
                token = self._RefreshToken()
            else:
                token = self._oauth_token
        else:
            token = self._RefreshToken()
        
        return token