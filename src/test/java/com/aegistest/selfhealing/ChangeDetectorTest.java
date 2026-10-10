package com.aegistest.selfhealing;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.dto.UiChangeDto;
import com.aegistest.selfhealing.healing.ChangeDetector;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class ChangeDetectorTest {

    private ChangeDetector detector;

    @BeforeEach
    void setUp() {
        detector = new ChangeDetector();
    }

    @Test
    void testDetectsSelectorRenamedAndContainerMoved() {
        PlannedAction failedAction = new PlannedAction(
                4,
                PlannedAction.ActionType.CLICK,
                "Button that submits checkout purchase",
                "#checkout-button",
                null
        );

        CandidateElementDto candidate = new CandidateElementDto();
        candidate.setSelector("button#place-order-cta");
        candidate.setText("Place My Order");

        List<UiChangeDto> changes = detector.detectChanges(failedAction, candidate, new PageSnapshot());

        assertFalse(changes.isEmpty());
        assertTrue(changes.stream().anyMatch(c -> "selector_renamed".equals(c.getType())));
        assertTrue(changes.stream().anyMatch(c -> "container_moved".equals(c.getType())));
    }
}
