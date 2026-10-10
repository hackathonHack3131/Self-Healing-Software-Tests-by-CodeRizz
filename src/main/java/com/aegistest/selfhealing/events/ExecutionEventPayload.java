package com.aegistest.selfhealing.events;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

public class ExecutionEventPayload {
    private String runId;
    private String eventType;
    private String timestamp;
    private Map<String, Object> data = new HashMap<>();

    public ExecutionEventPayload() {
        this.timestamp = Instant.now().toString();
    }

    public ExecutionEventPayload(String runId, String eventType) {
        this.runId = runId;
        this.eventType = eventType;
        this.timestamp = Instant.now().toString();
    }

    public ExecutionEventPayload with(String key, Object value) {
        this.data.put(key, value);
        return this;
    }

    public String getRunId() { return runId; }
    public void setRunId(String runId) { this.runId = runId; }

    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public Map<String, Object> getData() { return data; }
    public void setData(Map<String, Object> data) { this.data = data; }
}
