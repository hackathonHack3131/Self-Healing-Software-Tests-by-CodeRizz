package com.aegistest.selfhealing.dto;

public class UiChangeDto {
    private String id;
    private String elementDescription;
    private String type; // selector_renamed, container_moved, dom_restructured, styling_changed
    private String previousDomSnippet;
    private String newDomSnippet;
    private String impactScore; // low, medium, high
    private String detectedAt;

    public UiChangeDto() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getElementDescription() { return elementDescription; }
    public void setElementDescription(String elementDescription) { this.elementDescription = elementDescription; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getPreviousDomSnippet() { return previousDomSnippet; }
    public void setPreviousDomSnippet(String previousDomSnippet) { this.previousDomSnippet = previousDomSnippet; }

    public String getNewDomSnippet() { return newDomSnippet; }
    public void setNewDomSnippet(String newDomSnippet) { this.newDomSnippet = newDomSnippet; }

    public String getImpactScore() { return impactScore; }
    public void setImpactScore(String impactScore) { this.impactScore = impactScore; }

    public String getDetectedAt() { return detectedAt; }
    public void setDetectedAt(String detectedAt) { this.detectedAt = detectedAt; }
}
