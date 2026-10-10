package com.aegistest.selfhealing;

import com.aegistest.selfhealing.browser.BrowserContextSession;
import com.aegistest.selfhealing.browser.BrowserManager;
import com.aegistest.selfhealing.dto.CandidateElementDto;
import com.aegistest.selfhealing.execution.StepExecutionResult;
import com.aegistest.selfhealing.execution.StepExecutor;
import com.aegistest.selfhealing.healing.CandidateScorer;
import com.aegistest.selfhealing.healing.HealingResult;
import com.aegistest.selfhealing.healing.SelfHealingEngine;
import com.aegistest.selfhealing.inspection.PageInspector;
import com.aegistest.selfhealing.inspection.PageSnapshot;
import com.aegistest.selfhealing.intent.PlannedAction;
import com.aegistest.selfhealing.verification.AssertionEngine;
import com.aegistest.selfhealing.verification.VerificationResult;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import java.io.File;
import java.nio.file.Paths;

import static org.junit.jupiter.api.Assertions.*;

class LiveBrowserExecutionIntegrationTest {

    private BrowserManager browserManager;
    private BrowserContextSession session;
    private StepExecutor stepExecutor;
    private PageInspector pageInspector;
    private CandidateScorer candidateScorer;
    private AssertionEngine assertionEngine;
    private String localDemoUrl;

    @BeforeEach
    void setUp() {
        browserManager = new BrowserManager();
        ReflectionTestUtils.setField(browserManager, "headless", true);
        ReflectionTestUtils.setField(browserManager, "slowMoMs", 50.0);
        ReflectionTestUtils.setField(browserManager, "preferredChannel", "chromium");
        ReflectionTestUtils.setField(browserManager, "artifactStoragePath", "./artifacts");

        stepExecutor = new StepExecutor();
        ReflectionTestUtils.setField(stepExecutor, "actionTimeoutMs", 3000.0);
        ReflectionTestUtils.setField(stepExecutor, "navigationTimeoutMs", 5000.0);

        pageInspector = new PageInspector(new ObjectMapper());
        candidateScorer = new CandidateScorer();
        assertionEngine = new AssertionEngine();

        // Path to built-in static checkout demo
        File demoFile = Paths.get("src/main/resources/static/demo/index.html").toFile();
        localDemoUrl = demoFile.toURI().toString();

        session = browserManager.createSession();
    }

    @AfterEach
    void tearDown() {
        if (session != null) {
            session.close();
        }
        if (browserManager != null) {
            browserManager.cleanup();
        }
    }

    @Test
    void testVersionACheckoutPassesDirectly() {
        session.getPage().navigate(localDemoUrl + "?version=A");

        // Step 1: Fill Name
        PlannedAction fillName = new PlannedAction(1, PlannedAction.ActionType.FILL, "Customer Name", "input#customer-name", "Alex Morgan");
        StepExecutionResult res1 = stepExecutor.executeStep(session, fillName, "input#customer-name");
        assertTrue(res1.isSuccess());

        // Step 2: Fill Card
        PlannedAction fillCard = new PlannedAction(2, PlannedAction.ActionType.FILL, "Card Number", "input#card-number", "4242 4242 4242 4242");
        StepExecutionResult res2 = stepExecutor.executeStep(session, fillCard, "input#card-number");
        assertTrue(res2.isSuccess());

        // Step 3: Click Checkout (Baseline #checkout-button exists in Version A)
        PlannedAction clickCheckout = new PlannedAction(3, PlannedAction.ActionType.CLICK, "Checkout Button", "#checkout-button", null);
        StepExecutionResult res3 = stepExecutor.executeStep(session, clickCheckout, "#checkout-button");
        assertTrue(res3.isSuccess(), "Version A should find and click #checkout-button directly");

        // Verify Outcome
        VerificationResult verification = assertionEngine.verifyOutcome(session.getPage(), "Thank you for your order!");
        assertTrue(verification.isVerified());
        assertTrue(verification.getEvidenceText().contains("Order #ORD-84920"));
    }

    @Test
    void testVersionBBreaksOriginalSelectorAndSelfHeals() {
        session.getPage().navigate(localDemoUrl + "?version=B");

        // Step 1: Fill Name
        PlannedAction fillName = new PlannedAction(1, PlannedAction.ActionType.FILL, "Customer Name", "input#customer-name", "Alex Morgan");
        assertTrue(stepExecutor.executeStep(session, fillName, "input#customer-name").isSuccess());

        // Step 2: Try original checkout locator (#checkout-button does NOT exist in Version B!)
        PlannedAction clickCheckout = new PlannedAction(2, PlannedAction.ActionType.CLICK, "Button that submits checkout purchase", "#checkout-button", null);
        StepExecutionResult failedRes = stepExecutor.executeStep(session, clickCheckout, "#checkout-button");
        assertFalse(failedRes.isSuccess(), "Version B must break the original static locator #checkout-button");

        // Step 3: Self-Healing inspection and candidate scoring
        PageSnapshot snapshot = pageInspector.inspect(session.getPage());
        assertFalse(snapshot.getElements().isEmpty());

        CandidateElementDto bestCandidate = null;
        for (var el : snapshot.getElements()) {
            CandidateElementDto scored = candidateScorer.scoreCandidate(clickCheckout, el, 1);
            if (bestCandidate == null || scored.getConfidence() > bestCandidate.getConfidence()) {
                bestCandidate = scored;
            }
        }

        assertNotNull(bestCandidate);
        assertTrue(bestCandidate.getConfidence() >= 0.85, "Self-healing candidate confidence must be >= 0.85, was: " + bestCandidate.getConfidence());
        assertTrue(bestCandidate.getText().contains("Place My Order"));

        // Step 4: Execute repaired step using repaired locator
        StepExecutionResult repairedRes = stepExecutor.executeStep(session, clickCheckout, bestCandidate.getSelector());
        assertTrue(repairedRes.isSuccess(), "Repaired step must succeed using healed locator");

        // Step 5: Verify confirmation outcome
        VerificationResult verification = assertionEngine.verifyOutcome(session.getPage(), "Thank you for your order!");
        assertTrue(verification.isVerified(), "Final order confirmation state must be verified");
        assertTrue(verification.getEvidenceText().contains("ORD-84920"));
    }
}
