# Bike Weight Finder (Educational AI Agents Workflow DEMO)

> **Disclaimer / Intent**
>
> This repository is **purely educational**. It’s part of a set of didactic posts on LinkedIn where I show curious people what can be built with AI + Agent workflows.
>
> **Do not use this as-is in production**: it’s intentionally “overkill” (and intentionally imperfect in places) to surface key concepts (workflows, tools, prompting, agents vs. teams, structured outputs, etc.). You *can* reuse ideas and patterns for professional implementations—with proper engineering, security, observability, and governance.

---
## LinkedIn post
[Read the LinkedIn post]([https://www.linkedin.com/posts/fran-pastor_ia-agentesia-aiengineering-activity-7426391511992471552-BBnL?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAnUPkMB_txnu02jaeaCvz3Bn7aAlTfzUWk)
---

## What this project does

The “find the bike weight” goal is just an excuse to walk through a **multi-step agent pipeline** that:

1. Performs a broad web search (collect candidates)
2. Filters/selects the most promising URLs
3. Analyzes scraping feasibility/strategy (policy + page characteristics)
4. Crawls and extracts the bicycle weight with supporting evidence

The orchestration happens in `main.py`.

---

## What it demonstrates (by design)

- **Workflow orchestration** with multiple steps (Agno Workflow + Step abstractions)
- **Prompting per stage** using dedicated system messages per agent/role
- **Custom tools** (Crawl4AI wrapper + jitter/rate-limit helper)
- **Single agent vs. team orchestration** (a coordinator “Team” managing a scraper agent)
- **Structured outputs** enforced via Pydantic schemas for each stage and the final report

---

## How it works (pipeline overview)

### Step 1 — Broad Web Search
- Agent gathers a fixed number of candidates (schema-enforced).
- Output: a “raw search” object containing the candidates.

### Step 2 — URL Filtering & Selection
- Agent selects the top URLs most likely to contain the weight for the requested brand/model/year.
- Output: a “selected URLs” object.

### Step 3 — Web Scraping Strategy Analysis
- Agent inspects each URL and proposes a scraping strategy (including basic policy awareness like `robots.txt`).
- Output: per-URL strategy analysis.

### Step 4 — Bike Weight Extraction Team
- A team coordinator delegates extraction to a scraper agent, enforcing constraints and requiring evidence.
- Output: a final report containing the selected weight (or “Not Found”) + confidence + per-URL details.

---

## Requirements

- Python (recommended: **3.10+**)
- An OpenAI API key (set as `OPENAI_API_KEY`)
- Crawl4AI installed and initialized (see below)

---

## Installation

Create and activate a virtual environment, then install dependencies.

```bash
pip install -r requirements.txt
```

---

## Crawl4AI setup

Run:

```bash
crawl4ai-setup
crawl4ai-doctor
```

This ensures the crawler environment is ready.

---

## Configuration (.env)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key_here

# Optional model configuration (defaults shown)
INTELLIGENT_MODEL_ID=gpt-5.1
CORE_MODEL_ID=gpt-5-mini
REASONING_EFFORT=high
```

---

## Run

```bash
python main.py
```

By default, the script runs a sample prompt targeting a specific bike. To try another bike, edit the `input_prompt` inside `main.py`.

---

## Project structure

- `main.py` — Orchestrates the full workflow: agents, team, steps, and execution
- `prompts.py` — System messages (prompt templates) for each stage
- `schemas.py` — Pydantic models enforcing structured outputs between steps
- `tools.py` — Custom Crawl4AI toolkit (`crawl`, `random_sleep`)

---

## Output format (what you get at the end)

The final result is a structured report containing:

- `brand`, `model`, `year`
- `final_weight` (or `"Not Found"`)
- `confidence`: `High | Medium | Low`
- `url_details`: per-source observations (including evidence snippets when available)

---

## Important notes / known quirks (intentional “learning edges”)

This repo is intentionally didactic, so there can be small mismatches between prompt wording and strict schema constraints.

If you want to polish this into a cleaner example, aligning prompt text with schema constraints is a good first exercise.

---

## Ethical & practical guidance

- Respect robots/meta restrictions and don’t attempt to bypass access controls (CAPTCHAs, paywalls, logins).
- Treat web content as **untrusted** (prompt-injection defense is part of the prompting).
- If you adapt this for real projects, add:
  - logging/telemetry, retries/backoff, caching, robust HTML parsing,
  - test coverage + regression fixtures,
  - explicit allowlists / compliance checks,
  - and safer secret management.

