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
        Div(
            *[P(m) for m in messages],
            id="messages",
        ),
        Div(
            Form(  # How to do early input validation
                Fieldset(
                    Label("Message", Input(name="message")),
                    Label("Person", Input(name="person")),
                ),
                Button("Submit"),
                hx_post="message",
                hx_target="#messages",
                id="message-form",
            ),
        ),
    )


# @rt("/page2")
# def get():
#     return Main(
#         P("Add a message with the form below"),
#         Form(  # How to do early input validation
#             Fieldset(
#                 Label("Message", Input(name="message")),
#                 Label("Person", Input(name="person")),
#             ),
#             Button("Submit"),
#             action="/message",
#             method="post",
#         ),
#     )


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

    # Return both the updated messages div and a cleared form
    return (
        Div(*[P(m) for m in messages], id="messages"),
        Form(  # Return a fresh form with empty inputs
            Fieldset(
                Label("Message", Input(name="message")),
                Label("Person", Input(name="person")),
            ),
            Button("Submit"),
            hx_post="message",
            hx_target="#messages",
            id="message-form",
            hx_swap_oob="true",  # This tells HTMX to update this element out-of-band
        ),
    )


serve()
