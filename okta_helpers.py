import asyncio
import json
from pathlib import Path

from okta_jwt_verifier import AccessTokenVerifier, IDTokenVerifier

loop = asyncio.get_event_loop()


def is_access_token_valid(token, issuer):
    jwt_verifier = AccessTokenVerifier(issuer=issuer, audience='api://default')
    try:
        loop.run_until_complete(jwt_verifier.verify(token))
        return True
    except Exception:
        return False


def is_id_token_valid(token, issuer, client_id, nonce):
    jwt_verifier = IDTokenVerifier(issuer=issuer, client_id=client_id, audience='api://default')
    try:
        loop.run_until_complete(jwt_verifier.verify(token, nonce=nonce))
        return True
    except Exception:
        return False


def load_config(fname):
    config = None
    with open(fname) as f:
        config = json.load(f)
    return config


THIS_FOLDER = Path(__file__).parent.resolve()
fname_abs = THIS_FOLDER / "client_secrets.json"
config = load_config(fname_abs)
