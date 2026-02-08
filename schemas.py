"""
schemas.py

Pydantic models that define the structured outputs of each pipeline stage.

These schemas are the "contract" between:
- prompts.py (what the model is told to output)
- main.py (what the workflow validates and passes between steps)
"""

from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------
# Shared configuration (must match prompts.py)
# ---------------------------------------------------------------------
CANDIDATE_COUNT = 15
SELECTED_URL_COUNT = 5

ConfidenceLevel = Literal["High", "Medium", "Low"]


# ---------------------------------------------------------------------
# Step 1 — Raw Search Output (broad collection)
# ---------------------------------------------------------------------
class RawSearchCandidate(BaseModel):
    """One search candidate returned by the web search stage."""

    url: str = Field(..., description="The URL of the search result.")
    title: str = Field(..., description="The page title.")
    snippet: str = Field(..., description="A short snippet returned by the search engine.")
    source_type: Literal["Official", "Media", "Retailer", "Unknown"] = Field(
        ...,
        description="Preliminary classification of the source.",
    )


class RawSearchOutput(BaseModel):
    """Output contract for the broad search stage."""

    candidates: List[RawSearchCandidate] = Field(
        ...,
        min_items=CANDIDATE_COUNT,
        max_items=CANDIDATE_COUNT,
        description=f"Exactly {CANDIDATE_COUNT} candidate pages to be filtered later.",
    )


# ---------------------------------------------------------------------
# Step 2 — Filtered URL Selection Output
# ---------------------------------------------------------------------
class BikeWeightSearchOutput(BaseModel):
    """Output contract for the URL selection stage."""

    urls: List[str] = Field(
        ...,
        min_items=SELECTED_URL_COUNT,
        max_items=SELECTED_URL_COUNT,
        description=f"Exactly {SELECTED_URL_COUNT} high-relevance URLs selected from the candidates.",
    )


# ---------------------------------------------------------------------
# Step 3 — Strategy & Analysis Output (per-URL report)
# ---------------------------------------------------------------------
class UrlAnalysis(BaseModel):
    """Scraping feasibility and page characteristics for a single URL."""

    url: str = Field(..., description="The analyzed URL.")
    tech_stack: str = Field(..., description="Detected stack, e.g., WordPress, Shopify, React.")
    robots_status: str = Field(..., description="Summary of robots.txt and meta restrictions.")
    scraping_allowed: bool = Field(..., description="Whether crawling this URL is allowed by policy.")


class BikeWeightStrategyOutput(BaseModel):
    """Output contract for the scraping strategy stage."""

    analysis_report: List[UrlAnalysis] = Field(
        ...,
        min_items=SELECTED_URL_COUNT,
        max_items=SELECTED_URL_COUNT,
        description=f"Exactly {SELECTED_URL_COUNT} analyses (one per selected URL).",
    )


# ---------------------------------------------------------------------
# Step 4 — Per-URL extraction output (member agent output)
# ---------------------------------------------------------------------
class ScraperRow(BaseModel):
    """Extraction result for one URL."""

    url: str = Field(..., description="The URL that was crawled.")
    weight_value: str = Field(..., description="Exact weight text (e.g., '7.8 kg') or 'NOT FOUND'.")
    evidence_snippet: str = Field(..., description="Context snippet (max 160 chars) showing the weight.")
    status: Literal["OK", "NOT FOUND", "BLOCKED (robots/meta)"] = Field(
        ..., description="Result status for this URL."
    )
    notes: Optional[str] = Field(
        None,
        description="Extra context (e.g., size mismatch, ambiguous spec, policy uncertainty).",
    )


class BikeWeightScraperOutput(BaseModel):
    """Output contract for the scraper agent (one row per selected URL)."""

    extraction_results: List[ScraperRow] = Field(
        ...,
        min_items=SELECTED_URL_COUNT,
        max_items=SELECTED_URL_COUNT,
        description=f"Exactly {SELECTED_URL_COUNT} extraction rows (one per URL).",
    )


# ---------------------------------------------------------------------
# Final consolidated report (team output)
# ---------------------------------------------------------------------
class UrlExtractionDetail(BaseModel):
    """Summary detail for a URL in the final report."""

    url: str = Field(..., description="The URL that was evaluated.")
    data_found: bool = Field(..., description="Whether a weight value was successfully found.")
    observations: str = Field(..., description="Short explanation of what was found or why it failed.")


class BikeWeightReportOutput(BaseModel):
    """Final report contract produced by the Team coordinator."""

    brand: str = Field(..., description="Bicycle brand.")
    model: str = Field(..., description="Bicycle model.")
    year: str = Field(..., description="Model year.")
    final_weight: str = Field(..., description="Best weight value found or 'Not Found'.")
    confidence: ConfidenceLevel = Field(..., description="Confidence in the final_weight field.")
    url_details: List[UrlExtractionDetail] = Field(
        ...,
        min_items=SELECTED_URL_COUNT,
        max_items=SELECTED_URL_COUNT,
        description=f"Exactly {SELECTED_URL_COUNT} per-URL details.",
    )
