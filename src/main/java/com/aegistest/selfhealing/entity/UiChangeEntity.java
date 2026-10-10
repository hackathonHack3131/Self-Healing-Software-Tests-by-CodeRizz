package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "ui_changes")
public class UiChangeEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "run_id", length = 64)
    private String runId;

    @Column(name = "element_description", nullable = false)
    private String elementDescription;

    @Column(name = "change_type", length = 64, nullable = false)
    private String changeType; // selector_renamed, container_moved, dom_restructured, styling_changed

    @Column(name = "previous_dom_snippet", columnDefinition = "TEXT")
    private String previousDomSnippet;

    @Column(name = "new_dom_snippet", columnDefinition = "TEXT")
    private String newDomSnippet;

    @Column(name = "impact_score", length = 32)
    private String impactScore = "medium"; // low, medium, high

    @Column(name = "detected_at")
    private Instant detectedAt = Instant.now();

    public UiChangeEntity() {}

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public String getElementDescription() { return elementDescription; }
    public void setElementDescription(String elementDescription) { this.elementDescription = elementDescription; }

    public String getChangeType() { return changeType; }
    public void setChangeType(String changeType) { this.changeType = changeType; }

    public String getPreviousDomSnippet() { return previousDomSnippet; }
    public void setPreviousDomSnippet(String previousDomSnippet) { this.previousDomSnippet = previousDomSnippet; }

    public String getNewDomSnippet() { return newDomSnippet; }
    public void setNewDomSnippet(String newDomSnippet) { this.newDomSnippet = newDomSnippet; }

    public String getImpactScore() { return impactScore; }
    public void setImpactScore(String impactScore) { this.impactScore = impactScore; }

    public Instant getDetectedAt() { return detectedAt; }
    public void setDetectedAt(Instant detectedAt) { this.detectedAt = detectedAt; }
}
