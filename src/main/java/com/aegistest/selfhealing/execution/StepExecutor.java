package com.aegistest.selfhealing.execution;

import com.aegistest.selfhealing.browser.BrowserContextSession;
import com.aegistest.selfhealing.intent.PlannedAction;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.WaitForSelectorState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class StepExecutor {

    private static final Logger log = LoggerFactory.getLogger(StepExecutor.class);

    @Value("${aegis.browser.action-timeout-ms:5000}")
    private double actionTimeoutMs;

    @Value("${aegis.browser.navigation-timeout-ms:10000}")
    private double navigationTimeoutMs;

    public StepExecutionResult executeStep(BrowserContextSession session, PlannedAction action, String targetSelector) {
        Page page = session.getPage();
        String selector = targetSelector != null ? targetSelector : action.getLocatorHint();
        long startTime = System.currentTimeMillis();

        try {
            log.info("Executing step {} [{}]: selector='{}'", action.getStepNumber(), action.getActionType(), selector);

            switch (action.getActionType()) {
                case NAVIGATE -> {
                    page.navigate(action.getValue(), new Page.NavigateOptions().setTimeout(navigationTimeoutMs));
                }
                case CLICK -> {
                    // Try direct selector with action timeout
                    Locator locator = page.locator(selector).first();
                    locator.waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.VISIBLE).setTimeout(actionTimeoutMs));
                    locator.click(new Locator.ClickOptions().setTimeout(actionTimeoutMs));
                }
                case FILL -> {
                    Locator locator = page.locator(selector).first();
                    locator.waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.VISIBLE).setTimeout(actionTimeoutMs));
                    locator.fill(action.getValue() != null ? action.getValue() : "", new Locator.FillOptions().setTimeout(actionTimeoutMs));
                }
                case SELECT -> {
                    Locator locator = page.locator(selector).first();
                    locator.selectOption(action.getValue());
                }
                case ASSERT_VISIBLE -> {
                    Locator locator = page.locator(selector).first();
                    locator.waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.VISIBLE).setTimeout(actionTimeoutMs));
                }
                case ASSERT_TEXT -> {
                    Locator locator = page.locator(selector).first();
                    locator.waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.VISIBLE).setTimeout(actionTimeoutMs));
                }
            }

            long duration = System.currentTimeMillis() - startTime;
            String screenshot = session.captureScreenshotBase64();
            return StepExecutionResult.passed(duration, screenshot);

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            String screenshot = session.captureScreenshotBase64();
            String errorMsg = e.getMessage() != null ? e.getMessage() : e.getClass().getSimpleName();
            log.warn("Step execution failed on selector '{}': {}", selector, errorMsg);
            return StepExecutionResult.failed(duration, errorMsg, screenshot);
        }
    }
}
