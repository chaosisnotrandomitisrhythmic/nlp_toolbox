from fastapi import FastAPI
import asyncio
from typing import Optional
from pydantic import BaseModel


class SummaryParams(BaseModel):
    start_date: str
    end_date: str
    business_unit: Optional[str] = None
    therapeutic_area: Optional[str] = None
    disease_indication: Optional[str] = None


app = FastAPI()


@app.post("/dummy-summary")
async def get_dummy_summary(params: SummaryParams):
    await asyncio.sleep(2)

    html_content = f"""
    <html>
        <body>
            <h1>Dummy Summary Report</h1>
            <div class="summary">
                <h2>Key Findings</h2>
                <ul>
                    <li>Date Range: {params.start_date} to {params.end_date}</li>
                    <li>Business Unit: {params.business_unit or 'Not specified'}</li>
                    <li>Therapeutic Area: {params.therapeutic_area or 'Not specified'}</li>
                    <li>Disease Indication: {params.disease_indication or 'Not specified'}</li>
                </ul>
                <p>This is a dummy summary generated for demonstration purposes.</p>
            </div>
        </body>
    </html>
    """
    return {"result": {"id": "dummy-001", "summary": html_content}}


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI server"}
