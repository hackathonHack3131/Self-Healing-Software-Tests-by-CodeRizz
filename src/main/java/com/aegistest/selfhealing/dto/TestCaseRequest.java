package com.aegistest.selfhealing.dto;

import jakarta.validation.constraints.NotBlank;

public class TestCaseRequest {
    private String id;
    private String name;

    @NotBlank(message = "targetUrl must not be blank")
    private String targetUrl;

    @NotBlank(message = "intent must not be blank")
    private String intent;

    private String environment = "staging";
    private String browser = "chromium";
    private Boolean selfHealingEnabled = true;
    private Integer maxHealingAttempts = 3;
    private String expectedOutcome;

    public TestCaseRequest() {}

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

    public Boolean getSelfHealingEnabled() { return selfHealingEnabled; }
    public void setSelfHealingEnabled(Boolean selfHealingEnabled) { this.selfHealingEnabled = selfHealingEnabled; }

    public Integer getMaxHealingAttempts() { return maxHealingAttempts; }
    public void setMaxHealingAttempts(Integer maxHealingAttempts) { this.maxHealingAttempts = maxHealingAttempts; }

    public String getExpectedOutcome() { return expectedOutcome; }
    public void setExpectedOutcome(String expectedOutcome) { this.expectedOutcome = expectedOutcome; }
}
