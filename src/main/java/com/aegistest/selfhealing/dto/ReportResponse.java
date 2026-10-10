package com.aegistest.selfhealing.dto;

import java.util.ArrayList;
import java.util.List;

public class ReportResponse {
    private String id;
    private String runId;
    private String testName;
    private String testIntent;
    private String executedAt;
    private String environment;
    private String initialExecutionStatus;
    private String finalExecutionStatus;
    private long durationMs;
    private boolean healed;
    private int repairedSteps;
    private List<UiChangeDto> detectedInterfaceChanges = new ArrayList<>();
    private List<HealingAttemptDto> healingAttempts = new ArrayList<>();
    private List<AssertionItem> assertionResults = new ArrayList<>();
    private List<String> remainingRisks = new ArrayList<>();
    private List<String> maintenanceSuggestions = new ArrayList<>();
    private boolean isSimulated = false;

    public static class AssertionItem {
        private String assertion;
        private boolean passed;
        private String evidence;

        public AssertionItem() {}

        public AssertionItem(String assertion, boolean passed, String evidence) {
            this.assertion = assertion;
            this.passed = passed;
            this.evidence = evidence;
        }

        public String getAssertion() { return assertion; }
        public void setAssertion(String assertion) { this.assertion = assertion; }

        public boolean isPassed() { return passed; }
        public void setPassed(boolean passed) { this.passed = passed; }

        public String getEvidence() { return evidence; }
        public void setEvidence(String evidence) { this.evidence = evidence; }
    }

    public ReportResponse() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public String getTestName() { return testName; }
    public void setTestName(String testName) { this.testName = testName; }

    public String getTestIntent() { return testIntent; }
    public void setTestIntent(String testIntent) { this.testIntent = testIntent; }

    public String getExecutedAt() { return executedAt; }
    public void setExecutedAt(String executedAt) { this.executedAt = executedAt; }

    public String getEnvironment() { return environment; }
    public void setEnvironment(String environment) { this.environment = environment; }

    public String getInitialExecutionStatus() { return initialExecutionStatus; }
    public void setInitialExecutionStatus(String initialExecutionStatus) { this.initialExecutionStatus = initialExecutionStatus; }

    public String getFinalExecutionStatus() { return finalExecutionStatus; }
    public void setFinalExecutionStatus(String finalExecutionStatus) { this.finalExecutionStatus = finalExecutionStatus; }

    public long getDurationMs() { return durationMs; }
    public void setDurationMs(long durationMs) { this.durationMs = durationMs; }

    public boolean isHealed() { return healed; }
    public void setHealed(boolean healed) { this.healed = healed; }

    public int getRepairedSteps() { return repairedSteps; }
    public void setRepairedSteps(int repairedSteps) { this.repairedSteps = repairedSteps; }

    public List<UiChangeDto> getDetectedInterfaceChanges() { return detectedInterfaceChanges; }
    public void setDetectedInterfaceChanges(List<UiChangeDto> detectedInterfaceChanges) { this.detectedInterfaceChanges = detectedInterfaceChanges; }

    public List<HealingAttemptDto> getHealingAttempts() { return healingAttempts; }
    public void setHealingAttempts(List<HealingAttemptDto> healingAttempts) { this.healingAttempts = healingAttempts; }

    public List<AssertionItem> getAssertionResults() { return assertionResults; }
    public void setAssertionResults(List<AssertionItem> assertionResults) { this.assertionResults = assertionResults; }

    public List<String> getRemainingRisks() { return remainingRisks; }
    public void setRemainingRisks(List<String> remainingRisks) { this.remainingRisks = remainingRisks; }

    public List<String> getMaintenanceSuggestions() { return maintenanceSuggestions; }
    public void setMaintenanceSuggestions(List<String> maintenanceSuggestions) { this.maintenanceSuggestions = maintenanceSuggestions; }

    public boolean isSimulated() { return isSimulated; }
    public void setSimulated(boolean simulated) { isSimulated = simulated; }
}
