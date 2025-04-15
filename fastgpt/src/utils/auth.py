import json
import urllib.parse
import os

from fasthtml.common import Beforeware, RedirectResponse
from fasthtml.oauth import HuggingFaceClient
from loguru import logger

AUTH_CALLBACK_PATH = "/auth_redirect"

# Auth client setup for GitHub
auth_client = HuggingFaceClient(
    client_id=os.getenv("HUGGINGFACE_CLIENT_ID"),
    client_secret=os.getenv("HUGGINGFACE_CLIENT_SECRET"),
)


def parse_url_encoded_json(value: str) -> dict:
    try:
        decoded = urllib.parse.unquote(value)
        return json.loads(decoded)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse URL-encoded JSON: {e}")
        return {}


def before(req, session):
    # if not logged in, we send them to our login page
    # logged in means:
    # - 'user_id' in the session object,
    # - 'auth' in the request object

    # Store query params in session (signed cookies) to persist through auth redirect
    # When users authenticate, they are redirected back to our callback URL
    # Using session storage ensures we don't lose the query parameters during this flow
    query_params = req.query_params
    if "interro_selection" in query_params:
        session["interro_selection"] = parse_url_encoded_json(
            query_params["interro_selection"]
        )
    elif not "interro_selection" in session:
        session["interro_selection"] = {}

    auth = req.scope["auth"] = session.get("user_id", None)
    logger.debug(f"session: {session}")
    if not auth:
        return RedirectResponse("/login", status_code=303)


bware = Beforeware(before, skip=["/login", AUTH_CALLBACK_PATH])
