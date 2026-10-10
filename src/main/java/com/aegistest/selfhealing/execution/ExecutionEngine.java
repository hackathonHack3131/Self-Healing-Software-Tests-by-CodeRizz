package com.aegistest.selfhealing.execution;

import com.aegistest.selfhealing.browser.BrowserContextSession;
import com.aegistest.selfhealing.browser.BrowserManager;
import com.aegistest.selfhealing.dto.ConsoleLogDto;
import com.aegistest.selfhealing.dto.TestStepDto;
import com.aegistest.selfhealing.dto.UiChangeDto;
import com.aegistest.selfhealing.entity.*;
import com.aegistest.selfhealing.events.ExecutionEventPublisher;
import com.aegistest.selfhealing.healing.HealingResult;
import com.aegistest.selfhealing.healing.SelfHealingEngine;
import com.aegistest.selfhealing.inspection.PageInspector;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.PlannedAction;
import com.aegistest.selfhealing.repository.*;
import com.aegistest.selfhealing.verification.AssertionEngine;
import com.aegistest.selfhealing.verification.VerificationResult;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;

@Service
public class ExecutionEngine {

    private static final Logger log = LoggerFactory.getLogger(ExecutionEngine.class);

    @Value("${aegis.healing.max-attempts-per-step:3}")
    private int maxHealingPerStep;

    @Value("${aegis.healing.max-total-attempts:5}")
    private int maxTotalHealing;

    private final BrowserManager browserManager;
    private final PageInspector pageInspector;
    private final StepExecutor stepExecutor;
    private final SelfHealingEngine selfHealingEngine;
    private final AssertionEngine assertionEngine;
    private final ExecutionEventPublisher eventPublisher;
    private final TestRunRepository runRepository;
    private final ExecutionStepRepository stepRepository;
    private final HealingAttemptRepository healingRepository;
    private final UiChangeRepository uiChangeRepository;
    private final AssertionResultRepository assertionRepository;
    private final TestCaseRepository testCaseRepository;
    private final ObjectMapper objectMapper;

    public ExecutionEngine(BrowserManager browserManager,
                           PageInspector pageInspector,
                           StepExecutor stepExecutor,
                           SelfHealingEngine selfHealingEngine,
                           AssertionEngine assertionEngine,
                           ExecutionEventPublisher eventPublisher,
                           TestRunRepository runRepository,
                           ExecutionStepRepository stepRepository,
                           HealingAttemptRepository healingRepository,
                           UiChangeRepository uiChangeRepository,
                           AssertionResultRepository assertionRepository,
                           TestCaseRepository testCaseRepository,
                           ObjectMapper objectMapper) {
        this.browserManager = browserManager;
        this.pageInspector = pageInspector;
        this.stepExecutor = stepExecutor;
        this.selfHealingEngine = selfHealingEngine;
        this.assertionEngine = assertionEngine;
        this.eventPublisher = eventPublisher;
        this.runRepository = runRepository;
        this.stepRepository = stepRepository;
        this.healingRepository = healingRepository;
        this.uiChangeRepository = uiChangeRepository;
        this.assertionRepository = assertionRepository;
        this.testCaseRepository = testCaseRepository;
        this.objectMapper = objectMapper;
    }

