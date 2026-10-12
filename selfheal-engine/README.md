# Self-Healing E2E Test System (SelfHeal)

SelfHeal is a deterministic, intent-aware self-healing end-to-end testing engine:
- **Test Intent is IMMUTABLE**: Complete checkout with a valid credit card (canonical content hash verified on every run).
- **Steps are a Versioned Recipe**: Steps contain structural targets and logical `field_key` names, never hardcoded test data or literal credentials.
- **Deep Agent Autonomous Healer**: Rebuilds multi-step workflows when UI redesigns break locators, without human intervention.
- **Deterministic Verifier**: Decides pass or fail strictly in a clean browser replay from business invariants and page state, never via LLM claims.
- **Triage Gate**: Distinguishes structural UI redesigns from genuine application defects (HTTP 500, calculation errors) and strictly refuses to heal real bugs.

---

## Architecture

```
                 +---------------------------+
                 |  Immutable Intent (JSON)  |
                 | (Hash-Checked on Load)    |
                 +-------------+-------------+
                               |
                               v
                     +-------------------+
                     | Recipe v1 (JSON)  |
                     +---------+---------+
                               |
                               v
               +-------------------------------+
               | Initial Execution in Browser  |
               +---------------+---------------+
                               |
                +--------------+--------------+
                |                             |
         Passes Verifier                Step Fails /
                |                       Invariant Fails
                v                             |
        [PASS_NO_HEAL]                        v
         (Zero AI Calls)        +-------------------------------+
                                |  Failure Context & Triage     |
                                +---------------+---------------+
                                                |
                               +----------------+----------------+
                               |                                 |
                        Application Bug                      UI Drift
                     (HTTP 500 / Total Mismatch)                 |
                               |                                 v
                               v                   +---------------------------+
                       [FAIL_FUNCTIONAL]           | Deep Agent Healer         |
                    (Refuses False Healing)        | (Live Gemini or Recorded) |
                                                   +-------------+-------------+
                                                                 |
                                                                 v
                                                   +---------------------------+
                                                   | Validator & Tool Action   |
                                                   +-------------+-------------+
                                                                 |
                                                                 v
                                                   +---------------------------+
                                                   | Clean Replay Verification |
                                                   +-------------+-------------+
                                                                 |
                                                +----------------+----------------+
                                                |                                 |
                                             Passed                             Failed
                                                |                                 |
                                                v                                 v
                                       [PASS_AFTER_HEAL]                   [FAIL_HEALING]
                                    (Save Recipe v2 / v3)
                                                |
                                                v
                               +---------------------------------+
                               | Self-Contained Report Bundle    |
                               | runs/<run_id>/ (HTML, JSON, MD) |
                               +---------------------------------+
```

---

## Setup (Windows PowerShell)

Run the following commands in PowerShell from the project root:

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Install Chromium browser for Playwright
playwright install chromium

# 4. Configure environment
copy .env.example .env
```

Edit `.env` to supply your Google Gemini API key:
```env
DEEPAGENT_MODEL=google_genai:gemini-2.5-flash
GOOGLE_API_KEY=your_actual_api_key_here
DEMO_BASE_URL=http://127.0.0.1:5000
APP_ENV=local
```

---

## Running the Demo Shop & Web Dashboard

### Start Demo Shop (Port 5000)
```powershell
python cli.py serve
```

### Start Web Dashboard (Port 8080)
```powershell
python cli.py serve --dashboard
```

---

## CLI Commands & 5-Beat Demonstration

The CLI supports all five demonstration beats with exit codes (`0` for PASS, `1` for FAIL, `2` for BLOCKED, `3` for NEEDS_REVIEW):

```powershell
# 0. Establish or verify Version A baseline inventory
python cli.py baseline

# Beat 1: Version A (Baseline single-page checkout -> PASS_NO_HEAL)
python cli.py run --version a

# Beat 2: Version B (Multi-step UI redesign drift -> PASS_AFTER_HEAL)
python cli.py run --version b

# Beat 3: Version B Re-run (Executes newly saved Recipe v2 -> PASS_NO_HEAL, zero LLM calls)
python cli.py run --version b --recipe-version 2

# Beat 4: Version C (Server HTTP 500 error on checkout -> FAIL_FUNCTIONAL)
python cli.py run --version c

# Beat 5: Version D (Calculation mismatch $32.50 vs $36.50 -> FAIL_FUNCTIONAL)
python cli.py run --version d
```

### Automated 5-Beat Demo
Run all five beats sequentially with formatted status headlines and pauses:
```powershell
python cli.py demo
```

Or run the end-to-end background supervisor script:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/demo.ps1
```

### Safe Reset
Safely removes generated recipe versions above `v1` and clears `runs/` without deleting protected files:
```powershell
python cli.py reset
```
*Note: `cli.py reset` strictly refuses to modify or delete the immutable intent (`intents/checkout_intent.json`), the baseline inventory (`baselines/version_a_inventory.json`), or the initial recipe (`recipes/checkout/v1.json`).*

