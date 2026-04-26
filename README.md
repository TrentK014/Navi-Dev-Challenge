# Click This Link

https://navi-dev-challenge.vercel.app/

# Tech Stack

Python, FastAPI, Claude API, SQLite, TypeScript, Next.js, Tailwind CSS

Deployed using Vercel and Railway

# Navi Manufacturing Operations Chatbot

A chatbot that answers natural-language questions about a Turkish textile manufacturer's production dataset — machines, products, BOM variants, route steps, and operation parameters. The user types a question; the backend translates it into SQL, executes it against a local SQLite database, and returns a structured answer with a full audit trail of every query run.

## Live URLs

| Service  | URL |
|----------|-----|
| Frontend | https://navi-dev-challenge.vercel.app/ |
| Backend  | _Railway URL (add after deploy)_ |

## Local development

**Prerequisites:** Python 3.11+, Node.js 20+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Build the database (one-time)
python scripts/build_db.py        # prints row counts and writes data/seed.db

# Set environment variables
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY

# Run
uvicorn main:app --reload
# API available at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# .env.local already points to http://localhost:8000

npm run dev
# UI available at http://localhost:3000
```

## Architecture

### Why SQLite instead of Postgres or Supabase

The dataset is static and read-only: 17 machines, 50 products, 626 BOM variants, 3 929 route steps, 77 469 parameters. SQLite runs in-process with zero network overhead, requires no separate service to manage, and ships as a single committed file (`backend/data/seed.db`). Railway clones the repo and the database is immediately available — no migrations, no connection pooling, no cold-start latency. For a read-only static dataset of this size, SQLite is not a compromise; it is the correct tool.

### Why a single `run_sql` tool instead of curated query functions

The assignment explicitly asks about questions "and others we might think of." A curated set of functions (e.g., `get_products_for_machine`, `get_parameters_for_bom`) would answer the questions you anticipated and fail on the ones you didn't. A single `run_sql` tool gives the model full expressivity over a small, well-typed, five-table schema. The schema is compact enough to fit entirely in the system prompt, so the model always knows what is joinable to what. Any question that can be answered by SQL — aggregations, comparisons, pattern matches, counts — is answerable without adding a new function.

### Why correctness is enforced by deterministic SQL execution, not LLM judgment

The model never sees the raw 77 469 parameter rows. It sees only the results of the queries it writes. If it writes a correct query, it gets correct numbers. If it writes a wrong query, the database returns an error or empty rows, and the model retries. Hallucinated figures are structurally impossible: the model cannot invent a cycle time it never retrieved. This is the core correctness guarantee of the design.

### Why `routes` and `route_steps` are separate tables

The source JSON nests steps inside routes. Keeping that nesting would require JSON path queries or application-level unpacking on every request. Flattening into two tables — `routes` (one row per BOM variant, keyed by `bom_code`) and `route_steps` (one row per step, keyed by `(bom_code, sequence)`) — gives the model clean, indexable joins. Every parameter and every step is reachable with a single JOIN on `bom_code`.

### What we learned from inspecting the data (and adapted to)

The spec described a dataset where `version` distinguishes BOM variants per product (version 1, version 2, …). Inspection revealed that all 626 routes have `version = 1`. Products with multiple routes are distinguished by their `bom_code` suffix (e.g., `BOM-607C11020S9K.3-001` vs `BOM-607C11020S9K.3-022`). The system prompt was updated to reflect this: it teaches the model to use `bom_code` as the variant identifier, treat any user mention of "version 2" as a loose reference to a suffix, and list available `bom_codes` rather than version numbers when disambiguation is needed. The database schema was kept as specified (the `version` column still exists) because it is accurate — it just carries no meaningful differentiation in this dataset.

### How edge cases are handled

| Case | Mechanism |
|------|-----------|
| Unknown entity | Model queries the DB; zero rows → explicitly says entity not found, lists what exists |
| Ambiguous BOM variant | Model counts bom_codes for the product; if >5, shows count + examples and asks user to specify |
| Nonexistent product group | System prompt explicitly states only "Mamul" exists; model cites this when asked about "automotive" etc. |
| Prompt injection / off-topic | System prompt OUT-OF-SCOPE rule; model declines without calling run_sql |
| Empty or oversized input | Backend returns HTTP 400 before the model is invoked; frontend also validates client-side |
| Bad SQL from the model | `execute_run_sql` returns `{"error": "..."}` as a tool result; model sees it, corrects, retries |
| Iteration cap | After 8 tool-use loops, backend returns a friendly fallback message |
| Duplicate parameter keys | System prompt rule: prefer Turkish display names, mention snake_case alias only if asked |

### The SQL footer

Every assistant message ends with a collapsible "Show N queries" section that displays the exact SQL executed. This makes every answer independently auditable — users can copy the query, run it directly against the SQLite file, and verify the result themselves.

## Limitations

- Query results are capped at 200 rows. For products with many BOM variants or large parameter sets, the model may need to summarize rather than list everything.
- The tool-use loop is capped at 8 iterations. Complex multi-step questions that require more back-and-forth will receive a "try rephrasing" fallback.
- No streaming — responses appear all at once after the full tool-use loop completes.
- No message persistence — conversation state lives in the browser; a page refresh starts a new session.
- Input is capped at 4 000 characters on both the client and server.

## Tradeoffs considered and rejected

| Option | Why rejected |
|--------|--------------|
| Pure RAG over the JSON | Aggregation queries (average cycle time, machine utilization counts) require computation over many rows — retrieval alone cannot answer them correctly |
| Curated tool functions per query type | Limits the answerable question space to what was anticipated at build time; contradicts the "and others we might think of" requirement |
| Vercel serverless Python backend | The tool-use loop can take 8 sequential API calls; Vercel's 10-second serverless timeout would cut off complex queries mid-loop |
| Separate version column for BOM differentiation | The actual data has all routes at version 1; differentiation is by bom_code suffix, so the system prompt was adapted to match reality rather than the spec description |
