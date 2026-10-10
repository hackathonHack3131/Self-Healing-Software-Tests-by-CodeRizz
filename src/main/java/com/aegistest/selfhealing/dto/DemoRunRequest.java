package com.aegistest.selfhealing.dto;

public class DemoRunRequest {
    private String version = "A";
    private boolean selfHealing = true;

    public DemoRunRequest() {}

    public DemoRunRequest(String version, boolean selfHealing) {
        this.version = version;
        this.selfHealing = selfHealing;
    }

    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }

    public boolean isSelfHealing() { return selfHealing; }
    public void setSelfHealing(boolean selfHealing) { this.selfHealing = selfHealing; }
}
