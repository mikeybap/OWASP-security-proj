# Project 1 — Securing an AI Agent (Home Lab)

**Owner:** Mikey · **Started:** 2026-10-06 · **Target finish:** by end of 2026
**One-line pitch:** Build a small, fully local AI agent, test it against the published OWASP agentic/LLM risk categories in an isolated sandbox, then design and measure defenses that reduce those risks.

This is a **defensive** project. Everything runs on your own hardware against a toy agent you built. The goal is not to attack anyone — it's to show an interviewer that you understand how agent systems fail and that you can harden them, with before/after evidence.

**Repo:** GitHub `mikeybap/agent-security-proj` · local folder `~/projects/AIagent-sec` · files: `tools.py`, `agent.py`, `sandbox/`

---

## Why this project

- MCP (the protocol that lets AI agents call tools) exploded to 12,000+ public servers by early 2026, and researchers found hundreds of vulnerable ones in the wild. Securing agents is one of the fastest-growing security sub-fields and very few students have a project on it.
- It maps directly to two published standards you can cite on your resume:
  - **OWASP Top 10 for LLM Applications (2025)** — LLM01 Prompt Injection, etc.
  - **OWASP Top 10 for Agentic Applications (2026)** — ASI01 Agent Goal Hijack, ASI02 Tool Misuse, ASI03 Identity & Privilege Abuse, ASI10 Rogue Agents, etc.
- It uses your existing gear (M2 MacBook Air for the model, ThinkPad/Kali as an optional second isolated host) and ties into your Global Policy side through a short governance memo at the end.

## What "done" looks like (resume bullet)

> Built a local LLM agent with tool access and hardened it against the OWASP Agentic Top 10: implemented input/output filtering, tool allowlisting, and least-privilege scoping, reducing successful prompt-injection and tool-misuse cases from X/Y to Z/Y in a repeatable test harness. Published with full write-up and governance recommendations.

---

## Resources you'll use

| Need | Tool | Notes |
|---|---|---|
| Local model runtime | **Ollama** | runs on the M2 Air; use a tool-calling model like `llama3.2` (3GB) or `qwen2.5` |
| Agent + tools | **Python + MCP SDK** (`mcp`, `fastmcp`), `ollama` python client | you write a tiny MCP server exposing 2–3 toy tools |
| Automated adversarial testing | **garak** (NVIDIA, open source) and/or **promptfoo** | both have native Ollama support |
| Standards to map findings to | OWASP LLM Top 10 (2025), OWASP Agentic Top 10 (2026) | cite IDs in every finding |
| Version control | GitHub (`mikeybap` personal account) | README is the deliverable |
| Isolation | a dedicated project folder; keep tools read-only/scoped; no real credentials anywhere | the agent only ever touches a throwaway sandbox dir |

---

## Safety guardrails for the lab (read first)

1. **Isolation.** The agent's tools only ever act inside one throwaway directory (e.g. `./sandbox/`). No access to your real files, no network-write tools, no real API keys.
2. **Local only.** The model and MCP server run on `localhost`. Nothing is exposed to the internet.
3. **Toy targets only.** You test *your own* agent. You never point these tools at a system you don't own.
4. **Document, don't weaponize.** The write-up explains mechanisms and defenses at a conceptual level and shows metrics — it is not a how-to for attacking production systems.

---

## The build — phases and steps

### Phase 0 — Environment (≈1 evening) ✅ DONE 2026-10-06

- [x] Install Ollama on the M2 Air and pull a tool-calling model: `ollama pull llama3.2`
- [x] Create the repo locally and a Python virtual environment
- [x] Install Python deps (`mcp`, `fastmcp`, `ollama`); promptfoo via npm comes in Phase 3
- [x] Confirm the model answers / the MCP server starts
- [x] `git init`, first commit, push to GitHub (`mikeybap/agent-security-proj`)

**Deliverable:** working local model + repo with scaffold. ✅

### Phase 1 — Build the agent (≈2 evenings) — IN PROGRESS

- [x] Write the **MCP server** (`tools.py` with `fastmcp`) exposing 3 toy tools: `read_file`, `list_dir`, `fetch_text` — all confined to `./sandbox/`.
- [x] Write the **agent loop** (`agent.py`): connects to the server, converts MCP tool defs to Ollama's format, calls `ollama.chat(..., tools=...)`, runs tool calls, feeds results back, loops to a final answer.
- [ ] **Smoke test:** run `python agent.py "list the files in the sandbox and summarize notes.txt"` and confirm you see `[tool call]` lines then a `=== FINAL ANSWER ===`. That working run IS the undefended baseline.

