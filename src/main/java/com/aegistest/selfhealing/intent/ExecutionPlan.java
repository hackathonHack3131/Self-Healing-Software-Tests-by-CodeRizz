package com.aegistest.selfhealing.intent;

import java.util.ArrayList;
import java.util.List;

public class ExecutionPlan {
    private String intent;
    private List<String> preconditions = new ArrayList<>();
    private List<PlannedAction> steps = new ArrayList<>();
    private List<PlannedAction> assertions = new ArrayList<>();
    private String reasoningMode = "RULE_BASED"; // RULE_BASED or AI_ASSISTED

    public ExecutionPlan() {}

    public ExecutionPlan(String intent) {
        this.intent = intent;
    }

    public String getIntent() { return intent; }
    public void setIntent(String intent) { this.intent = intent; }

    public List<String> getPreconditions() { return preconditions; }
    public void setPreconditions(List<String> preconditions) { this.preconditions = preconditions; }

    public List<PlannedAction> getSteps() { return steps; }
    public void setSteps(List<PlannedAction> steps) { this.steps = steps; }

    public List<PlannedAction> getAssertions() { return assertions; }
    public void setAssertions(List<PlannedAction> assertions) { this.assertions = assertions; }

    public String getReasoningMode() { return reasoningMode; }
    public void setReasoningMode(String reasoningMode) { this.reasoningMode = reasoningMode; }
}
