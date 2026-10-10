package com.aegistest.selfhealing.browser;

import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.ScreenshotType;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Base64;
import java.util.UUID;

public class BrowserContextSession implements AutoCloseable {

    private final String sessionId;
    private final BrowserContext context;
    private final Page page;
    private final String artifactDir;

    public BrowserContextSession(BrowserContext context, String artifactDir) {
        this.sessionId = UUID.randomUUID().toString();
        this.context = context;
        this.page = context.newPage();
        this.artifactDir = artifactDir != null ? artifactDir : "./artifacts";

        // Setup base directory
        new File(this.artifactDir).mkdirs();
    }

    public Page getPage() {
        return page;
    }

    public BrowserContext getContext() {
        return context;
    }

    public String getSessionId() {
        return sessionId;
    }

    /**
     * Captures a screenshot as Base64 data URL for instant streaming to SSE / Frontend
     */
    public String captureScreenshotBase64() {
        try {
            byte[] bytes = page.screenshot(new Page.ScreenshotOptions().setType(ScreenshotType.JPEG).setQuality(70));
            return "data:image/jpeg;base64," + Base64.getEncoder().encodeToString(bytes);
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * Saves a screenshot to disk as an artifact and returns the file path
     */
    public String saveScreenshotArtifact(String stepName) {
        try {
            String filename = "screenshot_" + System.currentTimeMillis() + "_" + stepName.replaceAll("[^a-zA-Z0-9.-]", "_") + ".png";
            Path targetPath = Paths.get(artifactDir, filename);
            byte[] bytes = page.screenshot(new Page.ScreenshotOptions().setType(ScreenshotType.PNG));
            Files.write(targetPath, bytes);
            return targetPath.toAbsolutePath().toString();
        } catch (Exception e) {
            return null;
        }
    }

    @Override
    public void close() {
        try {
            if (page != null && !page.isClosed()) {
                page.close();
            }
        } catch (Exception ignored) {}

        try {
            if (context != null) {
                context.close();
            }
        } catch (Exception ignored) {}
    }
}