---

## LIVE vs RECORDED Healing Modes

SelfHeal supports two healing execution modes:

1. **LIVE Mode (`--mode live`)**:
   - Uses Google Gemini (`gemini-2.5-flash`) via the LangChain Deep Agents architecture.
   - Observes live interactive controls, calls subagents for failure analysis, validates every proposed action against accessibility rules, and generates candidate steps.
   - Prominently labeled with a green `LIVE` badge and real LLM call counts in reports.

2. **RECORDED Mode (`--mode recorded`)**:
   - Replays a genuine, pre-captured agent trace (`recorded/b_heal_trace.json`) recorded from a live healing run.
   - **Crucial Rule**: The recorded trace is NOT a fake bypass. Every action is dispatched through the **EXACT SAME** validator, executor, and fresh browser context clean-replay verifier as live AI.
   - If the recorded trace fails validation or does not satisfy business invariants, it fails honestly.
   - Prominently labeled with a blue `RECORDED` badge and `Recorded Deterministic Trace` provider in reports. Never labeled as live AI.

To record a genuine agent trace from a live run:
```powershell
python cli.py record
```

---

## Reporting Artifacts

Every run automatically generates a self-contained, standalone audit bundle in `runs/<run_id>/`:

| Artifact | Purpose |
|---|---|
| `report.html` | Standalone interactive HTML report with inline responsive CSS, prominent status badge, timeline, diagnosis grid (What Broke vs What Changed), untrusted model explanation box, verification checks table, and side-by-side recipe diff. |
| `report.json` | Validated Pydantic model (`RunReport`) containing full metadata, events, and metrics. |
| `report.md` | Clean Markdown summary report. |
| `snapshot_current.json` | Final captured DOM accessibility inventory. |
| `diff.json` | Structural UI diff comparing baseline to current version. |
| `agent_trace.json` | Chronological tool call trace executed during healing. |
| `screenshots/` | Captured screenshots of key steps and final states. |

The most recent run is mirrored into `runs/latest/` for instant inspection:
```powershell
start runs/latest/report.html
```

### Privacy & Secret Redaction Guarantee
- The reporting engine actively redacts API keys, bearer tokens, headers, cookies, and environment variables.
- Credit card numbers are masked to show at most the last 4 digits (`•••• •••• •••• 4242`). Full 16-digit card numbers are strictly prevented from appearing in any report, artifact, or log.

---

## 90-Second Demo Walkthrough Script

1. **[00:00 - 00:15] Introduction**:
   "Traditional E2E test suites break whenever developers redesign a form or split one page into multiple steps. SelfHeal solves this by treating test intent as immutable and test steps as disposable, auto-healable recipes."
2. **[00:15 - 00:30] Beat 1 (Baseline Pass)**:
   Run `python cli.py run --version a`.
   "Version A runs our checkout intent against the single-page checkout. Recipe v1 executes in under 4 seconds and passes deterministic verification with zero AI calls."
3. **[00:30 - 00:55] Beat 2 (Autonomous UI Redesign Healing)**:
   Run `python cli.py run --version b`.
   "The developers redesigned checkout into a 3-step wizard with different field locators. Recipe v1 fails on Step 1. Triage detects UI drift, engages our Deep Agent, explores the wizard, discovers the new flow, verifies the new recipe on a clean replay, and saves Recipe v2."
4. **[00:55 - 01:10] Beat 3 (Zero AI Cost Re-Run)**:
   Run `python cli.py run --version b --recipe-version 2`.
   "Running Version B again uses the healed Recipe v2. It completes all steps in ~3.5 seconds with zero LLM API calls and zero latency overhead."
5. **[01:10 - 01:25] Beat 4 & 5 (Application Defect Detection)**:
   Run `python cli.py run --version c` and `python cli.py run --version d`.
   "In Version C, the server throws an HTTP 500 error. In Version D, the tax calculation is broken ($32.50 vs $36.50). SelfHeal refuses to heal genuine application bugs, returning `FAIL_FUNCTIONAL` and reporting the exact root cause."
6. **[01:25 - 01:30] Inspection**:
   Open `runs/latest/report.html` to show the audit report and recipe diff.

---

## Backup Readiness & Screen Recording

If presenting offline or in network-constrained environments:
1. Ensure `recorded/b_heal_trace.json` is present.
2. Run `python cli.py run --version b --mode recorded` to demonstrate the full healing pipeline with deterministic replay.
3. To record a demo video without capturing secrets:
   - Close any open `.env` tabs in your code editor.
   - Run `powershell -ExecutionPolicy Bypass -File scripts/demo.ps1` in a clear terminal window.
   - Open `http://127.0.0.1:8080` in the browser to display the live dashboard.
   - Open `runs/latest/report.html` to review the generated report.

---

## Test Suite Execution

