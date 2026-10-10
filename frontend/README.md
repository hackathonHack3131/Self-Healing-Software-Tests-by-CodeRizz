# AegisTest — Intent-Aware Self-Healing E2E Testing Platform
### Tests That Heal Themselves: Intent-Aware End-to-End Testing That Survives Interface Changes

AegisTest is a next-generation automated testing platform engineered to eliminate flaky end-to-end tests caused by selector renaming, container restructuring, and DOM mutations.

---

## 🌟 The Core Problem AegisTest Solves

Traditional test frameworks (Selenium, Cypress, Playwright) rely on rigid selectors like `#checkout-button`.
When frontend engineers refactor a button (e.g. renaming it to *"Place My Order"*, moving it into a floating dock, or replacing IDs with Tailwind utility classes), tests break instantly—even when the actual user journey is 100% operational.

### The AegisTest Paradigm
Testers express objectives using **Natural Language Intent**:
> *"Complete checkout with a valid credit card and confirm that the order confirmation page is displayed."*

AegisTest:
1. **Understands Intent**: Maps user objectives to dynamic action pipelines.
2. **Executes Headless Workflows**: Dispatches actions in Chromium, Firefox, or WebKit.
3. **Detects UI Drift**: Intercepts missing elements and DOM mutations.
4. **Heals Autonomously**: Scores candidate elements via semantic intent, text similarity, DOM context proximity, and visual weight.
5. **Verifies Business Outcomes**: Asserts that real end-states (e.g., Order #ORD-84920 issued) are reached, safeguarding genuine user workflows.

---

## 🚀 Key Features

- **Version A vs. Version B Star Demo Lab (`/demo-lab`)**:
  - Live interactive checkout application with controlled UI mutations.
  - **Version A**: Baseline checkout form with `#checkout-button`.
  - **Version B**: Redesigned modern interface where `#checkout-button` is removed and replaced by `.action-dock > .btn-primary-gradient-v2: 'Place My Order'`.
  - Watch traditional tests fail and AegisTest synthesize the healed locator in real time with 96.4% confidence!
  - Side-by-side DOM Diff visualizer.
- **Analytics & Telemetry Dashboard (`/dashboard`)**:
  - Total Tests, Direct Passes, Self-Healed Tests, Authentic Bugs, Success Rate, Execution Duration.
  - 7-day trend area charts and daily repair activity bar charts.
  - Real-time UI mutation ticker and AI root-cause diagnostics.
- **Intent-Based Test Builder (`/tests/new`)**:
  - Natural-language intent as the immutable source of truth.
  - Quick-fill templates (Checkout, Auth, Cart Recalculation).
  - Dynamic step synthesizer preview.
  - Zod validation and test fixture JSON editor.
- **Live Test Execution Monitor (`/runs/[id]`)**:
  - Live step timeline with status badges (`passed`, `failed`, `healed`).
  - Wireframe browser viewport inspection highlighting repaired elements.
  - Real-time diagnostic console with filterable logs and copy tools.
- **Audit Reports & Post-Mortem (`/reports/[id]`)**:
  - Full trace of initial failures, AI candidate scoring breakdown, repaired actions, and assertion proofs.
  - One-click JSON download and PDF/Print export.
- **Resilient Backend Integration (`/settings`)**:
  - Connects to any REST backend (e.g., FastAPI / Node on port 8000).
  - Automatically activates high-fidelity simulated fallback runner if backend is offline.
  - Built-in Next.js REST API routes implementing the complete backend contract.

---

## 🛠️ Technology Stack

- **Framework**: Next.js 14 (App Router) + TypeScript
- **Styling**: Tailwind CSS (Dark Navy & Electric Violet/Cyan design system)
- **Charts**: Recharts (Pass/Fail area trends & daily repair activity)
- **Animations**: Framer Motion & Canvas Confetti
- **Icons**: Lucide React
- **Forms & Validation**: React Hook Form + Zod
- **API State**: TanStack React Query

---

## 💻 Local Setup & Running

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```
Key variables:
- `NEXT_PUBLIC_API_URL`: Backend REST endpoint (default: `http://localhost:8000`)
- `NEXT_PUBLIC_ENABLE_SIMULATION_FALLBACK`: `true` (enables standalone offline demo runner)

### 3. Launch Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🎯 Hackathon Presentation Guide (Step-by-Step)

1. **Start on the Landing Page (`/`)**:
   - Showcase the problem statement and the 5-stage intent lifecycle.
   - Contrast traditional CSS selector brittleness vs. semantic intent.
2. **Open the Version A/B Demo Lab (`/demo-lab`)**:
   - Step 1: Click **"Run Test on Version A"** → Green direct pass in 1.4s.
   - Step 2: Click **"Version B (Mutated UI)"** → Demonstrates the redesigned store layout where `#checkout-button` is removed.
   - Step 3: Turn **Self-Healing OFF** and run the test → Fails with `NoSuchElementException: '#checkout-button' not found`.
   - Step 4: Turn **Self-Healing ON** and run the test → AI intercept triggers, discovers `'Place My Order'` in `.action-dock` with 96.4% confidence, synthesizes repaired click, verifies order #ORD-84920, and triggers celebration confetti!
   - Step 5: Click **"Compare DOM Diff"** to show the exact code diff.
3. **Inspect the Dashboard (`/dashboard`)**:
   - Review the metrics showing tests saved from failing via self-healing.
4. **Export Report (`/reports/rep-chk-902`)**:
   - Show the comprehensive post-mortem report and download the JSON audit artifact.

---

## 📡 REST API Integration Contract

The frontend connects to the following REST API endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health & latency check |
| `GET` | `/api/dashboard` | Dashboard metrics and trend data |
| `GET` | `/api/tests` | List all test specifications |
| `POST` | `/api/tests` | Create a new intent-based test |
| `GET` | `/api/tests/:id` | Retrieve single test specification |
| `POST` | `/api/tests/:id/run` | Execute test run |
| `GET` | `/api/runs/:id` | Poll live run telemetry |
| `GET` | `/api/runs/:id/report`| Fetch detailed post-mortem audit report |
| `POST` | `/api/demo/reset` | Reset demo store to baseline Version A |
| `POST` | `/api/demo/version-b` | Apply Version B UI restructuring |
| `POST` | `/api/demo/run` | Execute demo run on Version A or B |
| `GET` | `/api/demo/compare` | Retrieve side-by-side DOM diff data |

*(Note: When a remote backend is offline, AegisTest automatically services these endpoints via its built-in Next.js route handlers and client-side fallback engine).*
