package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "healing_attempts")
public class HealingAttemptEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "run_id", length = 64, nullable = false)
    private String runId;

    @Column(name = "step_id", length = 64, nullable = false)
    private String stepId;

    @Column(name = "step_number", nullable = false)
    private int stepNumber;

    @Column(name = "failed_selector", length = 512, nullable = false)
    private String failedSelector;

    @Column(name = "failure_reason", columnDefinition = "TEXT", nullable = false)
    private String failureReason;

    @Column(length = 64, nullable = false)
    private String strategy; // semantic_intent, visual_similarity, dom_heuristic, llm_synthesis

    @Column(name = "repaired_action", nullable = false)
    private String repairedAction;

    @Column(name = "repaired_selector", length = 512, nullable = false)
    private String repairedSelector;

    @Column(name = "confidence_score", nullable = false)
    private double confidenceScore;

    @Column(name = "duration_ms")
    private long durationMs = 0;

    @Column(name = "timestamp")
    private Instant timestamp = Instant.now();

    @Column(name = "candidates_json", columnDefinition = "MEDIUMTEXT")
    private String candidatesJson;

    @Column(name = "selected_candidate_json", columnDefinition = "MEDIUMTEXT")
    private String selectedCandidateJson;

    @Column(name = "attempt_status", length = 32)
    private String attemptStatus = "SUCCESS";

    @Column(name = "repair_explanation", columnDefinition = "TEXT")
    private String repairExplanation;

    public HealingAttemptEntity() {}

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public String getStepId() { return stepId; }
    public void setStepId(String stepId) { this.stepId = stepId; }

    public int getStepNumber() { return stepNumber; }
    public void setStepNumber(int stepNumber) { this.stepNumber = stepNumber; }

    public String getFailedSelector() { return failedSelector; }
    public void setFailedSelector(String failedSelector) { this.failedSelector = failedSelector; }

    public String getFailureReason() { return failureReason; }
    public void setFailureReason(String failureReason) { this.failureReason = failureReason; }

    public String getStrategy() { return strategy; }
    public void setStrategy(String strategy) { this.strategy = strategy; }

    public String getRepairedAction() { return repairedAction; }
    public void setRepairedAction(String repairedAction) { this.repairedAction = repairedAction; }

    public String getRepairedSelector() { return repairedSelector; }
    public void setRepairedSelector(String repairedSelector) { this.repairedSelector = repairedSelector; }

    public double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(double confidenceScore) { this.confidenceScore = confidenceScore; }

    public long getDurationMs() { return durationMs; }
    public void setDurationMs(long durationMs) { this.durationMs = durationMs; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

    public String getCandidatesJson() { return candidatesJson; }
    public void setCandidatesJson(String candidatesJson) { this.candidatesJson = candidatesJson; }

    public String getSelectedCandidateJson() { return selectedCandidateJson; }
    public void setSelectedCandidateJson(String selectedCandidateJson) { this.selectedCandidateJson = selectedCandidateJson; }

    public String getAttemptStatus() { return attemptStatus; }
    public void setAttemptStatus(String attemptStatus) { this.attemptStatus = attemptStatus; }

    public String getRepairExplanation() { return repairExplanation; }
    public void setRepairExplanation(String repairExplanation) { this.repairExplanation = repairExplanation; }
}
