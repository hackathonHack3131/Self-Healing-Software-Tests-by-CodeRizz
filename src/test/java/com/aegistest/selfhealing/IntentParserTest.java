package com.aegistest.selfhealing;

import com.aegistest.selfhealing.ai.DeterministicHealingProvider;
import com.aegistest.selfhealing.ai.ExternalLLMHealingProvider;
import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.IntentParser;
import com.aegistest.selfhealing.intent.PlannedAction;
import com.aegistest.selfhealing.planning.PlanValidator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.web.reactive.function.client.WebClient;

import static org.junit.jupiter.api.Assertions.*;

class IntentParserTest {

    private IntentParser intentParser;
    private PlanValidator planValidator;

    @BeforeEach
    void setUp() {
        DeterministicHealingProvider fallback = new DeterministicHealingProvider();
        ExternalLLMHealingProvider llmProvider = new ExternalLLMHealingProvider(fallback, WebClient.builder());
        planValidator = new PlanValidator();
        intentParser = new IntentParser(llmProvider, planValidator);
    }

    @Test
    void testIntentParsingReturnsValidPlan() {
        String intent = "Complete checkout with a valid credit card and confirm the order.";
        ExecutionPlan plan = intentParser.parseAndValidate(intent, "http://localhost:5173");

        assertNotNull(plan);
        assertEquals(intent, plan.getIntent());
        assertFalse(plan.getSteps().isEmpty(), "Plan should contain execution steps");
        assertFalse(plan.getAssertions().isEmpty(), "Plan should contain verification assertions");

        // Verify checkout flow steps
        assertTrue(plan.getSteps().stream().anyMatch(s -> s.getActionType() == PlannedAction.ActionType.FILL));
        assertTrue(plan.getSteps().stream().anyMatch(s -> s.getActionType() == PlannedAction.ActionType.CLICK));
        assertEquals("RULE_BASED", plan.getReasoningMode());
    }

    @Test
    void testInvalidActionIsRejected() {
        ExecutionPlan invalidPlan = new ExecutionPlan("Malicious intent");
        PlannedAction badAction = new PlannedAction();
        badAction.setTargetDescription("Execute shell script");
        badAction.setValue("java.lang.Runtime.getRuntime().exec('rm -rf /')");
        invalidPlan.getSteps().add(badAction);

        assertThrows(Exception.class, () -> planValidator.validatePlan(invalidPlan));
    }

    @Test
    void testDisconnectedAIProviderUsesDeterministicEngine() {
        // Disconnected AI provider (no API key configured)
        String intent = "Purchase items in cart";
        ExecutionPlan plan = intentParser.parseAndValidate(intent, "http://localhost:8000/demo/index.html");

        assertNotNull(plan);
        assertEquals("RULE_BASED", plan.getReasoningMode());
        assertTrue(plan.getSteps().size() >= 3);
    }
}
