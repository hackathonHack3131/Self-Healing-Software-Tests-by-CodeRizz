package com.aegistest.selfhealing.healing;

import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.inspection.InspectedElement;
import com.aegistest.selfhealing.intent.PlannedAction;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

@Component
public class CandidateScorer {

    private static final Set<String> CHECKOUT_SUBMIT_TOKENS = new HashSet<>(Arrays.asList(
            "checkout", "order", "place", "purchase", "complete", "pay", "submit", "buy", "confirm"
    ));

    /**
     * Scores an inspected element against the failed action intent.
     * Produces a normalized confidence score (0.0 to 1.0) and match breakdown.
     */
    public CandidateElementDto scoreCandidate(PlannedAction failedAction, InspectedElement element, int candidateIndex) {
        CandidateElementDto dto = new CandidateElementDto();
        dto.setId("candidate-" + candidateIndex);
        dto.setTag(element.getTag());
        dto.setRole(element.getRole());
        dto.setText(element.getVisibleText());
        dto.setSelector(element.getPrimaryLocator());
        dto.setAttributes(element.getAttributes());

        // Calculate breakdown dimensions
        double semanticIntent = calculateSemanticIntentScore(failedAction, element);
        double textSimilarity = calculateTextSimilarityScore(failedAction, element);
        double domContext = calculateDomContextScore(element);
        double visualPosition = calculateVisualPositionScore(element);

        // Weighted confidence calculation:
        // Semantic: 40%, Text: 30%, DOM Context: 20%, Visual: 10%
        double confidence = (semanticIntent * 0.40) +
                            (textSimilarity * 0.30) +
                            (domContext * 0.20) +
                            (visualPosition * 0.10);

        // Normalize to 3 decimal places
        confidence = Math.round(confidence * 1000.0) / 1000.0;
        dto.setConfidence(confidence);

        CandidateElementDto.MatchBreakdown breakdown = new CandidateElementDto.MatchBreakdown(
                Math.round(semanticIntent * 1000.0) / 1000.0,
                Math.round(textSimilarity * 1000.0) / 1000.0,
                Math.round(domContext * 1000.0) / 1000.0,
                Math.round(visualPosition * 1000.0) / 1000.0
        );
        dto.setMatchBreakdown(breakdown);

        // Generate reasoning
        dto.setReasoning(buildReasoningString(element, confidence, semanticIntent, textSimilarity));

        return dto;
    }

    private double calculateSemanticIntentScore(PlannedAction failedAction, InspectedElement element) {
        double score = 0.0;
        String actionDesc = failedAction.getTargetDescription() != null ? failedAction.getTargetDescription().toLowerCase() : "";
        String text = (element.getVisibleText() + " " + element.getAccessibleName()).toLowerCase();

        // Check if both element and action belong to the checkout / order / purchase domain
        boolean actionIsCheckout = actionDesc.contains("checkout") || actionDesc.contains("order") || 
                                   actionDesc.contains("purchase") || actionDesc.contains("submit") || actionDesc.contains("buy");
        boolean elementIsCheckout = text.contains("checkout") || text.contains("order") || 
                                    text.contains("place") || text.contains("purchase") || text.contains("pay");

        if (actionIsCheckout && elementIsCheckout) {
            score += 0.60;
        } else {
            for (String token : CHECKOUT_SUBMIT_TOKENS) {
                if (text.contains(token)) score += 0.25;
            }
        }

        // Role compatibility
        if (failedAction.getActionType() == PlannedAction.ActionType.CLICK) {
            if ("button".equalsIgnoreCase(element.getTag()) || "button".equalsIgnoreCase(element.getRole())) {
                score += 0.40;
            }
        } else if (failedAction.getActionType() == PlannedAction.ActionType.FILL) {
            if ("input".equalsIgnoreCase(element.getTag()) || "textbox".equalsIgnoreCase(element.getRole())) {
                score += 0.40;
            }
        }

        return Math.min(1.0, score);
    }

