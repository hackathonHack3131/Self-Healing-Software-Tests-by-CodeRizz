package com.aegistest.selfhealing.service;

import com.aegistest.selfhealing.dto.DemoComparisonResponse;
import com.aegistest.selfhealing.dto.DemoRunRequest;
import com.aegistest.selfhealing.dto.TestRunResponse;
import com.aegistest.selfhealing.entity.TestCaseEntity;
import com.aegistest.selfhealing.entity.TestRunEntity;
import com.aegistest.selfhealing.execution.ExecutionEngine;
import com.aegistest.selfhealing.intent.ExecutionPlan;
import com.aegistest.selfhealing.intent.IntentParser;
import com.aegistest.selfhealing.repository.TestCaseRepository;
import com.aegistest.selfhealing.repository.TestRunRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
public class DemoManagerService {

    private static final Logger log = LoggerFactory.getLogger(DemoManagerService.class);

    @Value("${aegis.demo.target-url:http://localhost:5173}")
    private String externalDemoUrl;

    @Value("${aegis.demo.internal-url:http://localhost:8000/demo/index.html}")
    private String internalDemoUrl;

    private String currentVersion = "A";

    private final TestCaseRepository testCaseRepository;
    private final TestRunRepository testRunRepository;
    private final IntentParser intentParser;
    private final ExecutionEngine executionEngine;
    private final TestManagementService testManagementService;

    public DemoManagerService(TestCaseRepository testCaseRepository,
                              TestRunRepository testRunRepository,
                              IntentParser intentParser,
                              ExecutionEngine executionEngine,
                              TestManagementService testManagementService) {
        this.testCaseRepository = testCaseRepository;
        this.testRunRepository = testRunRepository;
        this.intentParser = intentParser;
        this.executionEngine = executionEngine;
        this.testManagementService = testManagementService;
    }

    public Map<String, Object> resetToVersionA() {
        this.currentVersion = "A";
        return Map.of("version", "A", "message", "Demo reset to baseline Version A successfully.");
    }

    public Map<String, Object> switchToVersionB() {
        this.currentVersion = "B";
        return Map.of("version", "B", "message", "Applied modern DOM restructuring (Version B).");
    }

    public String getCurrentVersion() {
        return currentVersion;
    }

    public TestRunResponse runDemoWorkflow(DemoRunRequest req) {
        String targetVer = req.getVersion() != null ? req.getVersion().toUpperCase() : currentVersion;
        this.currentVersion = targetVer;

        // Choose target URL (prefer external 5173 if accessible, else internal 8000 demo)
        String targetUrl = resolveDemoUrl(targetVer);

        // Find or create demo test case
        TestCaseEntity testCase = testCaseRepository.findById("demo-checkout")
                .orElseGet(() -> {
                    TestCaseEntity tc = new TestCaseEntity();
                    tc.setId("demo-checkout");
                    tc.setName("E-Commerce Checkout Workflow");
                    tc.setTargetUrl(targetUrl);
                    tc.setIntent("Complete checkout with a valid credit card and verify order confirmation.");
                    tc.setEnvironment("staging");
                    tc.setBrowser("chromium");
                    tc.setSelfHealingEnabled(req.isSelfHealing());
                    tc.setMaxHealingAttempts(3);
                    tc.setExpectedOutcome("Thank you for your order! Order #ORD-84920");
                    tc.setCreatedAt(Instant.now());
                    return testCaseRepository.save(tc);
                });

        testCase.setTargetUrl(targetUrl);
        testCase.setSelfHealingEnabled(req.isSelfHealing());
        testCaseRepository.save(testCase);

        ExecutionPlan plan = intentParser.parseAndValidate(testCase.getIntent(), targetUrl);

        TestRunEntity run = new TestRunEntity();
        run.setId("run-demo-" + targetVer.toLowerCase() + "-" + UUID.randomUUID().toString().substring(0, 8));
        run.setTestId(testCase.getId());
        run.setTestName(testCase.getName());
        run.setTargetUrl(targetUrl);
        run.setIntent(testCase.getIntent());
        run.setStatus("queued");
        run.setTotalSteps(plan.getSteps().size());
        run.setStartedAt(Instant.now());

        TestRunEntity savedRun = testRunRepository.save(run);

        // Execute live Playwright browser run asynchronously
        executionEngine.executeRunAsync(savedRun, testCase, plan);

        return testManagementService.toTestRunResponse(savedRun);
    }

    public DemoComparisonResponse getDemoComparison() {
        DemoComparisonResponse resp = new DemoComparisonResponse();

        DemoComparisonResponse.VersionDetails verA = new DemoComparisonResponse.VersionDetails(
                "#checkout-button",
                "Complete Purchase",
                "form-actions-flat",
                """
                <form id="checkout-form">
                  <div class="customer-info">...</div>
                  <div class="form-actions-flat">
                    <button id="checkout-button" class="btn-checkout">Complete Purchase</button>
                  </div>
                </form>
                """
        );

        DemoComparisonResponse.VersionDetails verB = new DemoComparisonResponse.VersionDetails(
                "div.action-dock > button.btn-primary-gradient-v2",
                "Place My Order",
                "action-dock bottom-sticky",
                """
                <form id="checkout-form">
                  <div class="customer-info">...</div>
                  <div class="action-dock bottom-sticky">
                    <button id="place-order-cta" class="btn-primary-gradient-v2" data-testid="place-order-cta">
                      Place My Order
                    </button>
                  </div>
                </form>
                """
        );

        resp.setVersionA(verA);
        resp.setVersionB(verB);

        List<DemoComparisonResponse.StructuralDiff> diffs = List.of(
                new DemoComparisonResponse.StructuralDiff(
                        "Primary Selector ID",
                        "Critical (Breaks static locator)",
                        "#checkout-button exists",
                        "#checkout-button removed entirely"
                ),
                new DemoComparisonResponse.StructuralDiff(
                        "Button Label Text",
                        "Medium",
                        "'Complete Purchase'",
                        "'Place My Order'"
                ),
                new DemoComparisonResponse.StructuralDiff(
                        "DOM Container Location",
                        "High",
                        "Inside .form-actions-flat",
                        "Relocated to sticky .action-dock wrapper"
                ),
                new DemoComparisonResponse.StructuralDiff(
                        "Semantic Role & Intent",
                        "Preserved (100% Intent Compatible)",
                        "Form submit trigger for checkout",
                        "Form submit trigger for checkout"
                )
        );

        resp.setStructuralDifferences(diffs);
        return resp;
    }

    private String resolveDemoUrl(String version) {
        // Test if external Vite demo is responding on 5173
        try {
            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofMillis(500))
                    .build();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(externalDemoUrl + "/?version=" + version))
                    .timeout(Duration.ofMillis(500))
                    .GET()
                    .build();
            HttpResponse<Void> response = client.send(request, HttpResponse.BodyHandlers.discarding());
            if (response.statusCode() == 200) {
                return externalDemoUrl + "/?version=" + version;
            }
        } catch (Exception ignored) {}

        // Fallback to internal demo served by Spring Boot
        return internalDemoUrl + "?version=" + version;
    }
}
