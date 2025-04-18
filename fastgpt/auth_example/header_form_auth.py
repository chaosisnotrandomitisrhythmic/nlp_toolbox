from loguru import logger
import time
from fasthtml.common import (
    FastHTML,
    P,
    RedirectResponse,
    Beforeware,
    HTTPException,
    Form,
    Input,
    Button,
    Titled,
    serve,
)

AUTH_EXPIRATION_TIME = 300


def auth_user(token):
    if token == "123":
        return {"user_id": "123", "auth_timestamp": time.time()}
    else:
        return False


def is_auth_valid(session, auth_expiration_time=AUTH_EXPIRATION_TIME):
    auth_timestamp = session.get("auth_timestamp", None)
    if not auth_timestamp:
        return False
    return (time.time() - auth_timestamp) < AUTH_EXPIRATION_TIME


def update_session(session, auth_result):
    session["user_id"] = auth_result["user_id"]
    session["auth_timestamp"] = auth_result["auth_timestamp"]
    return session


def before(req, session):
    # if not logged in, we send them to our login page
    # logged in means:
    # - 'user_id' in the session object,
    #
    logger.debug(f"session: {session}")
    logger.debug(type(session))

    query_params = req.query_params
    auth_user = session.get("user_id", None)
    az_auth_token = req.headers.get("x-az-auth-token", None)

    if not is_auth_valid(session):
        session.clear()
        return RedirectResponse(f"/login?{query_params}", status_code=303)
    elif az_auth_token:
        auth_result = auth_user(az_auth_token)
        if auth_result:
            update_session(session, auth_result)
        else:
            session.clear()
            return RedirectResponse(f"/login?{query_params}", status_code=303)


bware = Beforeware(before, skip=["/login"])


app = FastHTML(before=bware)


@app.get("/")
def home(request, conversation_id: int):

    return P(f"Hello World {request.query_params}")


@app.get("/login")
def login(request, conversation_id: int):
    # Create a login form with token input and preserve conversation_id
    form = Form(
        Input(id="token", name="token", placeholder="Enter your token"),
        Input(type="hidden", name="conversation_id", value=str(conversation_id)),
        Button("Login", type="submit"),
        method="post",
        action="/login",
    )
    return Titled("Login", form)


@app.post("/login")
async def login_post(request, session):
    form = await request.form()
    token = form.get("token")
    conversation_id = form.get("conversation_id")

    # Try to authenticate with the token
    auth_result = auth_user(token)
    if auth_result:
        update_session(session, auth_result)
        return RedirectResponse(f"/?conversation_id={conversation_id}", status_code=303)
    else:
        # If authentication fails, redirect back to login with conversation_id
        return RedirectResponse(
            f"/login?conversation_id={conversation_id}", status_code=303
        )


serve()
