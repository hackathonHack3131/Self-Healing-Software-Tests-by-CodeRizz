package com.aegistest.selfhealing.dto;

public class TestStepDto {
    private String id;
    private int stepNumber;
    private String description;
    private String originalAction;
    private String originalSelector;
    private String status; // pending, running, passed, failed, healing, healed
    private Long durationMs;
    private String error;
    private HealingAttemptDto healingAttempt;
    private String screenshotBefore;
    private String screenshotAfter;

    public TestStepDto() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public int getStepNumber() { return stepNumber; }
    public void setStepNumber(int stepNumber) { this.stepNumber = stepNumber; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getOriginalAction() { return originalAction; }
    public void setOriginalAction(String originalAction) { this.originalAction = originalAction; }

    public String getOriginalSelector() { return originalSelector; }
    public void setOriginalSelector(String originalSelector) { this.originalSelector = originalSelector; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Long getDurationMs() { return durationMs; }
    public void setDurationMs(Long durationMs) { this.durationMs = durationMs; }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public HealingAttemptDto getHealingAttempt() { return healingAttempt; }
    public void setHealingAttempt(HealingAttemptDto healingAttempt) { this.healingAttempt = healingAttempt; }

    public String getScreenshotBefore() { return screenshotBefore; }
    public void setScreenshotBefore(String screenshotBefore) { this.screenshotBefore = screenshotBefore; }

    public String getScreenshotAfter() { return screenshotAfter; }
    public void setScreenshotAfter(String screenshotAfter) { this.screenshotAfter = screenshotAfter; }
}
