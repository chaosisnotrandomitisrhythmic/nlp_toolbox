from fasthtml.common import *
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class SummaryParams:
    start_date: str
    end_date: str
    business_unit: Optional[str] = None
    therapeutic_area: Optional[str] = None
    disease_indication: Optional[str] = None


app, rt = fast_app(live=True, debug=True)


@rt("/summary")
def get(
    start_date: str,
    end_date: str,
    business_unit: Optional[str] = None,
    therapeutic_area: Optional[str] = None,
    disease_indication: Optional[str] = None,
):
    params = SummaryParams(**locals())

    return Titled("Summary", P(params))


serve()
