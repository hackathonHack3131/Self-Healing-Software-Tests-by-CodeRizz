import { 
  DashboardMetrics, 
  TestCase, 
  TestRun, 
  TestReport, 
  DemoComparisonResult, 
  DemoState, 
  ConsoleLogEntry,
  CandidateElement 
} from "@/types";
import { SEED_DASHBOARD_METRICS, SEED_TESTS, SAMPLE_CANDIDATE_ELEMENTS, SEED_UI_CHANGES } from "./mock-data";

export interface DemoComparisonResult {
  versionA: {
    checkoutSelector: string;
    domTree: string;
    buttonText: string;
    containerClass: string;
  };
  versionB: {
    checkoutSelector: string;
    domTree: string;
    buttonText: string;
    containerClass: string;
  };
  structuralDifferences: {
    field: string;
    impact: string;
    original: string;
    modified: string;
  }[];
}

class ApiService {
  private baseUrl: string = "http://localhost:8000";
  private localTests: TestCase[] = [...SEED_TESTS];
  private localRuns: Map<string, TestRun> = new Map();
  private demoState: DemoState = {
    version: "A",
    selfHealingEnabled: true,
    orderPlaced: false,
  };

  constructor() {
    if (typeof window !== "undefined") {
      const storedUrl = localStorage.getItem("aegis_backend_url");
      if (storedUrl) this.baseUrl = storedUrl;

      const storedTests = localStorage.getItem("aegis_local_tests");
      if (storedTests) {
        try {
          this.localTests = JSON.parse(storedTests);
        } catch {
          // ignore
        }
      }
    }
  }

