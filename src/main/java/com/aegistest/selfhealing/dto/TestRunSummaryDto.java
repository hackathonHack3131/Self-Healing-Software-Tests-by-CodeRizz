package com.aegistest.selfhealing.dto;

public class TestRunSummaryDto {
    private String id;
    private String testId;
    private String testName;
    private String targetApp;
    private String executedAt;
    private String durationFormatted;
    private String initialResult; // passed, failed
    private String finalResult; // passed, failed, healed
    private String healingStatus; // healed, unhealed, none_needed
    private int repairedStepsCount;

    public TestRunSummaryDto() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTestId() { return testId; }
    public void setTestId(String testId) { this.testId = testId; }

    public String getTestName() { return testName; }
    public void setTestName(String testName) { this.testName = testName; }

    public String getTargetApp() { return targetApp; }
    public void setTargetApp(String targetApp) { this.targetApp = targetApp; }

    public String getExecutedAt() { return executedAt; }
    public void setExecutedAt(String executedAt) { this.executedAt = executedAt; }

    public String getDurationFormatted() { return durationFormatted; }
    public void setDurationFormatted(String durationFormatted) { this.durationFormatted = durationFormatted; }

    public String getInitialResult() { return initialResult; }
    public void setInitialResult(String initialResult) { this.initialResult = initialResult; }

    public String getFinalResult() { return finalResult; }
    public void setFinalResult(String finalResult) { this.finalResult = finalResult; }

    public String getHealingStatus() { return healingStatus; }
    public void setHealingStatus(String healingStatus) { this.healingStatus = healingStatus; }

    public int getRepairedStepsCount() { return repairedStepsCount; }
    public void setRepairedStepsCount(int repairedStepsCount) { this.repairedStepsCount = repairedStepsCount; }
}
