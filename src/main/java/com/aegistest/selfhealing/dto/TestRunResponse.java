package com.aegistest.selfhealing.dto;

import java.util.ArrayList;
import java.util.List;

public class TestRunResponse {
    private String id;
    private String testId;
    private String testName;
    private String targetUrl;
    private String intent;
    private String status;
    private int currentStepIndex;
    private int totalSteps;
    private List<TestStepDto> steps = new ArrayList<>();
    private String startedAt;
    private String completedAt;
    private Long durationMs;
    private String initialResult;
    private String finalResult;
    private int healingCount;
    private boolean isSimulated = false;
    private String currentScreenshot;
    private List<ConsoleLogDto> logs = new ArrayList<>();
    private List<UiChangeDto> detectedChanges = new ArrayList<>();
    private FinalVerificationDto finalVerification;

    public TestRunResponse() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTestId() { return testId; }
    public void setTestId(String testId) { this.testId = testId; }

    public String getTestName() { return testName; }
    public void setTestName(String testName) { this.testName = testName; }

    public String getTargetUrl() { return targetUrl; }
    public void setTargetUrl(String targetUrl) { this.targetUrl = targetUrl; }

    public String getIntent() { return intent; }
    public void setIntent(String intent) { this.intent = intent; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public int getCurrentStepIndex() { return currentStepIndex; }
    public void setCurrentStepIndex(int currentStepIndex) { this.currentStepIndex = currentStepIndex; }

    public int getTotalSteps() { return totalSteps; }
    public void setTotalSteps(int totalSteps) { this.totalSteps = totalSteps; }

    public List<TestStepDto> getSteps() { return steps; }
    public void setSteps(List<TestStepDto> steps) { this.steps = steps; }

    public String getStartedAt() { return startedAt; }
    public void setStartedAt(String startedAt) { this.startedAt = startedAt; }

    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }

    public Long getDurationMs() { return durationMs; }
    public void setDurationMs(Long durationMs) { this.durationMs = durationMs; }

    public String getInitialResult() { return initialResult; }
    public void setInitialResult(String initialResult) { this.initialResult = initialResult; }

    public String getFinalResult() { return finalResult; }
    public void setFinalResult(String finalResult) { this.finalResult = finalResult; }

    public int getHealingCount() { return healingCount; }
    public void setHealingCount(int healingCount) { this.healingCount = healingCount; }

    public boolean isSimulated() { return isSimulated; }
    public void setSimulated(boolean simulated) { isSimulated = simulated; }

    public String getCurrentScreenshot() { return currentScreenshot; }
    public void setCurrentScreenshot(String currentScreenshot) { this.currentScreenshot = currentScreenshot; }

    public List<ConsoleLogDto> getLogs() { return logs; }
    public void setLogs(List<ConsoleLogDto> logs) { this.logs = logs; }

    public List<UiChangeDto> getDetectedChanges() { return detectedChanges; }
    public void setDetectedChanges(List<UiChangeDto> detectedChanges) { this.detectedChanges = detectedChanges; }

    public FinalVerificationDto getFinalVerification() { return finalVerification; }
    public void setFinalVerification(FinalVerificationDto finalVerification) { this.finalVerification = finalVerification; }
}
