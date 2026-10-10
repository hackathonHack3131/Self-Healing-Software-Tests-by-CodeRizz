# AegisTest — Backend & Self-Healing Engine
> **Intent-Aware End-to-End Testing That Survives Interface Changes**

---

## 🌟 Overview

The **AegisTest Self-Healing Engine** is an intent-aware browser automation platform built with **Java 21**, **Spring Boot 3.3.4**, and **Playwright for Java**. Unlike traditional test automation frameworks that break whenever a CSS selector, DOM hierarchy, or accessible label is modified, AegisTest continuously aligns live browser actions with high-level user intent.

### Key Capabilities
- **Natural Language Intent Compilation**: Converts goals like *"Complete checkout with a valid credit card and confirm the order"* into structured, verifiable execution plans.
- **Deep Browser Introspection**: Extracts accessible roles, ARIA labels, DOM ancestry, and bounding boxes via Playwright.
- **Transparent Multi-Dimensional Scoring**: Evaluates candidate replacement elements across Semantic Intent (40%), Text Similarity (30%), DOM Context (20%), and Visual Position (10%).
- **Safety & Idempotency Safeguards**: Rejects ambiguous candidates, enforces configurable confidence thresholds, and halts retries past safety limits.
- **Outcome Verification**: Validates explicit business outcomes in live DOM (e.g. order confirmation state, order tokens) rather than assuming a successful click equals success.
- **Dual Execution Modes**:
  - `RULE_BASED`: 100% deterministic, offline-capable fallback engine that powers the Version A/Version B demo without requiring API keys.
  - `AI_ASSISTED`: LLM reasoning provider via WebClient when external credentials (`AI_API_KEY`) are present.
- **Live SSE Event Streaming**: Pushes real-time execution steps, candidate selections, and DOM mutation events to the frontend.

---

## 🛠 Technology Stack

- **Runtime**: Java 21+ / 25
- **Framework**: Spring Boot 3.3.4 (Spring Web, Spring Validation, Spring Data JPA, WebFlux)
- **Browser Automation**: Playwright for Java 1.47.0
- **Database**: MySQL 8.x (with automatic, resilient embedded H2 fallback for zero-configuration local runs)
- **Migrations**: Flyway
- **Real-Time Streaming**: Server-Sent Events (SSE `SseEmitter`)
- **Containerization**: Docker & Docker Compose

---

## 🚀 Quick Start (Local Setup)

### 1. Build the Backend
From the `Backend/` directory:
```powershell
.\mvnw.cmd clean package -DskipTests
```
*(Or use `mvn clean package -DskipTests` if Maven is on your system PATH)*

### 2. Run Tests
```powershell
.\mvnw.cmd test
```

### 3. Start the Server
```powershell
.\mvnw.cmd spring-boot:run
```
The backend server will start on port **`8000`** (`http://localhost:8000`).

---

## 🐳 Running with Docker Compose

To run the complete backend with a dedicated MySQL 8.0 container:
```bash
docker-compose up --build
```
This boots:
1. `aegis-mysql`: MySQL 8.0 container on port `3306` with persistent volume and healthcheck.
2. `aegis-backend`: Spring Boot container on port `8000` with Playwright dependencies pre-installed.

---

## 📡 REST API Reference

### Health & Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Healthcheck and backend status |
| `GET` | `/api/dashboard` | Dashboard metrics, pass rates, healing trends, recent runs |

### Test Management
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tests` | List all test cases |
| `POST` | `/api/tests` | Create a new intent-driven test case |
| `GET` | `/api/tests/{id}` | Get test case by ID |
| `PUT` | `/api/tests/{id}` | Update test case |
| `DELETE` | `/api/tests/{id}` | Delete test case |
| `POST` | `/api/tests/{id}/run` | Dispatch live asynchronous browser run |

### Execution & Streaming
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/runs/{id}` | Get test run status, steps, and logs |
| `GET` | `/api/runs/{id}/events` | **Server-Sent Events (SSE)** real-time stream |
| `GET` | `/api/runs/{id}/report` | Detailed self-healing report |
| `POST` | `/api/runs/{id}/cancel` | Abort running browser execution |

