export type ExecutionStatus = 
  | 'queued' 
  | 'running' 
  | 'detecting_change' 
  | 'healing' 
  | 'verifying' 
  | 'passed' 
  | 'failed' 
  | 'cancelled';

export type StepStatus = 'pending' | 'running' | 'passed' | 'failed' | 'healing' | 'healed';

export interface CandidateElement {
  id: string;
  selector: string;
  tag: string;
  text: string;
  role: string;
  attributes: Record<string, string>;
  confidence: number;
  matchBreakdown: {
    semanticIntent: number;
    textSimilarity: number;
    domContext: number;
    visualPosition: number;
  };
  reasoning: string;
}

export interface HealingAttempt {
  id: string;
  stepNumber: number;
  failedSelector: string;
  failureReason: string;
  strategy: 'semantic_intent' | 'visual_similarity' | 'dom_heuristic' | 'llm_synthesis';
  candidatesScored: CandidateElement[];
  selectedCandidate: CandidateElement;
  repairedAction: string;
  repairedSelector: string;
  confidenceScore: number;
  durationMs: number;
  timestamp: string;
}

export interface TestStep {
  id: string;
  stepNumber: number;
  description: string;
  originalAction: string;
  originalSelector: string;
  status: StepStatus;
  durationMs?: number;
  error?: string;
  healingAttempt?: HealingAttempt;
  screenshotBefore?: string;
  screenshotAfter?: string;
}

export interface TestCase {
  id: string;
  name: string;
  targetUrl: string;
  intent: string;
  environment: 'production' | 'staging' | 'local';
  browser: 'chromium' | 'firefox' | 'webkit';
  selfHealingEnabled: boolean;
  maxHealingAttempts: number;
  expectedOutcome: string;
  createdAt: string;
  lastRunAt?: string;
  status?: 'passed' | 'failed' | 'healed' | 'never_run';
}

export interface TestRun {
  id: string;
  testId: string;
  testName: string;
  targetUrl: string;
  intent: string;
  status: ExecutionStatus;
  currentStepIndex: number;
  totalSteps: number;
  steps: TestStep[];
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  initialResult?: 'passed' | 'failed';
  finalResult?: 'passed' | 'failed' | 'healed';
  healingCount: number;
  isSimulated?: boolean;
  currentScreenshot?: string;
  logs: ConsoleLogEntry[];
  detectedChanges: UiChange[];
  finalVerification?: {
    verified: boolean;
    evidenceText: string;
    targetSelector: string;
  };
}

export interface ConsoleLogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'ai' | 'success';
  message: string;
  details?: Record<string, any>;
}

export interface UiChange {
  id: string;
  elementDescription: string;
  type: 'selector_renamed' | 'container_moved' | 'dom_restructured' | 'styling_changed';
  previousDomSnippet: string;
  newDomSnippet: string;
  impactScore: 'low' | 'medium' | 'high';
  detectedAt: string;
}

export interface DashboardMetrics {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  selfHealedTests: number;
  testSuccessRate: number;
  averageExecutionTimeMs: number;
  healingSuccessRate: number;
  isBackendConnected: boolean;
  recentRuns: TestRunSummary[];
  trends: {
    dates: string[];
    passRates: number[];
    healedRates: number[];
    failureRates: number[];
  };
  healingActivity: {
    date: string;
    healedCount: number;
    failedHealCount: number;
  }[];
  latestUiChanges: UiChange[];
  recentFailures: {
    id: string;
    testName: string;
    failureReason: string;
    recommendedAction: string;
    occurredAt: string;
  }[];
}

export interface TestRunSummary {
  id: string;
  testId: string;
  testName: string;
  targetApp: string;
  executedAt: string;
  durationFormatted: string;
  initialResult: 'passed' | 'failed';
  finalResult: 'passed' | 'failed' | 'healed';
  healingStatus: 'healed' | 'unhealed' | 'none_needed';
  repairedStepsCount: number;
}

export interface DemoState {
  version: 'A' | 'B';
  selfHealingEnabled: boolean;
  currentExecution?: TestRun;
  orderPlaced: boolean;
  lastRunReport?: TestReport;
}

export interface TestReport {
  id: string;
  runId: string;
  testName: string;
  testIntent: string;
  executedAt: string;
  environment: string;
  initialExecutionStatus: 'passed' | 'failed';
  finalExecutionStatus: 'passed' | 'failed' | 'healed';
  durationMs: number;
  healed: boolean;
  repairedSteps: number;
  detectedInterfaceChanges: UiChange[];
  healingAttempts: HealingAttempt[];
  assertionResults: {
    assertion: string;
    passed: boolean;
    evidence: string;
  }[];
  remainingRisks: string[];
  maintenanceSuggestions: string[];
  isSimulated: boolean;
}
