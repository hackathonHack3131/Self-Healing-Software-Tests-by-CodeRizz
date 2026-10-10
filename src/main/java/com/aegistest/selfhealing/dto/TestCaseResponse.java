package com.aegistest.selfhealing.dto;

public class TestCaseResponse {
    private String id;
    private String name;
    private String targetUrl;
    private String intent;
    private String environment;
    private String browser;
    private boolean selfHealingEnabled;
    private int maxHealingAttempts;
    private String expectedOutcome;
    private String createdAt;
    private String lastRunAt;
    private String status;

    public TestCaseResponse() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getTargetUrl() { return targetUrl; }
    public void setTargetUrl(String targetUrl) { this.targetUrl = targetUrl; }

    public String getIntent() { return intent; }
    public void setIntent(String intent) { this.intent = intent; }

    public String getEnvironment() { return environment; }
    public void setEnvironment(String environment) { this.environment = environment; }

    public String getBrowser() { return browser; }
    public void setBrowser(String browser) { this.browser = browser; }

    public boolean isSelfHealingEnabled() { return selfHealingEnabled; }
    public void setSelfHealingEnabled(boolean selfHealingEnabled) { this.selfHealingEnabled = selfHealingEnabled; }

    public int getMaxHealingAttempts() { return maxHealingAttempts; }
    public void setMaxHealingAttempts(int maxHealingAttempts) { this.maxHealingAttempts = maxHealingAttempts; }

    public String getExpectedOutcome() { return expectedOutcome; }
    public void setExpectedOutcome(String expectedOutcome) { this.expectedOutcome = expectedOutcome; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getLastRunAt() { return lastRunAt; }
    public void setLastRunAt(String lastRunAt) { this.lastRunAt = lastRunAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
