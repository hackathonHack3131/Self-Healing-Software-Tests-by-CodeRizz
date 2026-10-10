package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "execution_steps")
public class ExecutionStepEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "run_id", length = 64, nullable = false)
    private String runId;

    @Column(name = "step_number", nullable = false)
    private int stepNumber;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "original_action", nullable = false)
    private String originalAction;

    @Column(name = "original_selector", length = 512)
    private String originalSelector;

    @Column(name = "repaired_action")
    private String repairedAction;

    @Column(name = "repaired_selector", length = 512)
    private String repairedSelector;

    @Column(length = 32, nullable = false)
    private String status; // pending, running, passed, failed, healing, healed

    @Column(name = "duration_ms")
    private long durationMs = 0;

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "screenshot_before", columnDefinition = "TEXT")
    private String screenshotBefore;

    @Column(name = "screenshot_after", columnDefinition = "TEXT")
    private String screenshotAfter;

    public ExecutionStepEntity() {}

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public int getStepNumber() { return stepNumber; }
    public void setStepNumber(int stepNumber) { this.stepNumber = stepNumber; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getOriginalAction() { return originalAction; }
    public void setOriginalAction(String originalAction) { this.originalAction = originalAction; }

    public String getOriginalSelector() { return originalSelector; }
    public void setOriginalSelector(String originalSelector) { this.originalSelector = originalSelector; }

    public String getRepairedAction() { return repairedAction; }
    public void setRepairedAction(String repairedAction) { this.repairedAction = repairedAction; }

    public String getRepairedSelector() { return repairedSelector; }
    public void setRepairedSelector(String repairedSelector) { this.repairedSelector = repairedSelector; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public long getDurationMs() { return durationMs; }
    public void setDurationMs(long durationMs) { this.durationMs = durationMs; }

    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

    public String getScreenshotBefore() { return screenshotBefore; }
    public void setScreenshotBefore(String screenshotBefore) { this.screenshotBefore = screenshotBefore; }

    public String getScreenshotAfter() { return screenshotAfter; }
    public void setScreenshotAfter(String screenshotAfter) { this.screenshotAfter = screenshotAfter; }
}
