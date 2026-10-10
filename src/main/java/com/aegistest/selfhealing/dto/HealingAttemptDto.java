package com.aegistest.selfhealing.dto;

import java.util.ArrayList;
import java.util.List;

public class HealingAttemptDto {
    private String id;
    private int stepNumber;
    private String failedSelector;
    private String failureReason;
    private String strategy;
    private List<CandidateElementDto> candidatesScored = new ArrayList<>();
    private CandidateElementDto selectedCandidate;
    private String repairedAction;
    private String repairedSelector;
    private double confidenceScore;
    private long durationMs;
    private String timestamp;

    public HealingAttemptDto() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public int getStepNumber() { return stepNumber; }
    public void setStepNumber(int stepNumber) { this.stepNumber = stepNumber; }

    public String getFailedSelector() { return failedSelector; }
    public void setFailedSelector(String failedSelector) { this.failedSelector = failedSelector; }

    public String getFailureReason() { return failureReason; }
    public void setFailureReason(String failureReason) { this.failureReason = failureReason; }

    public String getStrategy() { return strategy; }
    public void setStrategy(String strategy) { this.strategy = strategy; }

    public List<CandidateElementDto> getCandidatesScored() { return candidatesScored; }
    public void setCandidatesScored(List<CandidateElementDto> candidatesScored) { this.candidatesScored = candidatesScored; }

    public CandidateElementDto getSelectedCandidate() { return selectedCandidate; }
    public void setSelectedCandidate(CandidateElementDto selectedCandidate) { this.selectedCandidate = selectedCandidate; }

    public String getRepairedAction() { return repairedAction; }
    public void setRepairedAction(String repairedAction) { this.repairedAction = repairedAction; }

    public String getRepairedSelector() { return repairedSelector; }
    public void setRepairedSelector(String repairedSelector) { this.repairedSelector = repairedSelector; }

    public double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(double confidenceScore) { this.confidenceScore = confidenceScore; }

    public long getDurationMs() { return durationMs; }
    public void setDurationMs(long durationMs) { this.durationMs = durationMs; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
}
