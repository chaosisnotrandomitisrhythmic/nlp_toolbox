from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Insight:
    docid: str
    insight: str
    insight_vector: List[float]
    sentiment_score: float

    date: datetime
    product: str
    country: str
    region: str
    disease_area_indication: List[str] = field(default_factory=list)
    az_therapeutic_area: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    business_unit: List[str] = field(default_factory=list)
    clinical_trial: List[str] = field(default_factory=list)
    meeting: List[str] = field(default_factory=list)
    transforming_care_project: List[str] = field(default_factory=list)
    submitter: List[str] = field(default_factory=list)
    product_topic: List[str] = field(default_factory=list)
    veeva_theme: List[str] = field(default_factory=list)
    disease_indication_1: List[str] = field(default_factory=list)
    disease_indication_2: List[str] = field(default_factory=list)
    disease_indication_3: List[str] = field(default_factory=list)
    disease_indication_4: List[str] = field(default_factory=list)
    disease_indication_5: List[str] = field(default_factory=list)
