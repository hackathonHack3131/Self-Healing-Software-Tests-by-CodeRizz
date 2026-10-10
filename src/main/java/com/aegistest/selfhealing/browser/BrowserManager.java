package com.aegistest.selfhealing.browser;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;

@Component
public class BrowserManager {

    private static final Logger log = LoggerFactory.getLogger(BrowserManager.class);

    @Value("${aegis.browser.headless:true}")
    private boolean headless;

    @Value("${aegis.browser.slow-mo-ms:100}")
    private double slowMoMs;

    @Value("${aegis.browser.channel:chromium}")
    private String preferredChannel;

    @Value("${aegis.artifacts.storage-path:./artifacts}")
    private String artifactStoragePath;

    private Playwright playwright;
    private Browser browser;

    public synchronized BrowserContextSession createSession() {
        initBrowserIfNeeded();

        Browser.NewContextOptions options = new Browser.NewContextOptions()
                .setViewportSize(1366, 768)
                .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AegisTest-Runner/1.0");

        return new BrowserContextSession(browser.newContext(options), artifactStoragePath);
    }

    private void initBrowserIfNeeded() {
        if (browser != null && browser.isConnected()) {
            return;
        }

        if (playwright == null) {
            log.info("Initializing Playwright runtime...");
            playwright = Playwright.create();
        }

        BrowserType.LaunchOptions launchOptions = new BrowserType.LaunchOptions()
                .setHeadless(headless)
                .setSlowMo(slowMoMs);

        // Attempt launch using preferred channel or fallbacks
        try {
            if ("chrome".equalsIgnoreCase(preferredChannel)) {
                launchOptions.setChannel("chrome");
            } else if ("msedge".equalsIgnoreCase(preferredChannel)) {
                launchOptions.setChannel("msedge");
            }

            log.info("Launching browser (channel: {}, headless: {})...", preferredChannel, headless);
            browser = playwright.chromium().launch(launchOptions);
        } catch (Exception e) {
            log.warn("Failed to launch browser with channel '{}': {}. Attempting fallback channels...", preferredChannel, e.getMessage());

            // Fallback sequence: standard bundled -> Chrome -> Edge
            try {
                BrowserType.LaunchOptions defaultOptions = new BrowserType.LaunchOptions()
                        .setHeadless(headless)
                        .setSlowMo(slowMoMs);
                browser = playwright.chromium().launch(defaultOptions);
                log.info("Successfully launched bundled Chromium");
            } catch (Exception e2) {
                try {
                    launchOptions.setChannel("chrome");
                    browser = playwright.chromium().launch(launchOptions);
                    log.info("Successfully launched system Chrome fallback");
                } catch (Exception e3) {
                    try {
                        launchOptions.setChannel("msedge");
                        browser = playwright.chromium().launch(launchOptions);
                        log.info("Successfully launched system Microsoft Edge fallback");
                    } catch (Exception e4) {
                        log.error("All browser launch strategies failed. Error: {}", e4.getMessage());
                        throw new RuntimeException("Could not launch any browser. Ensure Chromium, Chrome, or Edge is installed.", e4);
                    }
                }
            }
        }
    }

    @PreDestroy
    public synchronized void cleanup() {
        try {
            if (browser != null) {
                browser.close();
                browser = null;
            }
        } catch (Exception ignored) {}

        try {
            if (playwright != null) {
                playwright.close();
                playwright = null;
            }
        } catch (Exception ignored) {}
    }
}