  public setBaseUrl(url: string) {
    this.baseUrl = url;
    if (typeof window !== "undefined") {
      localStorage.setItem("aegis_backend_url", url);
    }
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  // Health Check
  public async getHealth(): Promise<{ status: "ok" | "degraded"; latencyMs: number; backendConnected: boolean }> {
    const start = Date.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${this.baseUrl}/api/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        return { status: "ok", latencyMs: Date.now() - start, backendConnected: true };
      }
    } catch {
      // Backend not running on configured port
    }
    return { status: "ok", latencyMs: 0, backendConnected: false };
  }

  // Dashboard Metrics
  public async getDashboard(): Promise<DashboardMetrics> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${this.baseUrl}/api/dashboard`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        return { ...data, isBackendConnected: true };
      }
    } catch {
      // Fallback to local simulated metrics
    }

    return {
      ...SEED_DASHBOARD_METRICS,
      totalTests: this.localTests.length + 44,
      isBackendConnected: false,
    };
  }

  // Get All Tests
  public async getTests(): Promise<TestCase[]> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${this.baseUrl}/api/tests`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        return await res.json();
      }
    } catch {
      // Fallback
    }
    return this.localTests;
  }

  // Create Test
  public async createTest(testData: Partial<TestCase>): Promise<TestCase> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const res = await fetch(`${this.baseUrl}/api/tests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(testData),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    const newTest: TestCase = {
      id: `test-${Date.now().toString(36)}`,
      name: testData.name || "Untitled Intent Test",
      targetUrl: testData.targetUrl || "http://localhost:5173",
      intent: testData.intent || "",
      environment: testData.environment || "staging",
      browser: testData.browser || "chromium",
      selfHealingEnabled: testData.selfHealingEnabled ?? true,
      maxHealingAttempts: testData.maxHealingAttempts || 3,
      expectedOutcome: testData.expectedOutcome || "Target verification achieved",
      createdAt: new Date().toISOString(),
      status: "never_run",
    };

    this.localTests.unshift(newTest);
    if (typeof window !== "undefined") {
      localStorage.setItem("aegis_local_tests", JSON.stringify(this.localTests));
    }
    return newTest;
  }

  // Get Test by ID
  public async getTest(id: string): Promise<TestCase | null> {
    try {
      const res = await fetch(`${this.baseUrl}/api/tests/${id}`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return this.localTests.find((t) => t.id === id) || null;
  }

  // Run Test by ID
  public async runTest(id: string): Promise<TestRun> {
    try {
      const res = await fetch(`${this.baseUrl}/api/tests/${id}/run`, { method: "POST" });
      if (res.ok) return await res.json();
    } catch {
      // Fallback to local simulation
    }

    const test = this.localTests.find((t) => t.id === id) || this.localTests[0];
    const run = this.generateSimulatedRun(test);
    this.localRuns.set(run.id, run);
    return run;
  }

  // Get Run Status
  public async getRun(id: string): Promise<TestRun | null> {
    try {
      const res = await fetch(`${this.baseUrl}/api/runs/${id}`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return this.localRuns.get(id) || this.generateSimulatedRun(this.localTests[0], id);
  }

  // Get Run Report
  public async getRunReport(id: string): Promise<TestReport | null> {
    try {
      const res = await fetch(`${this.baseUrl}/api/runs/${id}/report`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    return {
      id: `report-${id}`,
      runId: id,
      testName: "E-Commerce Checkout & Order Confirmation",
      testIntent: "Complete checkout with a valid credit card and confirm that the order confirmation page is displayed.",
      executedAt: new Date().toISOString(),
      environment: "staging",
      initialExecutionStatus: "failed",
      finalExecutionStatus: "healed",
      durationMs: 2780,
      healed: true,
      repairedSteps: 1,
      detectedInterfaceChanges: SEED_UI_CHANGES,
      healingAttempts: [
        {
          id: "heal-attempt-1",
          stepNumber: 4,
          failedSelector: "#checkout-button",
          failureReason: "Element not found in DOM tree: selector '#checkout-button' timed out after 5000ms. Button renamed to 'Place My Order' and wrapped inside 'div.action-dock'.",
          strategy: "semantic_intent",
          candidatesScored: SAMPLE_CANDIDATE_ELEMENTS,
          selectedCandidate: SAMPLE_CANDIDATE_ELEMENTS[0],
          repairedAction: "click('div.action-dock > button.btn-primary-gradient-v2')",
          repairedSelector: "div.action-dock > button.btn-primary-gradient-v2",
          confidenceScore: 0.964,
          durationMs: 420,
          timestamp: new Date().toISOString(),
        },
      ],
      assertionResults: [
        {
          assertion: "Customer name filled in shipping section",
          passed: true,
          evidence: "input[name='fullName'].value === 'Alex Morgan'",
        },
        {
          assertion: "Credit card details populated",
          passed: true,
          evidence: "4242 •••• •••• 4242 tokenized",
        },
        {
          assertion: "Checkout CTA clicked",
          passed: true,
          evidence: "Dispatched click to healed locator 'div.action-dock > button.btn-primary-gradient-v2'",
        },
        {
          assertion: "Order confirmation page rendered",
          passed: true,
          evidence: "Found text 'Thank you for your order! Order #ORD-84920' in DOM",
        },
      ],
      remainingRisks: [
        "Selector 'div.action-dock > button.btn-primary-gradient-v2' relies on Tailwind utility classes. Recommend adding data-testid='checkout-submit' to baseline code.",
      ],
      maintenanceSuggestions: [
        "Update repository test definition to reflect new semantic token.",
        "Auto-PR generated: branch 'fix/auto-heal-checkout-selector'.",
      ],
      isSimulated: true,
    };
  }

  // Demo Lab Endpoints
  public async resetDemo(): Promise<{ version: "A"; message: string }> {
    try {
      const res = await fetch(`${this.baseUrl}/api/demo/reset`, { method: "POST" });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    this.demoState.version = "A";
    this.demoState.orderPlaced = false;
    return { version: "A", message: "Demo reset to baseline Version A successfully." };
  }

  public async setDemoVersionB(): Promise<{ version: "B"; message: string }> {
    try {
      const res = await fetch(`${this.baseUrl}/api/demo/version-b`, { method: "POST" });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    this.demoState.version = "B";
    this.demoState.orderPlaced = false;
    return { version: "B", message: "Applied modern DOM restructuring (Version B)." };
  }

  public async runDemo(version: "A" | "B", selfHealing: boolean): Promise<TestRun> {
    try {
      const res = await fetch(`${this.baseUrl}/api/demo/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version, selfHealing }),
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback to local controlled simulation
    }

    return this.generateDemoRun(version, selfHealing);
  }

  public async compareDemo(): Promise<DemoComparisonResult> {
    try {
      const res = await fetch(`${this.baseUrl}/api/demo/compare`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    return {
      versionA: {
        checkoutSelector: "#checkout-button",
        buttonText: "Complete Purchase",
        containerClass: "form-actions-flat",
        domTree: `<form id="checkout-form">
  <div class="customer-info">...</div>
  <div class="form-actions-flat">
    <button id="checkout-button" class="btn-checkout">Complete Purchase</button>
  </div>
</form>`,
      },
      versionB: {
        checkoutSelector: "div.action-dock > button.btn-primary-gradient-v2",
        buttonText: "Place My Order",
        containerClass: "action-dock bottom-sticky",
        domTree: `<form id="checkout-form">
  <div class="customer-info">...</div>
  <div class="action-dock bottom-sticky">
    <button class="btn-primary-gradient-v2" data-testid="place-order-cta">
      Place My Order
    </button>
  </div>
</form>`,
      },
      structuralDifferences: [
        {
          field: "Primary Selector ID",
          impact: "Critical (Breaks static locator)",
          original: "#checkout-button exists",
          modified: "#checkout-button removed entirely",
        },
        {
          field: "Button Label Text",
          impact: "Medium",
          original: "'Complete Purchase'",
          modified: "'Place My Order'",
        },
        {
          field: "DOM Container Location",
          impact: "High",
          original: "Inside .form-actions-flat",
          modified: "Relocated to sticky .action-dock wrapper",
        },
        {
          field: "Semantic Role & Intent",
          impact: "Preserved (100% Intent Compatible)",
          original: "Form submit trigger for checkout",
          modified: "Form submit trigger for checkout",
        },
      ],
    };
  }

  // Simulation Helper for Demo Lab
  public generateDemoRun(version: "A" | "B", selfHealing: boolean): TestRun {
    const isVersionA = version === "A";
    const now = new Date().toISOString();

    if (isVersionA) {
      return {
        id: `run-demo-a-${Date.now()}`,
        testId: "demo-checkout",
        testName: "E-Commerce Checkout Workflow",
        targetUrl: "http://localhost:5173/checkout",
        intent: "Complete checkout with a valid credit card and verify order confirmation.",
        status: "passed",
        currentStepIndex: 4,
        totalSteps: 4,
        startedAt: now,
        completedAt: now,
        durationMs: 1420,
        initialResult: "passed",
        finalResult: "passed",
        healingCount: 0,
        isSimulated: true,
        steps: [
          {
            id: "step-1",
            stepNumber: 1,
            description: "Fill customer shipping information",
            originalAction: "fill('input#customer-name', 'Alex Morgan')",
            originalSelector: "input#customer-name",
            status: "passed",
            durationMs: 240,
          },
          {
            id: "step-2",
            stepNumber: 2,
            description: "Select Express Shipping method",
            originalAction: "click('input[name=\"shipping\"][value=\"express\"]')",
            originalSelector: "input[name=\"shipping\"][value=\"express\"]",
            status: "passed",
            durationMs: 180,
          },
          {
            id: "step-3",
            stepNumber: 3,
            description: "Enter test payment credentials",
            originalAction: "fill('input#card-number', '4242••••••••4242')",
            originalSelector: "input#card-number",
            status: "passed",
            durationMs: 310,
          },
          {
            id: "step-4",
            stepNumber: 4,
            description: "Click checkout confirmation button",
            originalAction: "click('#checkout-button')",
            originalSelector: "#checkout-button",
            status: "passed",
            durationMs: 290,
          },
        ],
        logs: [
          { id: "log-1", timestamp: "00:00.120", level: "info", message: "Browser instance ready (Chromium headless)" },
          { id: "log-2", timestamp: "00:00.350", level: "info", message: "Loaded target application: http://localhost:5173/checkout" },
          { id: "log-3", timestamp: "00:00.620", level: "info", message: "Step 1: Filled customer shipping fields [Alex Morgan]" },
          { id: "log-4", timestamp: "00:00.820", level: "info", message: "Step 2: Selected Express Shipping" },
          { id: "log-5", timestamp: "00:01.120", level: "info", message: "Step 3: Populated tokenized test payment credentials" },
          { id: "log-6", timestamp: "00:01.390", level: "info", message: "Step 4: Located '#checkout-button' successfully. Dispatched click." },
          { id: "log-7", timestamp: "00:01.420", level: "success", message: "Order confirmation received: #ORD-77192. Test Passed!" },
        ],
        detectedChanges: [],
        finalVerification: {
          verified: true,
          evidenceText: "Order confirmation screen rendered. Order ID #ORD-77192 verified in DOM.",
          targetSelector: "#order-confirmation",
        },
      };
    }

    // Version B with Self Healing = FALSE
    if (!selfHealing) {
      return {
        id: `run-demo-b-failed-${Date.now()}`,
        testId: "demo-checkout",
        testName: "E-Commerce Checkout Workflow",
        targetUrl: "http://localhost:5173/checkout",
        intent: "Complete checkout with a valid credit card and verify order confirmation.",
        status: "failed",
        currentStepIndex: 3,
        totalSteps: 4,
        startedAt: now,
        completedAt: now,
        durationMs: 5320,
        initialResult: "failed",
        finalResult: "failed",
        healingCount: 0,
        isSimulated: true,
        steps: [
          {
            id: "step-1",
            stepNumber: 1,
            description: "Fill customer shipping information",
            originalAction: "fill('input#customer-name', 'Alex Morgan')",
            originalSelector: "input#customer-name",
            status: "passed",
            durationMs: 250,
          },
          {
            id: "step-2",
            stepNumber: 2,
            description: "Select Express Shipping method",
            originalAction: "click('input[name=\"shipping\"][value=\"express\"]')",
            originalSelector: "input[name=\"shipping\"][value=\"express\"]",
            status: "passed",
            durationMs: 190,
          },
          {
            id: "step-3",
            stepNumber: 3,
            description: "Enter test payment credentials",
            originalAction: "fill('input#card-number', '4242••••••••4242')",
            originalSelector: "input#card-number",
            status: "passed",
            durationMs: 320,
          },
          {
            id: "step-4",
            stepNumber: 4,
            description: "Click checkout confirmation button",
            originalAction: "click('#checkout-button')",
            originalSelector: "#checkout-button",
            status: "failed",
            error: "TimeoutError: Element '#checkout-button' not found in DOM after 5000ms. Test aborted because self-healing is disabled.",
            durationMs: 5010,
          },
        ],
        logs: [
          { id: "log-1", timestamp: "00:00.120", level: "info", message: "Browser instance ready (Chromium headless)" },
          { id: "log-2", timestamp: "00:00.350", level: "info", message: "Loaded target application: http://localhost:5173/checkout (Version B)" },
          { id: "log-3", timestamp: "00:00.620", level: "info", message: "Step 1: Filled customer shipping fields" },
          { id: "log-4", timestamp: "00:00.820", level: "info", message: "Step 2: Selected Express Shipping" },
          { id: "log-5", timestamp: "00:01.120", level: "info", message: "Step 3: Populated payment credentials" },
          { id: "log-6", timestamp: "00:01.320", level: "warn", message: "Step 4: Looking for '#checkout-button'..." },
          { id: "log-7", timestamp: "00:06.320", level: "error", message: "NoSuchElementException: '#checkout-button' not found." },
          { id: "log-8", timestamp: "00:06.325", level: "error", message: "Test run FAILED. Self-healing is disabled in test configuration." },
        ],
        detectedChanges: [
          {
            id: "chg-b-1",
            elementDescription: "Checkout CTA Button",
            type: "selector_renamed",
            previousDomSnippet: '<button id="checkout-button">Complete Purchase</button>',
            newDomSnippet: '<div class="action-dock"><button class="btn-primary-gradient-v2">Place My Order</button></div>',
            impactScore: "high",
            detectedAt: now,
          },
        ],
      };
    }

    // Version B with Self Healing = TRUE -> HEALED!
    return {
      id: `run-demo-b-healed-${Date.now()}`,
      testId: "demo-checkout",
      testName: "E-Commerce Checkout Workflow",
      targetUrl: "http://localhost:5173/checkout",
      intent: "Complete checkout with a valid credit card and verify order confirmation.",
      status: "passed",
      currentStepIndex: 4,
      totalSteps: 4,
      startedAt: now,
      completedAt: now,
      durationMs: 2840,
      initialResult: "failed",
      finalResult: "healed",
      healingCount: 1,
      isSimulated: true,
      steps: [
        {
          id: "step-1",
          stepNumber: 1,
          description: "Fill customer shipping information",
          originalAction: "fill('input#customer-name', 'Alex Morgan')",
          originalSelector: "input#customer-name",
          status: "passed",
          durationMs: 250,
        },
        {
          id: "step-2",
          stepNumber: 2,
          description: "Select Express Shipping method",
          originalAction: "click('input[name=\"shipping\"][value=\"express\"]')",
          originalSelector: "input[name=\"shipping\"][value=\"express\"]",
          status: "passed",
          durationMs: 190,
        },
        {
          id: "step-3",
          stepNumber: 3,
          description: "Enter test payment credentials",
          originalAction: "fill('input#card-number', '4242••••••••4242')",
          originalSelector: "input#card-number",
          status: "passed",
          durationMs: 320,
        },
        {
          id: "step-4",
          stepNumber: 4,
          description: "Click checkout confirmation button",
          originalAction: "click('#checkout-button')",
          originalSelector: "#checkout-button",
          status: "healed",
          durationMs: 820,
          healingAttempt: {
            id: "heal-step-4",
            stepNumber: 4,
            failedSelector: "#checkout-button",
            failureReason: "Locator '#checkout-button' not found in mutated DOM tree. Button moved to '.action-dock' and renamed to 'Place My Order'.",
            strategy: "semantic_intent",
            candidatesScored: SAMPLE_CANDIDATE_ELEMENTS,
            selectedCandidate: SAMPLE_CANDIDATE_ELEMENTS[0],
            repairedAction: "click('div.action-dock > button.btn-primary-gradient-v2')",
            repairedSelector: "div.action-dock > button.btn-primary-gradient-v2",
            confidenceScore: 0.964,
            durationMs: 410,
            timestamp: now,
          },
        },
      ],
      logs: [
        { id: "log-1", timestamp: "00:00.120", level: "info", message: "Browser instance ready (Chromium headless)" },
        { id: "log-2", timestamp: "00:00.350", level: "info", message: "Target: http://localhost:5173/checkout (Version B with redesigned DOM)" },
        { id: "log-3", timestamp: "00:00.620", level: "info", message: "Step 1: Filled customer shipping fields" },
        { id: "log-4", timestamp: "00:00.820", level: "info", message: "Step 2: Selected Express Shipping" },
        { id: "log-5", timestamp: "00:01.120", level: "info", message: "Step 3: Populated payment credentials" },
        { id: "log-6", timestamp: "00:01.320", level: "warn", message: "Step 4: Selector '#checkout-button' failed to match." },
        { id: "log-7", timestamp: "00:01.330", level: "ai", message: "Self-Healing Engine activated: Inspecting DOM mutations against Intent 'Complete checkout'..." },
        { id: "log-8", timestamp: "00:01.520", level: "ai", message: "Discovered 3 interactive candidate elements. Computing semantic intent vector..." },
        { id: "log-9", timestamp: "00:01.710", level: "ai", message: "Candidate selected: 'div.action-dock > button.btn-primary-gradient-v2' (Confidence: 96.4%). Match reason: Submit role button with text 'Place My Order'." },
        { id: "log-10", timestamp: "00:01.880", level: "ai", message: "Synthesizing repaired action: click('div.action-dock > button.btn-primary-gradient-v2')" },
        { id: "log-11", timestamp: "00:02.140", level: "info", message: "Executing repaired action on live browser session..." },
        { id: "log-12", timestamp: "00:02.820", level: "success", message: "Verified state: Order confirmation screen reached! Order #ORD-84920 issued." },
        { id: "log-13", timestamp: "00:02.840", level: "success", message: "TEST PASSED VIA SELF-HEALING. Baseline locator update proposed." },
      ],
      detectedChanges: [
        {
          id: "chg-b-1",
          elementDescription: "Checkout CTA Button",
          type: "selector_renamed",
          previousDomSnippet: '<button id="checkout-button">Complete Purchase</button>',
          newDomSnippet: '<div class="action-dock"><button class="btn-primary-gradient-v2" data-testid="place-order-cta">Place My Order</button></div>',
          impactScore: "high",
          detectedAt: now,
        },
      ],
      finalVerification: {
        verified: true,
        evidenceText: "Order confirmation screen rendered. Order ID #ORD-84920 verified in DOM.",
        targetSelector: "div.order-confirmed-banner",
      },
    };
  }

  private generateSimulatedRun(test: TestCase, runId?: string): TestRun {
    const now = new Date().toISOString();
    return {
      id: runId || `run-${Date.now().toString(36)}`,
      testId: test.id,
      testName: test.name,
      targetUrl: test.targetUrl,
      intent: test.intent,
      status: "passed",
      currentStepIndex: 3,
      totalSteps: 3,
      startedAt: now,
      completedAt: now,
      durationMs: 2310,
      initialResult: "failed",
      finalResult: "healed",
      healingCount: 1,
      isSimulated: true,
      steps: [
        {
          id: "s1",
          stepNumber: 1,
          description: "Navigate to target URL and inspect interactive DOM tree",
          originalAction: `navigate('${test.targetUrl}')`,
          originalSelector: "window.location",
          status: "passed",
          durationMs: 450,
        },
        {
          id: "s2",
          stepNumber: 2,
          description: "Locate primary input elements from intent specification",
          originalAction: "locate(input[data-intent='primary'])",
          originalSelector: "input.target-input",
          status: "passed",
          durationMs: 380,
        },
        {
          id: "s3",
          stepNumber: 3,
          description: "Execute intent action and verify outcome",
          originalAction: "click('button#submit-action')",
          originalSelector: "button#submit-action",
          status: "healed",
          durationMs: 720,
          healingAttempt: {
            id: "heal-gen-1",
            stepNumber: 3,
            failedSelector: "button#submit-action",
            failureReason: "Selector 'button#submit-action' missing; button relocated to new layout container.",
            strategy: "semantic_intent",
            candidatesScored: SAMPLE_CANDIDATE_ELEMENTS,
            selectedCandidate: SAMPLE_CANDIDATE_ELEMENTS[0],
            repairedAction: "click('button[data-testid=\"place-order-cta\"]')",
            repairedSelector: "button[data-testid=\"place-order-cta\"]",
            confidenceScore: 0.952,
            durationMs: 390,
            timestamp: now,
          },
        },
      ],
      logs: [
        { id: "l1", timestamp: "00:00.100", level: "info", message: `Connecting to ${test.browser} runner...` },
        { id: "l2", timestamp: "00:00.450", level: "info", message: `Navigated to ${test.targetUrl}` },
        { id: "l3", timestamp: "00:00.830", level: "ai", message: `Synthesized user intent: "${test.intent}"` },
        { id: "l4", timestamp: "00:01.210", level: "warn", message: "Baseline selector timed out. Engaging Self-Healing Engine..." },
        { id: "l5", timestamp: "00:01.620", level: "ai", message: "Found semantic match with 95.2% confidence. Repaired locator." },
        { id: "l6", timestamp: "00:02.310", level: "success", message: `Verification passed: ${test.expectedOutcome}` },
      ],
      detectedChanges: SEED_UI_CHANGES.slice(0, 1),
      finalVerification: {
        verified: true,
        evidenceText: test.expectedOutcome,
        targetSelector: ".verified-outcome",
      },
    };
  }
}

export const api = new ApiService();
