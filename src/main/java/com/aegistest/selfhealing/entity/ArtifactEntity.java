package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "artifacts")
public class ArtifactEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "run_id", length = 64, nullable = false)
    private String runId;

    @Column(name = "artifact_type", length = 64, nullable = false)
    private String artifactType; // screenshot, dom_dump, video, report_pdf

    @Column(name = "storage_path", length = 1024, nullable = false)
    private String storagePath;

    @Column(name = "created_at")
    private Instant createdAt = Instant.now();

    public ArtifactEntity() {}

    public ArtifactEntity(String id, String runId, String artifactType, String storagePath) {
        this.id = id;
        this.runId = runId;
        this.artifactType = artifactType;
        this.storagePath = storagePath;
        this.createdAt = Instant.now();
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public String getArtifactType() { return artifactType; }
    public void setArtifactType(String artifactType) { this.artifactType = artifactType; }

    public String getStoragePath() { return storagePath; }
    public void setStoragePath(String storagePath) { this.storagePath = storagePath; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
