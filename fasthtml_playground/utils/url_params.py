from fasthtml.common import *
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Optional, get_type_hints

app, rt = fast_app(live=False, debug=True)


@dataclass
class SummaryParams:
    start_date: str
    end_date: str
    business_unit: Optional[str] = None
    therapeutic_area: Optional[str] = None
    disease_indication: Optional[str] = None

    def __post_init__(self):
        # Validate date formats and convert to datetime objects
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")

            # Validate that end_date is after start_date
            if end < start:
                raise ValueError("End date must be after start date")
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Dates must be in YYYY-MM-DD format")
            raise e


@rt("/summary")
def get(**kwargs):
    # Create and validate parameters using dataclass
    params = SummaryParams(**kwargs)

    # Return the parameters in a formatted way
    return Titled(
        "URL Parameters",
        H1("Summary Parameters"),
        Div(
            *[
                P(
                    f"{field.name.replace('_', ' ').title()}: {getattr(params, field.name) or 'Not specified'}"
                )
                for field in fields(SummaryParams)
            ]
        ),
    )


if __name__ == "__main__":
    serve()
