import time

from fasthtml.common import RedirectResponse, Beforeware
from loguru import logger

AUTH_EXPIRATION_TIME = 300


def auth_user(token):
    """
    Authenticates a user based on their token.

    Args:
        token (str): The authentication token to validate

    Returns:
        dict: If authentication is successful, returns a dictionary containing:
              - user_id: The authenticated user's ID
              - auth_timestamp: The current timestamp
        bool: False if authentication fails
    """
    if token == "123":
        return {"user_id": "123", "auth_timestamp": time.time()}
    else:
        return False


def is_auth_valid(session, auth_expiration_time=AUTH_EXPIRATION_TIME):
    """
    Checks if the current session authentication is still valid.

    Args:
        session: The Starlette session object containing authentication data
        auth_expiration_time (int, optional): The maximum age of authentication in seconds.
                                            Defaults to AUTH_EXPIRATION_TIME (300 seconds)

    Returns:
        bool: True if the session is valid and not expired, False otherwise
    """
    auth_timestamp = session.get("auth_timestamp", None)
    if not auth_timestamp:
        return False
    return (time.time() - auth_timestamp) < AUTH_EXPIRATION_TIME


def update_session(session, auth_result):
    """
    Updates the session with new authentication data.

    Args:
        session: The Starlette session object to update
        auth_result (dict): Dictionary containing:
                          - user_id: The authenticated user's ID
                          - auth_timestamp: The timestamp of authentication

    Returns:
        session: The updated session object
    """
    session["user_id"] = auth_result["user_id"]
    session["auth_timestamp"] = auth_result["auth_timestamp"]
    return session


def before(req, session):
    """
    Middleware function that handles authentication before processing a request.

    This function checks if the user is authenticated and handles Azure authentication tokens.
    If the user is not authenticated or the authentication is expired, they are redirected to the login page.

    Args:
        req: The incoming request object containing headers and query parameters
        session: A Starlette session object that maps to a signed cookie on the client side,
                containing user authentication data including auth_timestamp and user_id

    Returns:
        RedirectResponse: If authentication fails, redirects to the login page with original query parameters
        None: If authentication is successful, allows the request to proceed

    The function performs the following checks:
    1. Verifies if the session has a valid authentication timestamp
    2. If not valid, clears the session and redirects to login
    3. If an Azure auth token is present, validates it and updates the session
    4. If token validation fails, clears the session and redirects to login
    """
    logger.debug(f"session: {session}")

    query_params = req.query_params
    auth_user = session.get("user_id", None)
    az_auth_token = req.headers.get("x-az-auth-token", None)

    # Check if user is alreadylogged with a valid timestamp
    if not is_auth_valid(session):
        session.clear()
        return RedirectResponse(f"/login?{query_params}", status_code=303)
    # if there is an auth token, validate it
    elif az_auth_token:
        auth_result = auth_user(az_auth_token)
        if auth_result:
            update_session(session, auth_result)
        else:
            session.clear()
            return RedirectResponse(f"/login?{query_params}", status_code=303)


auth_bware = Beforeware(before, skip=["/login"])
