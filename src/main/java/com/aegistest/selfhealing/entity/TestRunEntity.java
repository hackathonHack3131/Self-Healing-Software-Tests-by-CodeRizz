package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "test_runs")
public class TestRunEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "test_id", length = 64, nullable = false)
    private String testId;

    @Column(name = "test_name", nullable = false)
    private String testName;

    @Column(name = "target_url", length = 1024, nullable = false)
    private String targetUrl;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String intent;

    @Column(length = 32, nullable = false)
    private String status; // queued, running, detecting_change, healing, verifying, passed, failed, cancelled

    @Column(name = "current_step_index")
    private int currentStepIndex = 0;

    @Column(name = "total_steps")
    private int totalSteps = 0;

    @Column(name = "started_at")
    private Instant startedAt = Instant.now();

    @Column(name = "completed_at")
    private Instant completedAt;

    @Column(name = "duration_ms")
    private long durationMs = 0;

    @Column(name = "initial_result", length = 32)
    private String initialResult; // passed, failed

    @Column(name = "final_result", length = 32)
    private String finalResult; // passed, failed, healed

    @Column(name = "healing_count")
    private int healingCount = 0;

    @Column(name = "is_simulated")
    private boolean isSimulated = false;

    @Column(name = "current_screenshot", columnDefinition = "TEXT")
    private String currentScreenshot;

    @Column(name = "final_verified")
    private boolean finalVerified = false;

    @Column(name = "final_evidence_text", columnDefinition = "TEXT")
    private String finalEvidenceText;

    @Column(name = "final_target_selector")
    private String finalTargetSelector;

    @Column(name = "error_summary", columnDefinition = "TEXT")
    private String errorSummary;

    public TestRunEntity() {}

    // Getters and Setters
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

    public Instant getStartedAt() { return startedAt; }
    public void setStartedAt(Instant startedAt) { this.startedAt = startedAt; }

    public Instant getCompletedAt() { return completedAt; }
    public void setCompletedAt(Instant completedAt) { this.completedAt = completedAt; }

    public long getDurationMs() { return durationMs; }
    public void setDurationMs(long durationMs) { this.durationMs = durationMs; }

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

    public boolean isFinalVerified() { return finalVerified; }
    public void setFinalVerified(boolean finalVerified) { this.finalVerified = finalVerified; }

    public String getFinalEvidenceText() { return finalEvidenceText; }
    public void setFinalEvidenceText(String finalEvidenceText) { this.finalEvidenceText = finalEvidenceText; }

    public String getFinalTargetSelector() { return finalTargetSelector; }
    public void setFinalTargetSelector(String finalTargetSelector) { this.finalTargetSelector = finalTargetSelector; }

    public String getErrorSummary() { return errorSummary; }
    public void setErrorSummary(String errorSummary) { this.errorSummary = errorSummary; }
}
