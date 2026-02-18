# Tampere Food & Beverage Intelligence Platform

**Capstone Project — LLM Fine-Tuning Course, Tampere University**

Build a multi-agent AI system that transforms restaurant menu photos into a searchable food intelligence database for Tampere, Finland.

## The Pipeline

```
Capture → Extract → Enrich → Store → Converse
```

1. **Capture** — Photograph real menus from restaurants, cafés, bars, and food trucks across Tampere
2. **Extract** — A vision agent reads menu images and outputs structured data (dish names, prices, categories, dietary tags)
3. **Enrich** — A web search agent adds Google ratings, addresses, cuisine types, and nutrition estimates
4. **Store** — Structured data flows into a database of your choice (PostgreSQL, Neo4j, or SQLite)
5. **Converse** — A natural language bot answers questions about Tampere's food scene

## Three-Agent Architecture

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Extraction Agent** | Read menu images | Menu photo (PNG/JPG) | Structured menu items (dish, price, category, dietary tags) |
| **Enrichment Agent** | Web search for context | Restaurant name | Google rating, address, cuisine type, nutrition estimates |
| **Query Agent** | Answer natural language questions | User question | Answer based on collected data |

## Technology Stack

### Required (you MUST use)
- **Pydantic AI** — Agent framework
- **Pydantic BaseModel** — Structured output
- **Python + asyncio** — Parallel processing
- **FastAPI** — Web application backend

### Pick One from Each Category / Or find a better one, these are just suggestions

**LLM Provider:**
- OpenAI GPT (gpt-5.2 ...)
- Anthropic Claude (Opus / Haiku / Sonnet)
- Ollama (Llama, Mistral — local)
- other

**Database:**
- PostgreSQL
- Neo4j
- SQLite
- other

**Query/Retrieval Approach:**
- Any RAG flavour
- MCP (FastMCP)
- Full Context Injection
- other

## Performance & Cost Tracking

Every pipeline stage must be instrumented. You must log and compare:

1. **Token Usage** — Input & output tokens per extraction, enrichment, and query
2. **Estimated Cost** — USD cost per image processed, per enrichment call, per user query
3. **Response Time** — Latency for each pipeline stage
4. **Cross-Team Comparison** — Different LLMs, databases, and query approaches compared across all teams at demo day

## Deliverable

A **working web application** that allows users to:
- Upload images of restaurant menus
- Have the data extracted and enriched automatically
- Store the data in the chosen database
- Query the database via a web interface using natural language
- View performance metrics (tokens, cost, latency)

Presented as a **live demo** at the end of the semester.

## Getting Started

### Navigate the Lessons

Start with `lesson1_curl.md` and progress sequentially through all 14 lessons. Each lesson introduces exactly one new concept. You must understand each lesson before moving to the next — the capstone project combines all of them.

See `instructions.md` for a detailed lesson-by-lesson guide.

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd tampere-food-intelligence

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt

# Set up your API keys
cp .env.example .env
# Edit .env and add your OpenAI and Anthropic API keys
```

**Important:** This is a BYOK (Bring Your Own Key) project. You need your own API keys for OpenAI and/or Anthropic. Or the course will provide access

### Collect Your Data

Walk around Tampere and photograph menus! Focus on:
- Lunch menus ("lounaslista") — abundant and publicly displayed
- Café menus with prices visible
- Food truck menus at events
- Bar drink menus

Place your photos in the `images/` folder for lesson 10, and `images_watchfolder/` for lessons 11-12.

## Recommended Sources

1. Book: Agentic Artificial intelligence, by Pascal Bornet
    https://andor.tuni.fi/discovery/fulldisplay?docid=cdi_askewsholts_vlebooks_9789819815678&context=PC&vid=358FIN_TAMPO:VU1

2. YT: How to Build AI Agents with PydanticAI (Beginner Tutorial) -
    https://www.youtube.com/watch?v=zcYtSckecD8

3. YT: Building AI Applications the Pydantic Way -
    https://www.youtube.com/watch?v=zJm5ou6tSxk

4. YT: Simplify AI Schemas with Pydantic & OpenAI (No More Manual JSON!) -
    https://www.youtube.com/watch?v=3Z03fwH1I7s

5. YT: MCP Crash Course: What Python Developers Need to Know -
    https://www.youtube.com/watch?v=5xqFjh56AwM

6. Claude Docs
    https://platform.claude.com/docs/en/intro

7. OpenAI Reference API Docs
    https://platform.openai.com/docs/api-reference/introduction

8. Pydantic AI Docs
    https://ai.pydantic.dev/

9. FastMCP Docs
    https://gofastmcp.com/getting-started/welcome
