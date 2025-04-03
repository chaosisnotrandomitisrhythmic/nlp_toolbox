from dataclasses import dataclass
import os
from typing import Optional


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


def profile_form(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    business_unit: Optional[str] = None,
    therapeutic_area: Optional[str] = None,
    disease_indication: Optional[str] = None,
):
    return Form(
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
            Label(
                "Start Date",
                Input(
                    name="start_date",
                    type="date",
                    value=start_date if start_date else "",
                ),
            ),
            Label(
                "End Date",
                Input(name="end_date", type="date", value=end_date if end_date else ""),
            ),
            Label(
                "Business Unit",
                Input(
                    name="business_unit", value=business_unit if business_unit else ""
                ),
            ),
            Label(
                "Therapeutic Area",
                Input(
                    name="therapeutic_area",
                    value=therapeutic_area if therapeutic_area else "",
                ),
            ),
            Label(
                "Disease Indication",
                Input(
                    name="disease_indication",
                    value=disease_indication if disease_indication else "",
                ),
            ),
        ),
        Button("Load Summary", type="submit"),
    )


@rt("/")
def get(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    business_unit: Optional[str] = None,
    therapeutic_area: Optional[str] = None,
    disease_indication: Optional[str] = None,
):
    print(start_date, end_date, business_unit, therapeutic_area, disease_indication)
    return Titled(
        "Retriever",
    ), Container(
        profile_form(
            start_date, end_date, business_unit, therapeutic_area, disease_indication
        ),
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

    response = await http_client.post(
        f"{API_BASE_URL}/dummy-summary",
        json={
            "start_date": form_data.get("start_date", ""),
            "end_date": form_data.get("end_date", ""),
            "business_unit": form_data.get("business_unit", ""),
            "therapeutic_area": form_data.get("therapeutic_area", ""),
            "disease_indication": form_data.get("disease_indication", ""),
        },
    )

    data = response.json()
    markdown_content = convert_to_markdown(data["result"]["summary"])

    return Div(render_md(markdown_content), cls="prose")


# Clean up the HTTP client when the application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()


serve()
