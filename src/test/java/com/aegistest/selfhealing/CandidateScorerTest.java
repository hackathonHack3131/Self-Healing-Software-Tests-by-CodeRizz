package com.aegistest.selfhealing;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.healing.CandidateScorer;
import com.aegistest.selfhealing.inspection.InspectedElement;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CandidateScorerTest {

    private CandidateScorer scorer;

    @BeforeEach
    void setUp() {
        scorer = new CandidateScorer();
    }

    @Test
    void testScorerIdentifiesRenamedCheckoutButtonWithHighConfidence() {
        PlannedAction failedAction = new PlannedAction(
                4,
                PlannedAction.ActionType.CLICK,
                "Button that submits checkout purchase",
                "#checkout-button",
                null
        );

        // Version B Renamed element: "Place My Order" button inside action-dock
        InspectedElement candidate = new InspectedElement();
        candidate.setTag("button");
        candidate.setRole("button");
        candidate.setVisibleText("Place My Order");
        candidate.setAccessibleName("Place My Order");
        candidate.setPrimaryLocator("button#place-order-cta");
        candidate.setContainerClass("action-dock bottom-sticky");
        candidate.setParentTag("div");
        candidate.setVisible(true);
        candidate.setEnabled(true);

        CandidateElementDto scored = scorer.scoreCandidate(failedAction, candidate, 1);

        assertNotNull(scored);
        assertTrue(scored.getConfidence() >= 0.85, "Expected high confidence score for renamed submit button, got: " + scored.getConfidence());
        assertTrue(scored.getMatchBreakdown().getSemanticIntent() > 0.8);
        assertTrue(scored.getMatchBreakdown().getTextSimilarity() > 0.5);
        assertTrue(scored.getReasoning().contains("High Confidence"));
    }

    @Test
    void testScorerRejectsIrrelevantElements() {
        PlannedAction failedAction = new PlannedAction(
                4,
                PlannedAction.ActionType.CLICK,
                "Button that submits checkout purchase",
                "#checkout-button",
                null
        );

        // Irrelevant candidate: footer terms link
        InspectedElement candidate = new InspectedElement();
        candidate.setTag("a");
        candidate.setRole("link");
        candidate.setVisibleText("Terms of Service");
        candidate.setPrimaryLocator("a.footer-link");
        candidate.setVisible(true);
        candidate.setEnabled(true);

        CandidateElementDto scored = scorer.scoreCandidate(failedAction, candidate, 2);

        assertNotNull(scored);
        assertTrue(scored.getConfidence() < 0.60, "Irrelevant link should have low confidence score, got: " + scored.getConfidence());
    }
}
