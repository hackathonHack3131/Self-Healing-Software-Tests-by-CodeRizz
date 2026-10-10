package com.aegistest.selfhealing.planning;

import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.springframework.stereotype.Component;

import java.util.EnumSet;
import java.util.Set;

@Component
public class PlanValidator {

    private static final Set<PlannedAction.ActionType> ALLOWED_ACTIONS = EnumSet.allOf(PlannedAction.ActionType.class);

    /**
     * Validates an execution plan against strict security and schema criteria.
     */
    public void validatePlan(ExecutionPlan plan) {
        if (plan == null) {
            throw new IllegalArgumentException("Execution plan cannot be null");
        }
        if (plan.getIntent() == null || plan.getIntent().trim().isEmpty()) {
            throw new IllegalArgumentException("Execution plan must contain a non-empty natural language intent");
        }
        if (plan.getSteps() == null || plan.getSteps().isEmpty()) {
            throw new IllegalArgumentException("Execution plan must contain at least one execution step");
        }

        for (PlannedAction step : plan.getSteps()) {
            if (step.getActionType() == null || !ALLOWED_ACTIONS.contains(step.getActionType())) {
                throw new SecurityException("Action type '" + step.getActionType() + "' is not in the allowed action allowlist");
            }
            if (step.getTargetDescription() == null || step.getTargetDescription().trim().isEmpty()) {
                throw new IllegalArgumentException("Step target description cannot be empty");
            }

            // Check for dangerous code injection attempts in values or locators
            String raw = (step.getLocatorHint() != null ? step.getLocatorHint() : "") + " " +
                         (step.getValue() != null ? step.getValue() : "");
            if (raw.matches("(?i).*(eval\\(|java\\.lang|Runtime\\.getRuntime|ProcessBuilder|<script).*")) {
                throw new SecurityException("Potential malicious script injection detected in plan step");
            }
        }
    }
}
