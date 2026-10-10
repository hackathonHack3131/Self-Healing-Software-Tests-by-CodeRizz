package com.aegistest.selfhealing.ai;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.PlannedAction;

import java.util.List;

public interface AIHealingProvider {

    /**
     * Decomposes a natural language intent into a structured, executable plan.
     */
    ExecutionPlan planFromIntent(String intent, String targetUrl);

    /**
     * Synthesizes reasoning or explanations for a detected UI change or failure.
     */
    String explainFailure(String originalSelector, String targetDescription, String errorMessage, PageSnapshot currentSnapshot);

    /**
     * Re-scores or reasons about alternative candidate elements for healing.
     */
    CandidateElementDto rankCandidate(PlannedAction failedAction, CandidateElementDto candidate, PageSnapshot currentSnapshot);

    /**
     * Indicates whether the external AI provider is connected and available.
     */
    boolean isAvailable();

    /**
     * Provider mode identifier: RULE_BASED or AI_ASSISTED.
     */
    String getMode();
}
