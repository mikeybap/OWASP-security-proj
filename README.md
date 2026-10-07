# Securing an AI Agent — Home Lab

A defensive security project: build a small **local** LLM agent with tool access, test it
against the published OWASP risk categories for LLM and agentic applications, then design and
**measure** defenses that reduce those risks.

Everything runs locally against a toy agent I built. The point is to show how tool-using AI
agents fail and how to harden them, with before/after evidence.

## Standards this maps to
- **OWASP Top 10 for LLM Applications (2025)** — e.g. LLM01 Prompt Injection
- **OWASP Top 10 for Agentic Applications (2026)** — e.g. ASI01 Agent Goal Hijack,
  ASI02 Tool Misuse, ASI03 Identity & Privilege Abuse, ASI10 Rogue Agents

## Architecture (baseline)
```
  user query ──► agent.py ──► Ollama (local LLM, tool-calling)
                    │               │ decides which tool to call
                    ▼               ▼
              MCP session ──► server.py  ──► tools act only inside ./sandbox/
```

## Components
- `server.py` — MCP server exposing toy tools (`list_dir`, `read_file`, `fetch_text`), confined to `./sandbox/`.
- `agent.py` — agent loop: converts MCP tools to Ollama format and runs tool-calling.
- `sandbox/` — the only directory the tools ever touch. Throwaway content only.

## Setup
```bash
# 1. Install Ollama (https://ollama.com) and pull a tool-calling model
ollama pull llama3.2

# 2. Python env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the agent (it launches the MCP server itself)
python agent.py "list the files in the sandbox and summarize notes.txt"
```

## Project phases
See the full plan in my Cybersecurity project. Short version:
0. Environment  1. Build the agent (baseline)  2. Baseline risk testing (map to OWASP)
3. Automate testing (garak / promptfoo)  4. Build & measure defenses  5. Write-up + governance memo

## Safety
Local only. Toy agent I own. Tools are scoped to a throwaway sandbox. No real credentials.
This repo documents mechanisms and defenses with metrics — it is not a tool for attacking real systems.

## Status
🚧 Phase 0–1 — scaffolding in place.
