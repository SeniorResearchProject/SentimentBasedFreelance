import base64
import hashlib
import hmac
import json

from django.conf import settings

def create_payload(first_name, last_name, amount, email, tx_ref):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "amount": amount,
        "email": email,
        "tx_ref": tx_ref,
    }

    return json.dumps(payload).encode()

def get_chapa_token(payload, secret_key):
    signature = hmac.new(
        secret_key.encode(),
        payload,
        hashlib.sha256
    ).digest()

    token = base64.b64encode(signature).decode()

    return token

def get_secret_key():
    return settings.CHAPAPI_SECRET_KEY
