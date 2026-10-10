package com.aegistest.selfhealing.healing;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.dto.UiChangeDto;

import java.util.ArrayList;
import java.util.List;

public class HealingResult {
    public enum Status {
        SUCCESS,
        AMBIGUOUS,
        UNSAFE,
        FAILED
    }

    private Status status;
    private CandidateElementDto selectedCandidate;
    private List<CandidateElementDto> allCandidates = new ArrayList<>();
    private String repairedSelector;
    private String repairedAction;
    private String strategy = "semantic_intent";
    private String explanation;
    private List<UiChangeDto> detectedChanges = new ArrayList<>();
    private double confidenceScore;

    public HealingResult() {}

    public Status getStatus() { return status; }
    public void setStatus(Status status) { this.status = status; }

    public CandidateElementDto getSelectedCandidate() { return selectedCandidate; }
    public void setSelectedCandidate(CandidateElementDto selectedCandidate) { this.selectedCandidate = selectedCandidate; }

    public List<CandidateElementDto> getAllCandidates() { return allCandidates; }
    public void setAllCandidates(List<CandidateElementDto> allCandidates) { this.allCandidates = allCandidates; }

    public String getRepairedSelector() { return repairedSelector; }
    public void setRepairedSelector(String repairedSelector) { this.repairedSelector = repairedSelector; }

    public String getRepairedAction() { return repairedAction; }
    public void setRepairedAction(String repairedAction) { this.repairedAction = repairedAction; }

    public String getStrategy() { return strategy; }
    public void setStrategy(String strategy) { this.strategy = strategy; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public List<UiChangeDto> getDetectedChanges() { return detectedChanges; }
    public void setDetectedChanges(List<UiChangeDto> detectedChanges) { this.detectedChanges = detectedChanges; }

    public double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(double confidenceScore) { this.confidenceScore = confidenceScore; }
}
