package com.aegistest.selfhealing.dto;

public class FinalVerificationDto {
    private boolean verified;
    private String evidenceText;
    private String targetSelector;

    public FinalVerificationDto() {}

    public FinalVerificationDto(boolean verified, String evidenceText, String targetSelector) {
        this.verified = verified;
        this.evidenceText = evidenceText;
        this.targetSelector = targetSelector;
    }

    public boolean isVerified() { return verified; }
    public void setVerified(boolean verified) { this.verified = verified; }

    public String getEvidenceText() { return evidenceText; }
    public void setEvidenceText(String evidenceText) { this.evidenceText = evidenceText; }

    public String getTargetSelector() { return targetSelector; }
    public void setTargetSelector(String targetSelector) { this.targetSelector = targetSelector; }
}
