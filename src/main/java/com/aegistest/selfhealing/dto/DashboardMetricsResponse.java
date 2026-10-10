package com.aegistest.selfhealing.dto;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class DashboardMetricsResponse {
    private int totalTests;
    private int passedTests;
    private int failedTests;
    private int selfHealedTests;
    private double testSuccessRate;
    private double averageExecutionTimeMs;
    private double healingSuccessRate;
    private boolean isBackendConnected = true;
    private List<TestRunSummaryDto> recentRuns = new ArrayList<>();
    private TrendsDto trends = new TrendsDto();
    private List<Map<String, Object>> healingActivity = new ArrayList<>();
    private List<UiChangeDto> latestUiChanges = new ArrayList<>();
    private List<Map<String, Object>> recentFailures = new ArrayList<>();

    public static class TrendsDto {
        private List<String> dates = new ArrayList<>();
        private List<Double> passRates = new ArrayList<>();
        private List<Double> healedRates = new ArrayList<>();
        private List<Double> failureRates = new ArrayList<>();

        public TrendsDto() {}

        public List<String> getDates() { return dates; }
        public void setDates(List<String> dates) { this.dates = dates; }

        public List<Double> getPassRates() { return passRates; }
        public void setPassRates(List<Double> passRates) { this.passRates = passRates; }

        public List<Double> getHealedRates() { return healedRates; }
        public void setHealedRates(List<Double> healedRates) { this.healedRates = healedRates; }

        public List<Double> getFailureRates() { return failureRates; }
        public void setFailureRates(List<Double> failureRates) { this.failureRates = failureRates; }
    }

    public DashboardMetricsResponse() {}

    public int getTotalTests() { return totalTests; }
    public void setTotalTests(int totalTests) { this.totalTests = totalTests; }

    public int getPassedTests() { return passedTests; }
    public void setPassedTests(int passedTests) { this.passedTests = passedTests; }

    public int getFailedTests() { return failedTests; }
    public void setFailedTests(int failedTests) { this.failedTests = failedTests; }

    public int getSelfHealedTests() { return selfHealedTests; }
    public void setSelfHealedTests(int selfHealedTests) { this.selfHealedTests = selfHealedTests; }

    public double getTestSuccessRate() { return testSuccessRate; }
    public void setTestSuccessRate(double testSuccessRate) { this.testSuccessRate = testSuccessRate; }

    public double getAverageExecutionTimeMs() { return averageExecutionTimeMs; }
    public void setAverageExecutionTimeMs(double averageExecutionTimeMs) { this.averageExecutionTimeMs = averageExecutionTimeMs; }

    public double getHealingSuccessRate() { return healingSuccessRate; }
    public void setHealingSuccessRate(double healingSuccessRate) { this.healingSuccessRate = healingSuccessRate; }

    public boolean isBackendConnected() { return isBackendConnected; }
    public void setBackendConnected(boolean backendConnected) { isBackendConnected = backendConnected; }

    public List<TestRunSummaryDto> getRecentRuns() { return recentRuns; }
    public void setRecentRuns(List<TestRunSummaryDto> recentRuns) { this.recentRuns = recentRuns; }

    public TrendsDto getTrends() { return trends; }
    public void setTrends(TrendsDto trends) { this.trends = trends; }

    public List<Map<String, Object>> getHealingActivity() { return healingActivity; }
    public void setHealingActivity(List<Map<String, Object>> healingActivity) { this.healingActivity = healingActivity; }

    public List<UiChangeDto> getLatestUiChanges() { return latestUiChanges; }
    public void setLatestUiChanges(List<UiChangeDto> latestUiChanges) { this.latestUiChanges = latestUiChanges; }

    public List<Map<String, Object>> getRecentFailures() { return recentFailures; }
    public void setRecentFailures(List<Map<String, Object>> recentFailures) { this.recentFailures = recentFailures; }
}
