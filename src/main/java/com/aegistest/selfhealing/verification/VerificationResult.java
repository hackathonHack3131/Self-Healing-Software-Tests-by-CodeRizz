package com.aegistest.selfhealing.verification;

public class VerificationResult {
    private boolean verified;
    private String evidenceText;
    private String targetSelector;
    private String details;

    public VerificationResult() {}

    public VerificationResult(boolean verified, String evidenceText, String targetSelector, String details) {
        this.verified = verified;
        this.evidenceText = evidenceText;
        this.targetSelector = targetSelector;
        this.details = details;
    }

    public boolean isVerified() { return verified; }
    public void setVerified(boolean verified) { this.verified = verified; }

    public String getEvidenceText() { return evidenceText; }
    public void setEvidenceText(String evidenceText) { this.evidenceText = evidenceText; }

    public String getTargetSelector() { return targetSelector; }
    public void setTargetSelector(String targetSelector) { this.targetSelector = targetSelector; }

    public String getDetails() { return details; }
    public void setDetails(String details) { this.details = details; }
}
