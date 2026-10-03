from pydantic import BaseModel, Field
from typing import List, Literal

class Biomarker(BaseModel):
    marker: str = Field(..., description="Name of the biomarker")
    category: List[str] = Field(..., description="Type/Category of Biomarker")
    change: List[Literal[
        "Not Applicable (N/A)",
        "Increasing Trend",
        "Decreasing Trend",
        "Statistically Increased",
        "Statistically Decreased",
        "Divergent",
        "No Change"
    ]] = Field(..., description="Change in the biomarker")
    protein: str = Field(..., description="Name of protein associated with the biomarker")
    is_measured: bool = Field(..., description="Indicates if the biomarker was measured in the study i sit tested or just discussed")


class BiomarkersList(BaseModel):
    biomarkers: List[Biomarker] = Field(..., description="List of biomarkers with their respective changes")