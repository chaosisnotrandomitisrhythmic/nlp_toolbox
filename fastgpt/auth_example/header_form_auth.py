from loguru import logger
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


def auth_user(token):
    if token == "123":
        return {"user_id": "123"}
    else:
        return False


def before(req, session):
    # if not logged in, we send them to our login page
    # logged in means:
    # - 'user_id' in the session object,
    #
    logger.debug(f"session: {session}")

    query_params = req.query_params
    auth_user = session.get("user_id", None)
    token = req.headers.get("x-az-auth-token")

    # If no token and no user_id in session, redirect to login
    if not token and not auth_user:
        return RedirectResponse(f"/login?{query_params}", status_code=303)

    # If there's a token, try to verify it
    if token:
        auth_user = auth_user(token)
        if auth_user:
            session["user_id"] = auth_user["user_id"]
        else:
            return RedirectResponse(f"/login?{query_params}", status_code=303)


bware = Beforeware(before, skip=["/login"])


app = FastHTML(before=bware)


@app.get("/")
def home(conversation_id: int):
    return P(f"Hello World {conversation_id}")


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
        session["user_id"] = auth_result["user_id"]
        return RedirectResponse(f"/?conversation_id={conversation_id}", status_code=303)
    else:
        # If authentication fails, redirect back to login with conversation_id
        return RedirectResponse(
            f"/login?conversation_id={conversation_id}", status_code=303
        )


serve()
