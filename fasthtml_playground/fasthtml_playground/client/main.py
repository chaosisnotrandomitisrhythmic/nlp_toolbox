from dataclasses import dataclass
import os


import httpx
from fasthtml.common import *
from html_to_markdown import convert_to_markdown
from monsterui.all import *
from starlette.requests import Request

# Choose a theme color (blue, green, red, etc)
hdrs = Theme.zinc.headers()
# Create your app with the theme
app, rt = fast_app(hdrs=hdrs, live=True, debug=True)

# Configure external API settings
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "30.0"))

# Create a single HTTP client for the application
http_client = httpx.AsyncClient(timeout=API_TIMEOUT)


@dataclass
class UserSelections:
    email: str
    phone: str
    age: int


profile_form = Form(
    # Remove the traditional form submission
    # method="post",
    # action="/summary",
    # Add HTMX attributes for form submission
    hx_post="summary",
    hx_target="#content",
    hx_swap="innerHTML",
    hx_indicator="#loading",
)(
    Fieldset(
        Label("Email", Input(name="email")),
        Label("Phone", Input(name="phone")),
        Label("Age", Input(name="age")),
    ),
    Button("Load", type="submit"),
)


@rt("/")
def get():
    return Titled(
        "Retriever",
    ), Container(
        profile_form,
        # A place to put content from request
        Div(id="content"),
        # Loading indicator ready for htmx use
        # For more options see https://monsterui.answer.ai/api_ref/docs_loading
        Loading(id="loading", htmx_indicator=True),
    )


@rt("/summary")
async def post(request: Request):
    # Get form data from the request
    form_data = await request.form()
    email = form_data.get("email", "")
    phone = form_data.get("phone", "")
    age = form_data.get("age", "")

    # Create a profile object with the form data
    user_selections = UserSelections(
        email=email, phone=phone, age=int(age) if age else 0
    )
    print(user_selections)

    try:
        response = await http_client.get(f"{API_BASE_URL}/dummy-summary")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        markdown_content = convert_to_markdown(data["result"]["summary"])
        return Div(render_md(markdown_content), cls="prose")
    except httpx.HTTPError as e:
        return Div(f"Error fetching data: {str(e)}", cls="error")
    except Exception as e:
        return Div(f"An unexpected error occurred: {str(e)}", cls="error")


# Clean up the HTTP client when the application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()


serve()
