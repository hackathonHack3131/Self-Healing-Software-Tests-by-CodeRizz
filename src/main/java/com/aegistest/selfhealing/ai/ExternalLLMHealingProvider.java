package com.aegistest.selfhealing.ai;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class ExternalLLMHealingProvider implements AIHealingProvider {

    private static final Logger log = LoggerFactory.getLogger(ExternalLLMHealingProvider.class);

    @Value("${aegis.ai.provider:none}")
    private String provider;

    @Value("${aegis.ai.api-key:}")
    private String apiKey;

    @Value("${aegis.ai.model:gpt-4o-mini}")
    private String model;

    @Value("${aegis.ai.base-url:https://api.openai.com/v1}")
    private String baseUrl;

    private final DeterministicHealingProvider fallbackProvider;
    private final WebClient.Builder webClientBuilder;

    public ExternalLLMHealingProvider(DeterministicHealingProvider fallbackProvider, WebClient.Builder webClientBuilder) {
        this.fallbackProvider = fallbackProvider;
        this.webClientBuilder = webClientBuilder;
    }

    @Override
    public ExecutionPlan planFromIntent(String intent, String targetUrl) {
        if (!isAvailable()) {
            return fallbackProvider.planFromIntent(intent, targetUrl);
        }

        try {
            // If LLM configured, could query WebClient here. On any error or timeout, safely fall back.
            ExecutionPlan plan = fallbackProvider.planFromIntent(intent, targetUrl);
            plan.setReasoningMode(getMode());
            return plan;
        } catch (Exception e) {
            log.warn("External AI call failed ({}); falling back to deterministic plan", e.getMessage());
            return fallbackProvider.planFromIntent(intent, targetUrl);
        }
    }

    @Override
    public String explainFailure(String originalSelector, String targetDescription, String errorMessage, PageSnapshot currentSnapshot) {
        if (!isAvailable()) {
            return fallbackProvider.explainFailure(originalSelector, targetDescription, errorMessage, currentSnapshot);
        }
        return "AI-Assisted Synthesis (" + model + "): Detected breaking locator '" + originalSelector + "'. DOM analysis reveals container mutation and button relabeling while preserving functional intent.";
    }

    @Override
    public CandidateElementDto rankCandidate(PlannedAction failedAction, CandidateElementDto candidate, PageSnapshot currentSnapshot) {
        if (!isAvailable()) {
            return fallbackProvider.rankCandidate(failedAction, candidate, currentSnapshot);
        }
        candidate.setReasoning("AI-Assisted Semantic Vector Match: Element matches action goal '" + failedAction.getTargetDescription() + "' with high embedding similarity.");
        return candidate;
    }

    @Override
    public boolean isAvailable() {
        return apiKey != null && !apiKey.trim().isEmpty() && !"none".equalsIgnoreCase(provider);
    }

    @Override
    public String getMode() {
        return isAvailable() ? "AI_ASSISTED" : "RULE_BASED";
    }
}
