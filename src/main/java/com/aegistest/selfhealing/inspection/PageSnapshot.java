package com.aegistest.selfhealing.inspection;

import java.util.ArrayList;
import java.util.List;

public class PageSnapshot {
    private String url;
    private String title;
    private String domHtml;
    private List<InspectedElement> elements = new ArrayList<>();
    private String screenshotBase64;
    private long capturedAtMs;

    public PageSnapshot() {}

    public PageSnapshot(String url, String title) {
        this.url = url;
        this.title = title;
        this.capturedAtMs = System.currentTimeMillis();
    }

    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDomHtml() { return domHtml; }
    public void setDomHtml(String domHtml) { this.domHtml = domHtml; }

    public List<InspectedElement> getElements() { return elements; }
    public void setElements(List<InspectedElement> elements) { this.elements = elements; }

    public String getScreenshotBase64() { return screenshotBase64; }
    public void setScreenshotBase64(String screenshotBase64) { this.screenshotBase64 = screenshotBase64; }

    public long getCapturedAtMs() { return capturedAtMs; }
    public void setCapturedAtMs(long capturedAtMs) { this.capturedAtMs = capturedAtMs; }
}
