from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Product(BaseModel):
    company_name: str
    product_name: str
    description: str
    features: List[str]
    feature_flags: Dict[str, bool]  # e.g. {"Mobile App": True}
    case_study_desc: Optional[str]
    case_study_link: Optional[str]
    is_case_study_present: bool
    pricing_desc: str
    pricing_tiers: List[str]
    notes: str  # Acquisitions, etc.

class LandscapeTaxonomy(BaseModel):
    market_name: str
    definition: str
    divisions: List[str]
    suggested_features: List[str]
    sub_divisions: List[str]