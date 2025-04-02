from fasthtml.common import *
from monsterui.all import *


# Choose a theme color (blue, green, red, etc)
hdrs = Theme.zinc.headers()
# Create your app with the theme
app, rt = fast_app(hdrs=hdrs, live=True, debug=True)

# Make messages a list that can be modified
messages = [
    "This message is from the server",
    "This is another message from the server",
]


@rt("/")
def get():
    return Main(
        *[P(m) for m in messages],
        A("Link to page 2 (to add messages)", href="/page2"),
    )


@rt("/page2")
def get():
    return Main(
        P("Add a message with the form below"),
        Form(  # How to do early input validation
            Fieldset(
                Label("Message", Input(name="message")),
                Label("Person", Input(name="person")),
            ),
            Button("Submit"),
            action="/message",
            method="post",
        ),
    )


@rt("/message")
async def post(request):
    # request is a starlette.requests.Request object
    form_data = await request.form()

    # Get the message from the form data using request.data
    print(form_data)
    message = form_data.get("message", "").strip()
    person = form_data.get("person", "").strip()
    if message and person:  # do better input validation here
        messages.append(f"{person}: {message}")

    return Redirect("/")


serve()