### Demo Lab Controls
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/demo/reset` | Reset demo to baseline **Version A** (`#checkout-button`) |
| `POST` | `/api/demo/version-b` | Switch demo to redesigned **Version B** (restructured DOM) |
| `POST` | `/api/demo/run` | Execute demo workflow (`{"version": "A"|"B", "selfHealing": true|false}`) |
| `GET` | `/api/demo/compare` | Inspect structural DOM differences between Version A & B |

### Reports
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/reports` | List recent execution reports |
| `GET` | `/api/reports/{id}` | Get report by ID |
| `GET` | `/api/reports/{id}/export` | Export report as Markdown download |

---

## 🔄 Real-Time SSE Event Types

When subscribed to `/api/runs/{id}/events`, the backend streams the following structured events:
- `connected`: Initial client handshake
- `run.started`: Run initialized with target URL and intent
- `page.inspected`: Page introspected with element count
- `plan.generated`: Structured execution plan created
- `step.started`: Step execution began
- `step.failed`: Baseline locator timed out or failed
- `change.detected`: UI mutation classified (`selector_renamed`, `container_moved`, etc.)
- `healing.started`: Self-healing candidate discovery activated
- `candidate.selected`: Highest-scoring replacement element chosen
- `step.repaired`: Repaired action executed and verified
- `assertion.passed`: Business outcome verified in live DOM
- `assertion.failed`: Business outcome verification failed
- `run.completed`: Execution completed (`passed`, `healed`, or `failed`)

---

## 🧪 Demonstration Workflow (Version A vs Version B)

The engine includes a self-contained interactive checkout app served at `http://localhost:8000/demo/index.html` (and also works seamlessly with Vite at `http://localhost:5173`):

1. **Version A (Baseline)**:
   - Contains customer shipping, payment details, and submit button `#checkout-button`.
   - Executing the test passes directly with status `PASSED` (0 healing attempts).
2. **Version B (Breaking UI Redesign)**:
   - Deliberately removes `#checkout-button`.
   - Relocates the button into `<div class="action-dock bottom-sticky">`.
   - Renames visible label to *"Place My Order"*, with class `.btn-primary-gradient-v2` and test ID `place-order-cta`.
3. **Execution with Self-Healing = FALSE**:
   - Selector `#checkout-button` times out after 5000ms.
   - Run halts immediately with status `FAILED`.
4. **Execution with Self-Healing = TRUE**:
   - Engine detects `#checkout-button` missing.
   - Scans DOM and scores alternative candidates.
   - Selects `button#place-order-cta` with **96.4% confidence**.
   - Reconstructs and executes click on repaired locator.
   - Verifies order confirmation screen (`Order #ORD-84920`).
   - Produces report with status `HEALED_PASSED`.

---

## ⚙️ Environment Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8000` | HTTP port |
| `SPRING_DATASOURCE_URL` | `jdbc:mysql://localhost:3306/aegis_test...` | MySQL JDBC URL |
| `SPRING_DATASOURCE_USERNAME` | `root` | MySQL user |
| `SPRING_DATASOURCE_PASSWORD` | `root` | MySQL password |
| `BROWSER_HEADLESS` | `true` | Launch Chromium headless (`false` to view UI) |
| `BROWSER_SLOW_MO` | `100` | Delay between actions in ms for observation |
| `AI_PROVIDER` | `none` | AI provider (`none`, `openai`, `gemini`, `anthropic`) |
| `AI_API_KEY` | *(empty)* | Optional API key |
| `MAX_HEALING_PER_STEP` | `3` | Max repairs per single step |
| `MAX_TOTAL_HEALING` | `5` | Max repairs per test run |
| `CONFIDENCE_HIGH` | `0.85` | High confidence automatic repair threshold |
| `CONFIDENCE_MEDIUM` | `0.60` | Medium confidence threshold |
