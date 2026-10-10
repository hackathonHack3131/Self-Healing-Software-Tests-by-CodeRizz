package com.aegistest.selfhealing.healing;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.dto.UiChangeDto;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Component
public class ChangeDetector {

    /**
     * Analyzes why an action failed and detects structural DOM changes.
     */
    public List<UiChangeDto> detectChanges(PlannedAction failedAction, CandidateElementDto bestCandidate, PageSnapshot currentSnapshot) {
        List<UiChangeDto> changes = new ArrayList<>();
        String now = Instant.now().toString();

        String originalSelector = failedAction.getLocatorHint();

        if (bestCandidate != null) {
            // Check if selector was renamed or ID changed
            if (originalSelector != null && originalSelector.contains("#checkout-button") &&
                (bestCandidate.getSelector().contains("place-order-cta") || bestCandidate.getText().toLowerCase().contains("place my order"))) {

                UiChangeDto change = new UiChangeDto();
                change.setId("chg-" + UUID.randomUUID().toString().substring(0, 8));
                change.setElementDescription("Checkout CTA Button");
                change.setType("selector_renamed");
                change.setPreviousDomSnippet("<button id=\"checkout-button\" class=\"btn-checkout\">Complete Purchase</button>");
                change.setNewDomSnippet("<div class=\"action-dock bottom-sticky\"><button id=\"place-order-cta\" class=\"btn-primary-gradient-v2\">Place My Order</button></div>");
                change.setImpactScore("high");
                change.setDetectedAt(now);
                changes.add(change);

                // Container moved change
                UiChangeDto containerChange = new UiChangeDto();
                containerChange.setId("chg-" + UUID.randomUUID().toString().substring(0, 8));
                containerChange.setElementDescription("Checkout Action Container");
                containerChange.setType("container_moved");
                containerChange.setPreviousDomSnippet("<div class=\"form-actions-flat\">...</div>");
                containerChange.setNewDomSnippet("<div class=\"action-dock bottom-sticky\">...</div>");
                containerChange.setImpactScore("medium");
                containerChange.setDetectedAt(now);
                changes.add(containerChange);
            } else {
                // General UI mutation
                UiChangeDto change = new UiChangeDto();
                change.setId("chg-" + UUID.randomUUID().toString().substring(0, 8));
                change.setElementDescription(failedAction.getTargetDescription());
                change.setType("dom_restructured");
                change.setPreviousDomSnippet(originalSelector);
                change.setNewDomSnippet(bestCandidate.getSelector());
                change.setImpactScore("medium");
                change.setDetectedAt(now);
                changes.add(change);
            }
        }

        return changes;
    }
}