    /**
     * Executes a test run asynchronously using real Playwright browser automation.
     */
    @Async("testExecutionExecutor")
    public void executeRunAsync(TestRunEntity run, TestCaseEntity testCase, ExecutionPlan plan) {
        String runId = run.getId();
        long startMs = System.currentTimeMillis();

        log.info("Starting live browser execution for Run ID '{}' targeting '{}'...", runId, run.getTargetUrl());

        // Update status to running
        run.setStatus("running");
        run.setStartedAt(Instant.now());
        runRepository.save(run);

        eventPublisher.publish(runId, "run.started", Map.of(
                "runId", runId,
                "targetUrl", run.getTargetUrl(),
                "intent", run.getIntent(),
                "totalSteps", plan.getSteps().size()
        ));

        BrowserContextSession session = null;
        int healingCount = 0;
        boolean overallPassed = true;
        boolean anyStepHealed = false;
        String initialResult = null;

        try {
            session = browserManager.createSession();

            // 1. Initial navigation to target URL
            log.info("Navigating to target URL: {}", run.getTargetUrl());
            session.getPage().navigate(run.getTargetUrl());

            // 2. Initial Page Inspection
            PageSnapshot initialSnapshot = pageInspector.inspect(session.getPage());
            run.setCurrentScreenshot(session.captureScreenshotBase64());
            runRepository.save(run);

            eventPublisher.publish(runId, "page.inspected", Map.of(
                    "pageTitle", initialSnapshot.getTitle(),
                    "elementCount", initialSnapshot.getElements().size()
            ));

            eventPublisher.publish(runId, "plan.generated", Map.of(
                    "reasoningMode", plan.getReasoningMode(),
                    "stepsCount", plan.getSteps().size(),
                    "assertionsCount", plan.getAssertions().size()
            ));

            // 3. Execute Steps
            int stepIndex = 0;
            for (PlannedAction step : plan.getSteps()) {
                stepIndex++;
                run.setCurrentStepIndex(stepIndex);
                runRepository.save(run);

                eventPublisher.publish(runId, "step.started", Map.of(
                        "stepNumber", step.getStepNumber(),
                        "description", step.getTargetDescription(),
                        "action", step.getActionType().name(),
                        "selector", step.getLocatorHint() != null ? step.getLocatorHint() : ""
                ));

                // Save initial step record
                ExecutionStepEntity stepEntity = new ExecutionStepEntity();
                stepEntity.setId("step-" + runId + "-" + step.getStepNumber());
                stepEntity.setRunId(runId);
                stepEntity.setStepNumber(step.getStepNumber());
                stepEntity.setDescription(step.getTargetDescription());
                stepEntity.setOriginalAction(step.getActionType().name().toLowerCase() + "('" + step.getLocatorHint() + "')");
                stepEntity.setOriginalSelector(step.getLocatorHint());
                stepEntity.setStatus("running");
                stepRepository.save(stepEntity);

                // Attempt original execution
                StepExecutionResult execResult = stepExecutor.executeStep(session, step, step.getLocatorHint());
                stepEntity.setDurationMs(execResult.getDurationMs());
                stepEntity.setScreenshotAfter(execResult.getScreenshotAfter());
                run.setCurrentScreenshot(execResult.getScreenshotAfter());

                if (execResult.isSuccess()) {
                    stepEntity.setStatus("passed");
                    stepRepository.save(stepEntity);
                    if (initialResult == null && stepIndex == plan.getSteps().size() && !anyStepHealed) {
                        initialResult = "passed";
                    }
                    continue;
                }

                // Step failed!
                if (initialResult == null) {
                    initialResult = "failed";
                }

                log.warn("Step {} failed with error: {}. Testing self-healing eligibility...", step.getStepNumber(), execResult.getErrorMessage());
                stepEntity.setErrorMessage(execResult.getErrorMessage());
                stepEntity.setStatus("failed");
                stepRepository.save(stepEntity);

                eventPublisher.publish(runId, "step.failed", Map.of(
                        "stepNumber", step.getStepNumber(),
                        "failedSelector", step.getLocatorHint(),
                        "error", execResult.getErrorMessage()
                ));

                // Check self-healing policy
                if (!testCase.isSelfHealingEnabled()) {
                    log.info("Self-healing disabled for this test case. Halting run.");
                    overallPassed = false;
                    break;
                }

                if (healingCount >= maxTotalHealing) {
                    log.warn("Exceeded maximum total healing attempts ({}). Halting.", maxTotalHealing);
                    overallPassed = false;
                    break;
                }

                // Self-Healing activated!
                run.setStatus("healing");
                runRepository.save(run);

                eventPublisher.publish(runId, "healing.started", Map.of(
                        "stepNumber", step.getStepNumber(),
                        "failedSelector", step.getLocatorHint(),
                        "targetGoal", step.getTargetDescription()
                ));

                HealingResult healingResult = selfHealingEngine.healStep(session.getPage(), step, execResult.getErrorMessage());

                if (healingResult.getStatus() == HealingResult.Status.SUCCESS) {
                    healingCount++;
                    anyStepHealed = true;

                    // Publish candidate selected
                    eventPublisher.publish(runId, "candidate.selected", Map.of(
                            "candidateSelector", healingResult.getRepairedSelector(),
                            "confidence", healingResult.getConfidenceScore(),
                            "reasoning", healingResult.getSelectedCandidate().getReasoning()
                    ));

                    // Publish detected change
                    if (!healingResult.getDetectedChanges().isEmpty()) {
                        for (UiChangeDto change : healingResult.getDetectedChanges()) {
                            UiChangeEntity changeEntity = new UiChangeEntity();
                            changeEntity.setId(change.getId());
                            changeEntity.setRunId(runId);
                            changeEntity.setElementDescription(change.getElementDescription());
                            changeEntity.setChangeType(change.getType());
                            changeEntity.setPreviousDomSnippet(change.getPreviousDomSnippet());
                            changeEntity.setNewDomSnippet(change.getNewDomSnippet());
                            changeEntity.setImpactScore(change.getImpactScore());
                            uiChangeRepository.save(changeEntity);

                            eventPublisher.publish(runId, "change.detected", Map.of(
                                    "type", change.getType(),
                                    "description", change.getElementDescription(),
                                    "impact", change.getImpactScore()
                            ));
                        }
                    }

                    // Retry execution using repaired selector
                    log.info("Retrying step {} with healed selector '{}'...", step.getStepNumber(), healingResult.getRepairedSelector());
                    StepExecutionResult retryResult = stepExecutor.executeStep(session, step, healingResult.getRepairedSelector());

                    if (retryResult.isSuccess()) {
                        stepEntity.setStatus("healed");
                        stepEntity.setRepairedSelector(healingResult.getRepairedSelector());
                        stepEntity.setRepairedAction(healingResult.getRepairedAction());
                        stepEntity.setDurationMs(stepEntity.getDurationMs() + retryResult.getDurationMs());
                        stepEntity.setScreenshotAfter(retryResult.getScreenshotAfter());
                        stepRepository.save(stepEntity);

                        // Save healing attempt record
                        HealingAttemptEntity attempt = new HealingAttemptEntity();
                        attempt.setId("heal-" + UUID.randomUUID().toString());
                        attempt.setRunId(runId);
                        attempt.setStepId(stepEntity.getId());
                        attempt.setStepNumber(step.getStepNumber());
                        attempt.setFailedSelector(step.getLocatorHint());
                        attempt.setFailureReason(execResult.getErrorMessage());
                        attempt.setStrategy(healingResult.getStrategy());
                        attempt.setRepairedAction(healingResult.getRepairedAction());
                        attempt.setRepairedSelector(healingResult.getRepairedSelector());
                        attempt.setConfidenceScore(healingResult.getConfidenceScore());
                        attempt.setDurationMs(retryResult.getDurationMs());
                        attempt.setAttemptStatus("SUCCESS");
                        attempt.setRepairExplanation(healingResult.getExplanation());
                        try {
                            attempt.setCandidatesJson(objectMapper.writeValueAsString(healingResult.getAllCandidates()));
                            attempt.setSelectedCandidateJson(objectMapper.writeValueAsString(healingResult.getSelectedCandidate()));
                        } catch (Exception ignored) {}
                        healingRepository.save(attempt);

                        eventPublisher.publish(runId, "step.repaired", Map.of(
                                "stepNumber", step.getStepNumber(),
                                "repairedSelector", healingResult.getRepairedSelector(),
                                "confidence", healingResult.getConfidenceScore()
                        ));
                    } else {
                        log.error("Retry with repaired selector failed: {}", retryResult.getErrorMessage());
                        overallPassed = false;
                        break;
                    }
                } else {
                    log.error("Healing engine could not resolve candidate: {}", healingResult.getExplanation());
                    overallPassed = false;
                    break;
                }
            }

            // 4. Verify explicit outcome
            run.setStatus("verifying");
            runRepository.save(run);

            VerificationResult verification = assertionEngine.verifyOutcome(session.getPage(), testCase.getExpectedOutcome());

            run.setFinalVerified(verification.isVerified());
            run.setFinalEvidenceText(verification.getEvidenceText());
            run.setFinalTargetSelector(verification.getTargetSelector());

            // Save assertion record
            AssertionResultEntity assertionEntity = new AssertionResultEntity();
            assertionEntity.setId("assert-" + UUID.randomUUID().toString());
            assertionEntity.setRunId(runId);
            assertionEntity.setAssertionType("OUTCOME_VERIFICATION");
            assertionEntity.setExpectedOutcome(testCase.getExpectedOutcome());
            assertionEntity.setActualOutcome(verification.getEvidenceText());
            assertionEntity.setPassed(verification.isVerified());
            assertionEntity.setEvidence(verification.getEvidenceText());
            assertionRepository.save(assertionEntity);

            if (verification.isVerified()) {
                eventPublisher.publish(runId, "assertion.passed", Map.of(
                        "evidence", verification.getEvidenceText(),
                        "selector", verification.getTargetSelector()
                ));
            } else {
                overallPassed = false;
                eventPublisher.publish(runId, "assertion.failed", Map.of(
                        "evidence", verification.getEvidenceText()
                ));
            }

        } catch (Exception e) {
            log.error("Fatal error during test run execution: {}", e.getMessage(), e);
            overallPassed = false;
            run.setErrorSummary(e.getMessage());
        } finally {
            if (session != null) {
                session.close();
            }

            long totalDuration = System.currentTimeMillis() - startMs;
            run.setDurationMs(totalDuration);
            run.setCompletedAt(Instant.now());
            run.setHealingCount(healingCount);
            run.setInitialResult(initialResult != null ? initialResult : (overallPassed ? "passed" : "failed"));

            if (overallPassed) {
                run.setStatus("passed");
                run.setFinalResult(anyStepHealed ? "healed" : "passed");
                testCase.setStatus(anyStepHealed ? "healed" : "passed");
            } else {
                run.setStatus("failed");
                run.setFinalResult("failed");
                testCase.setStatus("failed");
            }

            testCase.setLastRunAt(Instant.now());
            testCaseRepository.save(testCase);
            runRepository.save(run);

            eventPublisher.publish(runId, "run.completed", Map.of(
                    "runId", runId,
                    "finalResult", run.getFinalResult(),
                    "healingCount", healingCount,
                    "durationMs", totalDuration
            ));

            log.info("Run '{}' completed in {}ms with finalResult='{}'", runId, totalDuration, run.getFinalResult());
        }
    }
}
