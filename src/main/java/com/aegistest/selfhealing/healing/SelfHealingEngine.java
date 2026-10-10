package com.aegistest.selfhealing.healing;

import com.aegistest.selfhealing.ai.ExternalLLMHealingProvider;
import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.dto.UiChangeDto;
import com.aegistest.selfhealing.inspection.InspectedElement;
import com.aegistest.selfhealing.inspection.PageInspector;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.PlannedAction;
import com.microsoft.playwright.Page;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Component
public class SelfHealingEngine {

    private static final Logger log = LoggerFactory.getLogger(SelfHealingEngine.class);

    @Value("${aegis.healing.confidence-threshold-high:0.85}")
    private double highConfidenceThreshold;

    @Value("${aegis.healing.confidence-threshold-medium:0.60}")
    private double mediumConfidenceThreshold;

    private final PageInspector pageInspector;
    private final CandidateScorer candidateScorer;
    private final ChangeDetector changeDetector;
    private final ExternalLLMHealingProvider aiProvider;

    public SelfHealingEngine(PageInspector pageInspector,
                             CandidateScorer candidateScorer,
                             ChangeDetector changeDetector,
                             ExternalLLMHealingProvider aiProvider) {
        this.pageInspector = pageInspector;
        this.candidateScorer = candidateScorer;
        this.changeDetector = changeDetector;
        this.aiProvider = aiProvider;
    }

    /**
     * Executes the self-healing algorithm:
     * 1. Re-inspects current page DOM
     * 2. Extracts candidate elements
     * 3. Scores and ranks candidates transparently
     * 4. Enforces safety thresholds & ambiguity checks
     * 5. Synthesizes repaired action locator
     */
    public HealingResult healStep(Page page, PlannedAction failedAction, String originalError) {
        log.info("Engaging Self-Healing Engine for failed action '{}'...", failedAction.getTargetDescription());

        HealingResult result = new HealingResult();

        // 1. Re-inspect the current interface
        PageSnapshot currentSnapshot = pageInspector.inspect(page);

        // 2. Score all interactive elements on the page
        List<CandidateElementDto> scoredCandidates = new ArrayList<>();
        int index = 1;
        for (InspectedElement element : currentSnapshot.getElements()) {
            if (!element.isVisible() || !element.isEnabled()) {
                continue;
            }
            CandidateElementDto candidate = candidateScorer.scoreCandidate(failedAction, element, index++);
            candidate = aiProvider.rankCandidate(failedAction, candidate, currentSnapshot);
            scoredCandidates.add(candidate);
        }

        // Sort descending by confidence score
        scoredCandidates.sort(Comparator.comparingDouble(CandidateElementDto::getConfidence).reversed());
        result.setAllCandidates(scoredCandidates);

        if (scoredCandidates.isEmpty()) {
            result.setStatus(HealingResult.Status.FAILED);
            result.setExplanation("No interactive candidate elements found in active DOM snapshot.");
            return result;
        }

        CandidateElementDto best = scoredCandidates.get(0);

        // Check for ambiguous multiple top matches
        if (scoredCandidates.size() > 1) {
            CandidateElementDto second = scoredCandidates.get(1);
            if (best.getConfidence() < 0.90 && Math.abs(best.getConfidence() - second.getConfidence()) < 0.05) {
                log.warn("Healing ambiguity: top two candidates have near identical confidence ({} vs {})",
                        best.getConfidence(), second.getConfidence());
                result.setStatus(HealingResult.Status.AMBIGUOUS);
                result.setSelectedCandidate(best);
                result.setConfidenceScore(best.getConfidence());
                result.setExplanation("Ambiguous recovery: Multiple alternative elements have similar confidence scores. Manual confirmation required.");
                return result;
            }
        }

        // Validate confidence against thresholds
        if (best.getConfidence() < mediumConfidenceThreshold) {
            log.warn("Top candidate confidence {} is below medium threshold {}", best.getConfidence(), mediumConfidenceThreshold);
            result.setStatus(HealingResult.Status.FAILED);
            result.setSelectedCandidate(best);
            result.setConfidenceScore(best.getConfidence());
            result.setExplanation("Healing rejected: Top candidate confidence (" +
                    Math.round(best.getConfidence() * 100) + "%) is below minimum threshold (" +
                    Math.round(mediumConfidenceThreshold * 100) + "%).");
            return result;
        }

        // Successful candidate selection!
        result.setStatus(HealingResult.Status.SUCCESS);
        result.setSelectedCandidate(best);
        result.setConfidenceScore(best.getConfidence());
        result.setStrategy("semantic_intent");

        // Synthesize repaired action and selector
        String repairedSelector = best.getSelector();
        result.setRepairedSelector(repairedSelector);

        if (failedAction.getActionType() == PlannedAction.ActionType.CLICK) {
            result.setRepairedAction("click('" + repairedSelector + "')");
        } else if (failedAction.getActionType() == PlannedAction.ActionType.FILL) {
            result.setRepairedAction("fill('" + repairedSelector + "', '" + failedAction.getValue() + "')");
        } else {
            result.setRepairedAction("interact('" + repairedSelector + "')");
        }

        // Detect structural UI mutations
        List<UiChangeDto> changes = changeDetector.detectChanges(failedAction, best, currentSnapshot);
        result.setDetectedChanges(changes);

        // Build human-readable explanation
        String explanation = aiProvider.explainFailure(failedAction.getLocatorHint(), failedAction.getTargetDescription(), originalError, currentSnapshot);
        result.setExplanation(explanation);

        log.info("Self-Healing successful! Selected replacement '{}' with confidence {}%",
                repairedSelector, Math.round(best.getConfidence() * 100));

        return result;
    }
}
