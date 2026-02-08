"""
main.py

Bike Weight Finder — teaching-friendly multi-step AI workflow.

This script orchestrates a 4-stage pipeline:
1) Broad web search (collect candidate pages)
2) URL selection (pick the most relevant sources)
3) Scraping strategy analysis (robots/meta checks + basic page analysis)
4) Extraction (crawl pages and extract the bicycle weight with evidence)

Run:
    python main.py
"""

from __future__ import annotations

import os
import asyncio
import random
import time
from dotenv import load_dotenv

from agno.tools import Toolkit
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.workflow import Workflow, Step
from agno.team import Team
from agno.tools.websearch import WebSearchTools

from tools import CrawlTools

from prompts import (
    BICYCLE_WEIGHT_SEARCH_SYSTEM_MESSAGE,
    BICYCLE_WEIGHT_SELECTOR_SYSTEM_MESSAGE,
    BICYCLE_WEIGHT_STRATEGY_SYSTEM_MESSAGE,
    BICYCLE_WEIGHT_SCRAPER_SYSTEM_MESSAGE,
    BICYCLE_WEIGHT_TEAM_SYSTEM_MESSAGE,
)
from schemas import (
    RawSearchOutput,
    BikeWeightSearchOutput,
    BikeWeightStrategyOutput,
    BikeWeightReportOutput
)

# Load environment variables
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set.")

# Constants
INTELLIGENT_MODEL_ID = os.getenv("INTELLIGENT_MODEL_ID", "gpt-5.1")
CORE_MODEL_ID = os.getenv("CORE_MODEL_ID", "gpt-5-mini")
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "high")

search_model = OpenAIResponses(id=CORE_MODEL_ID, reasoning_effort=REASONING_EFFORT)
filter_search_model = OpenAIResponses(id=INTELLIGENT_MODEL_ID, reasoning_effort=REASONING_EFFORT)
core_model = OpenAIResponses(id=CORE_MODEL_ID, reasoning_effort=REASONING_EFFORT)
team_model = OpenAIResponses(id=INTELLIGENT_MODEL_ID, reasoning_effort=REASONING_EFFORT)

SEARCH_TOOL_CALL_LIMIT = 5
STRATEGY_TOOL_CALL_LIMIT = 10
SCRAPER_TOOL_CALL_LIMIT = 10

DEBUG_MODE = True

# Initialize Tools
crawl4ai_toolkit = CrawlTools()

# ------------------------------------------------------------------------
# STEP 1: Broad Search Agent
# ------------------------------------------------------------------------
bicycle_weight_search_agent = Agent(
    model=search_model,
    tools=[WebSearchTools(enable_news=False)],
    tool_call_limit=SEARCH_TOOL_CALL_LIMIT,
    system_message=BICYCLE_WEIGHT_SEARCH_SYSTEM_MESSAGE,
    output_schema=RawSearchOutput,
    debug_mode=DEBUG_MODE
)

# ------------------------------------------------------------------------
# STEP 2: Selector & Filter Agent
# ------------------------------------------------------------------------
bicycle_weight_selector_agent = Agent(
    model=filter_search_model,
    system_message=BICYCLE_WEIGHT_SELECTOR_SYSTEM_MESSAGE,
    output_schema=BikeWeightSearchOutput,
    debug_mode=DEBUG_MODE
)

# ------------------------------------------------------------------------
# STEP 3: Scraping Strategy Analyst
# ------------------------------------------------------------------------
bicycle_weight_scraping_analyst_agent = Agent(
    model=core_model,
    tools=[crawl4ai_toolkit],
    tool_call_limit=STRATEGY_TOOL_CALL_LIMIT,
    system_message=BICYCLE_WEIGHT_STRATEGY_SYSTEM_MESSAGE,
    output_schema=BikeWeightStrategyOutput,
    debug_mode=DEBUG_MODE
)

# ------------------------------------------------------------------------
# STEP 4: Scraper Team
# ------------------------------------------------------------------------
bicycle_weight_scraper = Agent(
    model=core_model,
    tools=[crawl4ai_toolkit],
    tool_call_limit=SCRAPER_TOOL_CALL_LIMIT,
    system_message=BICYCLE_WEIGHT_SCRAPER_SYSTEM_MESSAGE,
    debug_mode=DEBUG_MODE
)

bicycle_weight_scraper_team = Team(
    model=team_model,
    members=[bicycle_weight_scraper],
    get_member_information_tool=True,
    system_message=BICYCLE_WEIGHT_TEAM_SYSTEM_MESSAGE,
    markdown=True,
    show_members_responses=True,
    output_schema=BikeWeightReportOutput,
    debug_mode=DEBUG_MODE
)

# ------------------------------------------------------------------------
# WORKFLOW DEFINITION
# ------------------------------------------------------------------------
bike_weight_workflow = Workflow(
    name="Bike Weight Finder",
    steps=[
        Step(
            name="Broad Web Search",
            agent=bicycle_weight_search_agent
        ),
        Step(
            name="URL Filtering & Selection",
            agent=bicycle_weight_selector_agent
        ),
        Step(
            name="Web Scraping Strategy Analysis",
            agent=bicycle_weight_scraping_analyst_agent
        ),
        Step(
            name="Bike Weight Extraction Team",
            team=bicycle_weight_scraper_team
        ),
    ],
    debug_mode=DEBUG_MODE
)

if __name__ == "__main__":
    input_prompt = """
Find the weight of the bike:
  - Brand: Megamo
  - Model: Track 00
  - Year: 2026
"""
    try:
        asyncio.run(
            bike_weight_workflow.aprint_response(
                input_prompt,
                markdown=True,
            )
        )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
