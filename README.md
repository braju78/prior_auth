# MRI Prior Authorization Assistant

A small agentic AI application for a fictional MRI prior-authorization workflow. It extracts clinical facts from a synthetic note, retrieves patient and rule data through MCP, applies the authorization policy deterministically, and pauses for human approval before producing the final outcome.

## Architecture

```
Patient ID + Clinical Note
          |
          v
      LangGraph
          |
          +--> MCP: get_patient()
          |
          +--> MCP: get_rule()
          |
          +--> Reader Agent (LLM)
          |       |
          |       +--> pain_weeks
          |       +--> physio_weeks
          |
          +--> Decision Agent (deterministic)
          |       |
          |       +--> Approve / Deny / Need more information
          |
          +--> interrupt()
                  |
                  v
             Human Review
                  |
             +----+----+
            yes        no
             |          |
             v          v
        Final result   Decision rejected by reviewer
```

The application does not read patient or rule data directly. Those capabilities are exposed through one local stdio MCP server.

## Design

- **Reader agent:** Uses one LLM to extract `pain_weeks` and `physio_weeks`. Each value is a number or `null`.
- **Decision agent:** Pure Python policy evaluation, in the required order. No second LLM call.
- **MCP server:** Official MCP Python SDK with `get_patient()` and `get_rule()`.
- **Human review:** LangGraph `interrupt()` pauses before the final outcome. `InMemorySaver` checkpoints the run so it can resume.
- **Testing:** `test.py` runs the three required cases with a deterministic test reader and a simulated `yes` response.
- **Web UI:** Minimal FastAPI page demonstrates the review boundary.

### Policy

1. Inactive plan -> Deny.
2. Explicit pain duration < 6 weeks OR explicit physiotherapy duration < 6 weeks -> Deny.
3. If pain or physiotherapy duration is not established -> Need more information.
4. Otherwise -> Approve.

Exactly six weeks meets the requirement. "No physiotherapy was tried" is zero weeks. Missing/undocumented physiotherapy duration is `null`.

## Setup

Python 3.11+ is required.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env` for the real LLM reader.

## Run the CLI

```bash
python -m app.cli --patient-id P001 --note data/P001.txt
```

The CLI pauses for reviewer input:

```text
Accept this recommendation? (yes/no)
```

## Run the web UI

```bash
uvicorn web.app:app --reload
```

Open `http://127.0.0.1:8000`.

## Run tests

```bash
python test.py
```

The tests do not require an LLM API key. They use a deterministic reader fixture while exercising the LangGraph workflow, MCP calls, policy evaluation, and simulated human approval.

## Repository contents

```
app/          LangGraph application
mcp_server/   Local MCP server
data/         Synthetic patients, rule, and clinical notes
web/           Minimal review UI
tests/         Unit tests
test.py       Required assignment test runner
.env.example  Environment variable template
```

All patient data is fictional and created solely for this assignment.

## AI coding assistance

AI coding assistance was used for implementation support, review, and documentation. The final repository was reviewed against the assignment requirements and the generated code was adapted accordingly.

## Assumptions

- OpenAI is used as the permitted LLM provider for the reference implementation.
- The local MCP server uses stdio because the assignment explicitly permits a local stdio server.
- The in-memory LangGraph checkpointer is sufficient for this assignment; a production deployment would use a durable checkpointer.
