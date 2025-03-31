from fasthtml.common import *
from monsterui.all import *
import httpx
from html_to_markdown import convert_to_markdown

# Choose a theme color (blue, green, red, etc)
hdrs = Theme.zinc.headers()

# Create your app with the theme
app, rt = fast_app(hdrs=hdrs, live=True)


@rt
def index():
    return Titled(
        "Retriever",
        # Button to trigger an HTMX request
        Button(
            "Load",
            id="load",
            # Trigger HTMX request to add content to #content
            get=get_summary,
            hx_target="#content",
            hx_swap="innerHTML",
            # While request in flight, show loading indicator
            hx_indicator="#loading",
        ),
        # A place to put content from request
        Div(id="content"),
        # Loading indicator ready for htmx use
        # For more options see https://monsterui.answer.ai/api_ref/docs_loading
        Loading(id="loading", htmx_indicator=True),
    )


@rt
async def get_summary():
    # Sleep for a second to simulate a long request
    # await asyncio.sleep(1)
    # return P("Loading Demo")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("http://localhost:8000/dummy-summary")
        data = response.json()

    markdown_content = convert_to_markdown(data["result"]["summary"])

    return Div(render_md(markdown_content), cls="prose")


serve()
