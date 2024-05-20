import time
from google.auth.transport import requests
from google.oauth2 import id_token

class Google:
    # Google class to fetch the user info and return it

   @staticmethod
   def validate(auth_token):
        try:
            idinfo = id_token.verify_oauth2_token(
                auth_token, requests.Request(), clock_skew_in_seconds=10
            )

            if 'accounts.google.com' in idinfo['iss']:
                return idinfo
            else:
                raise ValueError('Invalid token issuer')
        except:
            # raise ValueError('Token validation failed: {}'.format(str(e)))
            return "Token validation failed"