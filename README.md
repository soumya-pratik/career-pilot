# Career Pilot

Hybrid multi-agent MVP that suggests job roles from your resume and projects, finds matching postings, and posts a digest to Discord.

## Agents

| Agent | Role |
|-------|------|
| **Job Scout** | Reads `data/resume.md` + `data/projects.md`, suggests roles via LLM, searches jobs via JSearch |
| **Master** | Orchestrates Scout, saves `output/latest_run.json`, posts Discord webhook digest |

Job Scout is behind a backend switch (`SCOUT_BACKEND=local` today; `cursor` reserved for a future Cursor SDK integration).

## Setup

```bash
cd career-pilot
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -e .
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env` with:

1. **`OPENAI_API_KEY`** — OpenAI (or compatible) API key  
2. **`JSEARCH_API_KEY`** — RapidAPI key for [JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)  
3. **`DISCORD_WEBHOOK_URL`** — Discord channel webhook  

### Discord webhook

1. Open your Discord server → channel settings → **Integrations** → **Webhooks**  
2. Create a webhook, copy the URL into `.env`

### Resume / projects

Replace the sample content in:

- [`data/resume.md`](data/resume.md)
- [`data/projects.md`](data/projects.md)

## Usage

Full pipeline (Scout → save JSON → Discord):

```bash
python -m career_pilot run
# or: career-pilot run
```

Scout only (print JSON, skip Discord, still writes `output/latest_run.json`):

```bash
python -m career_pilot scout-only
```

Useful flags:

```bash
python -m career_pilot run --no-discord
python -m career_pilot run --no-persist
```

## Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model |
| `OPENAI_BASE_URL` | (OpenAI) | Optional compatible base URL |
| `SCOUT_BACKEND` | `local` | `local` or `cursor` (not implemented) |
| `JOB_LOCATION` | `Remote` | Location hint for searches |
| `MAX_ROLES` | `5` | Max suggested roles |
| `JOBS_PER_ROLE` | `3` | Jobs fetched per role query |
| `MAX_JOBS` | `10` | Cap after URL dedupe |

## Project layout

```
src/career_pilot/
  agents/
    master.py           # orchestrator + Discord
    job_scout.py        # facade
    backends/
      local.py          # LLM + JSearch (MVP)
      cursor.py         # stub for later
  tools/
    job_search.py
    discord_notify.py
  prompts/
    job_scout.py
  cli.py
  schemas.py            # ScoutResult contract
data/
  resume.md
  projects.md
```

## Extending later

- Set `SCOUT_BACKEND=cursor` after implementing `agents/backends/cursor.py` with the Cursor SDK  
- Add a Discord bot that calls `master.run()`  
- Schedule with cron / Task Scheduler / GitHub Actions  
- Persist seen job URLs under `output/` to avoid repeat digests  

## Notes

- If JSearch fails or the key is missing, Master still posts role suggestions and includes an error note.  
- Discord messages longer than ~1900 characters are split automatically.
