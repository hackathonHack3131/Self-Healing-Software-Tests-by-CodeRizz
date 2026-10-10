package com.aegistest.selfhealing.execution;

public class StepExecutionResult {
    private boolean success;
    private long durationMs;
    private String errorMessage;
    private String screenshotBefore;
    private String screenshotAfter;

    public StepExecutionResult() {}

    public static StepExecutionResult passed(long durationMs, String screenshotAfter) {
        StepExecutionResult res = new StepExecutionResult();
        res.success = true;
        res.durationMs = durationMs;
        res.screenshotAfter = screenshotAfter;
        return res;
    }

    public static StepExecutionResult failed(long durationMs, String errorMessage, String screenshotAfter) {
        StepExecutionResult res = new StepExecutionResult();
        res.success = false;
        res.durationMs = durationMs;
        res.errorMessage = errorMessage;
        res.screenshotAfter = screenshotAfter;
        return res;
    }

    public boolean isSuccess() { return success; }
    public long getDurationMs() { return durationMs; }
    public String getErrorMessage() { return errorMessage; }
    public String getScreenshotBefore() { return screenshotBefore; }
    public void setScreenshotBefore(String screenshotBefore) { this.screenshotBefore = screenshotBefore; }
    public String getScreenshotAfter() { return screenshotAfter; }
}
