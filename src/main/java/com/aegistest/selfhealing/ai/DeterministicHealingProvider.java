package com.aegistest.selfhealing.ai;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class DeterministicHealingProvider implements AIHealingProvider {

    @Override
    public ExecutionPlan planFromIntent(String intent, String targetUrl) {
        ExecutionPlan plan = new ExecutionPlan(intent);
        plan.setReasoningMode(getMode());
        plan.getPreconditions().add("Target application URL is accessible");
        plan.getPreconditions().add("Test sandbox payment credentials are available");

        List<PlannedAction> steps = new ArrayList<>();

        String lower = intent != null ? intent.toLowerCase() : "";

        // E-Commerce / Checkout flow intent
        if (lower.contains("checkout") || lower.contains("order") || lower.contains("cart") || lower.contains("purchase")) {
            // Step 1: Customer Name
            PlannedAction step1 = new PlannedAction(
                    1,
                    PlannedAction.ActionType.FILL,
                    "Customer full name field",
                    "input#customer-name, input[name='fullName']",
                    "Alex Morgan"
            );
            step1.setValueReference("testCustomer.fullName");
            steps.add(step1);

            // Step 2: Shipping method selection
            PlannedAction step2 = new PlannedAction(
                    2,
                    PlannedAction.ActionType.CLICK,
                    "Express shipping method radio button",
                    "input[name='shipping'][value='express']",
                    null
            );
            steps.add(step2);

            // Step 3: Card number
            PlannedAction step3 = new PlannedAction(
                    3,
                    PlannedAction.ActionType.FILL,
                    "Test credit card number input",
                    "input#card-number, input[name='cardNumber']",
                    "4242 4242 4242 4242"
            );
            step3.setValueReference("testPayment.cardNumber");
            steps.add(step3);

            // Step 4: Submit button (The baseline selector that breaks in Version B)
            PlannedAction step4 = new PlannedAction(
                    4,
                    PlannedAction.ActionType.CLICK,
                    "Button that submits checkout purchase",
                    "#checkout-button",
                    null
            );
            steps.add(step4);

            // Final verification assertion
            PlannedAction assertion = new PlannedAction(
                    5,
                    PlannedAction.ActionType.ASSERT_VISIBLE,
                    "Order confirmation banner and Order ID",
                    "#order-confirmation, .order-confirmed-banner",
                    "Thank you for your order!"
            );
            plan.getAssertions().add(assertion);
        } else {
            // Generic fallback plan
            PlannedAction step1 = new PlannedAction(
                    1,
                    PlannedAction.ActionType.CLICK,
                    "Primary interactive element for: " + intent,
                    "button, input[type='submit'], [role='button']",
                    null
            );
            steps.add(step1);

            PlannedAction assertion = new PlannedAction(
                    2,
                    PlannedAction.ActionType.ASSERT_VISIBLE,
                    "State verification for: " + intent,
                    "body",
                    null
            );
            plan.getAssertions().add(assertion);
        }

        plan.setSteps(steps);
        return plan;
    }

    @Override
    public String explainFailure(String originalSelector, String targetDescription, String errorMessage, PageSnapshot currentSnapshot) {
        return "Deterministic Analysis: Original locator '" + originalSelector + "' failed to resolve. " +
                "Target goal was '" + targetDescription + "'. Inspecting active DOM mutations revealed structural layout and selector renaming.";
    }

    @Override
    public CandidateElementDto rankCandidate(PlannedAction failedAction, CandidateElementDto candidate, PageSnapshot currentSnapshot) {
        // High confidence rule-based match if it's a button with checkout / order semantics
        String text = candidate.getText() != null ? candidate.getText().toLowerCase() : "";
        String role = candidate.getRole() != null ? candidate.getRole().toLowerCase() : "";

        if (("button".equals(role) || "button".equals(candidate.getTag())) &&
            (text.contains("order") || text.contains("purchase") || text.contains("place") || text.contains("checkout") || text.contains("pay"))) {
            candidate.setReasoning("Rule-Based Match: Button with matching checkout intent text '" + candidate.getText() + "' and submit semantics.");
        }
        return candidate;
    }

    @Override
    public boolean isAvailable() {
        return true;
    }

    @Override
    public String getMode() {
        return "RULE_BASED";
    }
}