Run the complete test suite across all modules:
```powershell
pytest -q
```
Expected result: **155 passed** (137 core SelfHeal engine tests + 18 GitHub Change Intelligence tests).

---

## GitHub Change Intelligence

**GitHub Change Intelligence** performs grounded commit diff analysis between any two commits, branches, or tags in a GitHub repository. It predicts UI locator drift, calculation modifications, broken endpoints, and deleted test coverage before running end-to-end test suites.

### Architecture & Data Flow

```
                      +---------------------------------------+
                      | User / CLI / Webhook Input            |
                      | (Repo URL, Base Ref, Head Ref)        |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | Security & SSRF Validation            |
                      | (HTTPS only, github.com, sanitize)    |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | Isolated Git Sandbox                  |
                      | (Temporary bare/shallow clone, no     |
                      | shell=True, disabled hooks, timeout)  |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | Grounded Diff & AST Analysis          |
                      | - UI/UX locators & form changes       |
                      | - Business logic & calculations       |
                      | - Backend API routes & models         |
                      | - Test additions & deletions          |
                      | - Dependencies & configuration        |
                      +-------------------+-------------------+
                                          |
                        +-----------------+-----------------+
                        |                                   |
                LLM Configured                      LLM Not Configured /
                (Google Gemini)                     Rate Limit Exhausted
                        |                                   |
                        v                                   v
             [AI-Assisted Synthesis]             [Deterministic Fallback]
             (Untrusted input guarded)           (100% verified facts)
                        |                                   |
                        +-----------------+-----------------+
                                          |
                                          v
                      +---------------------------------------+
                      | Standalone Audit Bundle               |
                      | runs/github_analysis/<job_id>/        |
                      | - report.html (interactive UI)        |
                      | - report.json (Pydantic schema)       |
                      | - report.md   (Markdown summary)      |
                      +---------------------------------------+
```

### Exact Startup & Analysis Commands (PowerShell)

#### 1. Interactive Web Dashboard
Start the web dashboard and navigate to the GitHub Intelligence studio:
```powershell
# Start web dashboard on port 8080
python cli.py serve --dashboard

# Open browser to:
# http://127.0.0.1:8080/github-intelligence
```

#### 2. Command-Line Interface (CLI)
Analyze any public repository directly from PowerShell:
```powershell
# Compare specific release tags
python cli.py analyze --repo https://github.com/pallets/flask --base 3.1.2 --head 3.1.3

# Compare latest commit with its parent
python cli.py analyze --repo https://github.com/psf/requests
```

#### 3. Real Git Commit Demonstration Script
Run the automated end-to-end demonstration on a real 2-commit repository fixture:
```powershell
python scripts/demo_github_analysis.py
```

### REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/github-analysis` | Submit repository comparison job (`repo_url`, `base_ref`, `head_ref`). Returns `202 Accepted` with `job_id`. |
| `GET` | `/api/github-analysis/<job_id>` | Poll job progress and status (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`). |
| `GET` | `/api/github-analysis/<job_id>/report` | Retrieve completed, validated Pydantic JSON report. |
| `GET` | `/api/github-analysis/<job_id>/html` | Serve standalone interactive HTML report. |

### Selecting Base and Target Commits
- **Default Behavior**: If `head_ref` is omitted, the engine uses `HEAD`. If `base_ref` is omitted, the engine automatically resolves the target commit's first parent (`HEAD~1`).
- **Explicit References**: Specify commit SHAs (e.g. `2179ae9`), branch names (`main`, `feature/checkout`), or tags (`v2.1.0`).

### Deterministic vs AI-Assisted Modes
1. **Deterministic Mode**: Operates strictly via AST inspection, diff regex, and Git numstat analysis. Identifies removed assertions, button locator changes, and calculation revisions with 100% ground truth and zero external dependencies.
2. **AI-Assisted Mode**: When Google Gemini (`gemini-2.5-flash`) is available, the engine synthesizes an executive summary highlighting testing advice and risk considerations. All repository data is treated as untrusted input and guarded against prompt injection. If the LLM quota is exhausted or unconfigured, the engine cleanly falls back to deterministic mode without failing.

### Security Guarantees
- **SSRF Prevention**: Strictly restricts repositories to `https://github.com/` (blocks internal IP ranges, loopbacks, and credentials).
- **Subprocess Safety**: All Git commands execute via structured argument lists (`shell=False`). No user input is ever concatenated into shell strings.
- **Sandboxing**: Repositories are cloned with `--no-checkout`, `-c core.hooksPath=/dev/null`, and cleaned up automatically upon exit. Analyzed code is never executed or imported.
- **Secret Redaction**: API keys, bearer tokens, private keys, and 16-digit payment card numbers are masked across diffs, reports, and logs.
- **Path Traversal Protection**: Job identifiers are validated with `^[a-zA-Z0-9_\-]+$`, rejecting directory traversal (`..`).

### Running Feature Tests
```powershell
pytest tests/test_repo_analysis.py -v
```
Expected result: **18 passed**.

