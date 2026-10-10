package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "execution_events")
public class ExecutionEventEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(name = "run_id", length = 64, nullable = false)
    private String runId;

    @Column(name = "event_type", length = 64, nullable = false)
    private String eventType;

    @Column(name = "payload_json", columnDefinition = "MEDIUMTEXT", nullable = false)
    private String payloadJson;

    @Column(name = "timestamp")
    private Instant timestamp = Instant.now();

    public ExecutionEventEntity() {}

    public ExecutionEventEntity(String id, String runId, String eventType, String payloadJson, Instant timestamp) {
        this.id = id;
        this.runId = runId;
        this.eventType = eventType;
        this.payloadJson = payloadJson;
        this.timestamp = timestamp;
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }

    public String getPayloadJson() { return payloadJson; }
    public void setPayloadJson(String payloadJson) { this.payloadJson = payloadJson; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }
}
