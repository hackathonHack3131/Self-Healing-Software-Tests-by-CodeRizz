package com.aegistest.selfhealing.entity;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "test_cases")
public class TestCaseEntity {

    @Id
    @Column(length = 64)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(name = "target_url", length = 1024, nullable = false)
    private String targetUrl;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String intent;

    @Column(length = 32)
    private String environment = "staging";

    @Column(length = 32)
    private String browser = "chromium";

    @Column(name = "self_healing_enabled")
    private boolean selfHealingEnabled = true;

    @Column(name = "max_healing_attempts")
    private int maxHealingAttempts = 3;

    @Column(name = "expected_outcome", columnDefinition = "TEXT")
    private String expectedOutcome;

    @Column(name = "created_at")
    private Instant createdAt = Instant.now();

    @Column(name = "last_run_at")
    private Instant lastRunAt;

    @Column(length = 32)
    private String status = "never_run";

    public TestCaseEntity() {}

    // Getters and Setters
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

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public Instant getLastRunAt() { return lastRunAt; }
    public void setLastRunAt(Instant lastRunAt) { this.lastRunAt = lastRunAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
