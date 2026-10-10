package com.aegistest.selfhealing.dto;

import java.util.Map;

public class ConsoleLogDto {
    private String id;
    private String timestamp;
    private String level; // info, warn, error, ai, success
    private String message;
    private Map<String, Object> details;

    public ConsoleLogDto() {}

    public ConsoleLogDto(String id, String timestamp, String level, String message) {
        this.id = id;
        this.timestamp = timestamp;
        this.level = level;
        this.message = message;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public String getLevel() { return level; }
    public void setLevel(String level) { this.level = level; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public Map<String, Object> getDetails() { return details; }
    public void setDetails(Map<String, Object> details) { this.details = details; }
}
