package com.aegistest.selfhealing.intent;

import com.aegistest.selfhealing.ai.AIHealingProvider;
import com.aegistest.selfhealing.ai.ExternalLLMHealingProvider;
import com.aegistest.selfhealing.planning.PlanValidator;
import org.springframework.stereotype.Component;

@Component
public class IntentParser {

    private final ExternalLLMHealingProvider aiProvider;
    private final PlanValidator planValidator;

    public IntentParser(ExternalLLMHealingProvider aiProvider, PlanValidator planValidator) {
        this.aiProvider = aiProvider;
        this.planValidator = planValidator;
    }

    /**
     * Parses intent into an ExecutionPlan and validates it against allowlists and security rules.
     */
    public ExecutionPlan parseAndValidate(String intent, String targetUrl) {
        ExecutionPlan plan = aiProvider.planFromIntent(intent, targetUrl);
        planValidator.validatePlan(plan);
        return plan;
    }
}