    private double calculateTextSimilarityScore(PlannedAction failedAction, InspectedElement element) {
        String target = (failedAction.getTargetDescription() != null ? failedAction.getTargetDescription() : "").toLowerCase();
        String locator = (failedAction.getLocatorHint() != null ? failedAction.getLocatorHint() : "").toLowerCase();
        String candidate = (element.getVisibleText() + " " + element.getAccessibleName()).toLowerCase();

        if (candidate.trim().isEmpty()) return 0.1;

        // Check synonym equivalence for primary CTA actions
        if ((target.contains("checkout") || target.contains("purchase") || locator.contains("checkout")) &&
            (candidate.contains("order") || candidate.contains("place") || candidate.contains("purchase"))) {
            return 0.90;
        }

        // Substring / token overlap
        String combinedTarget = target + " " + locator.replaceAll("[^a-zA-Z0-9]", " ");
        String[] targetWords = combinedTarget.split("\\s+");
        int matches = 0;
        for (String word : targetWords) {
            if (word.length() > 2 && candidate.contains(word)) {
                matches++;
            }
        }

        double tokenScore = (double) matches / Math.max(1, targetWords.length);
        double levenshtein = computeNormalizedLevenshtein(target, candidate);

        return Math.min(1.0, Math.max(0.2, (tokenScore * 0.7) + (levenshtein * 0.3)));
    }

    private double calculateDomContextScore(InspectedElement element) {
        double score = 0.5; // Base score

        String container = element.getContainerClass() != null ? element.getContainerClass().toLowerCase() : "";
        String parentTag = element.getParentTag() != null ? element.getParentTag().toLowerCase() : "";

        // Elements inside form-actions, action-dock, sticky bars, or footer buttons have high intent relevance
        if (container.contains("action") || container.contains("dock") || container.contains("footer") || container.contains("sticky")) {
            score += 0.40;
        }
        if ("form".equals(parentTag) || "div".equals(parentTag)) {
            score += 0.10;
        }

        return Math.min(1.0, score);
    }

    private double calculateVisualPositionScore(InspectedElement element) {
        double score = 0.0;
        if (element.isVisible()) score += 0.6;
        if (element.isEnabled()) score += 0.4;
        return score;
    }

    private double computeNormalizedLevenshtein(String s1, String s2) {
        int maxLength = Math.max(s1.length(), s2.length());
        if (maxLength == 0) return 1.0;
        int distance = levenshteinDistance(s1, s2);
        return 1.0 - ((double) distance / maxLength);
    }

    private int levenshteinDistance(String a, String b) {
        int[] costs = new int[b.length() + 1];
        for (int j = 0; j < costs.length; j++) costs[j] = j;
        for (int i = 1; i <= a.length(); i++) {
            costs[0] = i;
            int nw = i - 1;
            for (int j = 1; j <= b.length(); j++) {
                int cj = Math.min(1 + Math.min(costs[j], costs[j - 1]),
                        a.charAt(i - 1) == b.charAt(j - 1) ? nw : nw + 1);
                nw = costs[j];
                costs[j] = cj;
            }
        }
        return costs[b.length()];
    }

    private String buildReasoningString(InspectedElement el, double confidence, double semantic, double textSim) {
        if (confidence >= 0.85) {
            return "High Confidence (" + Math.round(confidence * 100) + "%): Matches functional role '" + el.getTag() +
                    "' and semantic tokens for submit intent with visible text '" + el.getVisibleText() + "'.";
        } else if (confidence >= 0.60) {
            return "Medium Confidence (" + Math.round(confidence * 100) + "%): Partial semantic alignment. Element is visible and interactive.";
        } else {
            return "Low Confidence (" + Math.round(confidence * 100) + "%): Weak semantic overlap. Candidate does not match primary intent.";
        }
    }
}
