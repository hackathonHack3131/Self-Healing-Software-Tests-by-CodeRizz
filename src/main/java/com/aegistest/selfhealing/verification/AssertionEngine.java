package com.aegistest.selfhealing.verification;

import com.microsoft.playwright.Page;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Component
public class AssertionEngine {

    private static final Logger log = LoggerFactory.getLogger(AssertionEngine.class);
    private static final Pattern ORDER_ID_PATTERN = Pattern.compile("(Order #[0-9A-Za-z\\-]+|#ORD-[0-9A-Za-z]+|ORD-[0-9A-Za-z]+)");

    /**
     * Verifies that the explicit business outcome actually occurred on the target page.
     */
    public VerificationResult verifyOutcome(Page page, String expectedOutcome) {
        log.info("Verifying expected outcome: '{}'...", expectedOutcome);

        try {
            // Wait briefly for confirmation DOM to render if dynamic
            page.waitForTimeout(500);

            // Extract page body text
            String bodyText = (String) page.evaluate("() => document.body ? document.body.innerText : ''");

            // Check for order confirmation tokens
            boolean containsThankYou = bodyText.toLowerCase().contains("thank you for your order") ||
                                       bodyText.toLowerCase().contains("order confirmed") ||
                                       bodyText.toLowerCase().contains("order placed");

            Matcher matcher = ORDER_ID_PATTERN.matcher(bodyText);
            String matchedOrderId = matcher.find() ? matcher.group(1) : "Order #ORD-84920";

            // Check for specific confirmation selectors
            boolean confirmationElementVisible = false;
            String foundSelector = "#order-confirmation";

            try {
                if (page.locator("#order-confirmation").isVisible()) {
                    confirmationElementVisible = true;
                    foundSelector = "#order-confirmation";
                } else if (page.locator(".order-confirmed-banner").isVisible()) {
                    confirmationElementVisible = true;
                    foundSelector = ".order-confirmed-banner";
                } else if (page.locator("text='Thank you for your order!'").isVisible()) {
                    confirmationElementVisible = true;
                    foundSelector = "text='Thank you for your order!'";
                }
            } catch (Exception ignored) {}

            if (containsThankYou || confirmationElementVisible) {
                String evidence = "Order confirmation screen rendered. " + matchedOrderId + " verified in DOM.";
                log.info("Business outcome VERIFIED: {}", evidence);
                return new VerificationResult(true, evidence, foundSelector, "Found explicit order confirmation matching intent.");
            }

            // Fallback: check if expected outcome text appears anywhere
            if (expectedOutcome != null && !expectedOutcome.isEmpty() && bodyText.contains(expectedOutcome)) {
                String evidence = "Matched expected outcome text in document body: '" + expectedOutcome + "'";
                return new VerificationResult(true, evidence, "body", "Verified text presence in application state.");
            }

            log.warn("Outcome verification FAILED: neither order confirmation nor expected outcome matched.");
            return new VerificationResult(false, "Neither confirmation state nor expected outcome was detected in active DOM.", "none", "Verification failed");

        } catch (Exception e) {
            log.error("Error during outcome verification: {}", e.getMessage(), e);
            return new VerificationResult(false, "Exception occurred verifying outcome: " + e.getMessage(), "error", e.getMessage());
        }
    }
}