**Notes / gotchas hit:**
- MCP SDK field is `input_schema` (snake_case) on this install, not `inputSchema`. Agent now handles both.
- Ollama response normalized to a dict so `.get()` works across client versions.

**Deliverable:** `tools.py`, `agent.py`, architecture diagram in README. The *undefended* agent.

### Phase 2 — Establish the baseline risk picture (≈2 evenings)

Run a **structured, repeatable** set of adversarial test cases against the undefended agent and record pass/fail for each. Organize cases by OWASP category so the write-up maps cleanly:

- [ ] **ASI01 / LLM01 — Goal hijack & direct prompt injection:** user-supplied instructions that try to override the agent's task.
- [ ] **Indirect injection (via `fetch_text`):** put adversarial text in a local file/page the agent fetches, and see whether the agent follows instructions embedded in fetched content rather than treating it as data.
- [ ] **ASI02 — Tool misuse:** attempts to make the agent use a tool outside its intended scope (e.g. read outside the sandbox dir via path traversal like `../`).
- [ ] **ASI03 — Privilege/scope:** check what the tools *could* reach if asked.
- [ ] Record each as a row: `case id | OWASP id | input | expected-safe behavior | actual behavior | pass/fail`.

**Deliverable:** a `baseline_results.md` table with your X/Y failure counts. This is the "before" number.

### Phase 3 — Automate the testing (≈1–2 evenings)

- [ ] Add **garak**: run it against your Ollama model to get a standardized vulnerability scan. CLI shape:
  `python -m garak --target_type ollama --target_name llama3.2 --probes <selection>`
  (use `--list_probes` to see categories; you can select probes by OWASP tag).
- [ ] Optionally add **promptfoo** (npm: `npm install -g promptfoo`) with an `ollama:chat:llama3.2` provider and a red-team config, so you have a second, repeatable harness and a nice HTML report.
- [ ] Commit the configs so the whole test suite is reproducible by anyone who clones the repo.

**Deliverable:** reproducible scan configs + saved reports.

### Phase 4 — Build the defenses (≈3–4 evenings, the core of the project)

Implement each defense, then **re-run Phases 2–3** to measure the improvement:

- [ ] **Tool allowlisting + least privilege:** the agent may only call an explicit allowlist of tools; each tool enforces its own scope.
- [ ] **Path confinement:** `read_file`/`list_dir` resolve the real path and reject anything outside the sandbox dir (kills the `../` traversal).
- [ ] **Input handling:** treat fetched/tool content as *data, not instructions* — e.g. clearly delimit untrusted content in the prompt and add a system instruction that external content is never a command source.
- [ ] **Output filtering:** scan tool results and model output for obvious injection markers / sensitive patterns before acting on them.
- [ ] **Authentication on the MCP server:** require a key so an arbitrary local process can't drive your tools (mirrors the #1 real-world MCP problem: unauthenticated servers).
- [ ] **Human-in-the-loop gate (ASI09):** any "write"-style action pauses for confirmation.

**Deliverable:** hardened `tools.py`/`agent.py` + `hardened_results.md` showing Z/Y failures. The before→after delta is your headline metric.

### Phase 5 — Write-up & governance memo (≈2 evenings)

- [ ] Polish the **README**: problem, architecture diagram, threat model, baseline results, each defense with the OWASP id it addresses, before/after metrics table, how to reproduce.
- [ ] Write a **2-page policy/governance memo**: "What an organization should require before deploying tool-using AI agents" — authentication, least privilege, logging, human gates, supply-chain review of MCP tools. This is where your Global Policy + Security & Intelligence Club angle shows and sets you apart from pure-technical applicants.
- [ ] Final commit; make the repo public; add it to your resume and LinkedIn.

**Deliverable:** public GitHub repo + governance memo (also saved to this project).

---

## Rough schedule (fits around classes)

| Window | Phase |
|---|---|
| Oct, week 1–2 | Phase 0 + Phase 1 (environment + agent) |
| Oct, week 3–4 | Phase 2 (baseline) |
| Nov, week 1 | Phase 3 (automate) |
| Nov, weeks 2–3 | Phase 4 (defenses — the big one) |
| Nov wk 4 / Dec | Phase 5 (write-up + memo), buffer for finals |

## Progress log

- 2026-10-06 — Plan created.
- 2026-10-06 — Phase 0 done: Ollama + llama3.2 installed, venv + deps, scaffold built (`tools.py`, `agent.py`, `sandbox/`), pushed to GitHub `mikeybap/agent-security-proj`. Fixed `input_schema` vs `inputSchema` and Ollama response-dict issues along the way. Next: Phase 1 smoke test, then Phase 2 baseline table.
