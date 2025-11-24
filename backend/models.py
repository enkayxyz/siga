from pydantic import BaseModel
from typing import List, Optional

class Location(BaseModel):
    city: Optional[str] = None
    country: str
    address: Optional[str] = None
    coordinates: Optional[List[float]] = None  # [lat, lng]

class Financials(BaseModel):
    revenue: Optional[str] = None
    currency: Optional[str] = None
    fiscal_year: Optional[str] = None
    employees: Optional[int] = None

class Subsidiary(BaseModel):
    name: str
    type: Optional[str] = "Subsidiary"  # Branch, Subsidiary, HQ
    location: Optional[Location] = None
    financials: Optional[Financials] = None
    parent_company: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = "Unknown"

class ResearchUsage(BaseModel):
    tavily_calls: int = 0
    llm_tokens: int = 0
    estimated_cost: float = 0.0

class Company(BaseModel):
    name: str
    hq_location: Optional[Location] = None
    subsidiaries: List[Subsidiary] = []
    total_revenue: Optional[str] = None
    usage: Optional[ResearchUsage] = None
