package com.aegistest.selfhealing.inspection;

import java.util.HashMap;
import java.util.Map;

public class InspectedElement {
    private String tag;
    private String role;
    private String accessibleName;
    private String associatedLabel;
    private String visibleText;
    private String inputType;
    private String placeholder;
    private String safeValue;
    private boolean visible = true;
    private boolean enabled = true;
    private String domPath;
    private String parentTag;
    private String containerClass;
    private String testId; // data-testid or data-test
    private String id;
    private String name;
    private String cssClasses;
    private Map<String, String> attributes = new HashMap<>();

    // Bounding Box coordinates
    private double x;
    private double y;
    private double width;
    private double height;

    // Generated candidate locators in priority order
    private String primaryLocator;
    private String accessibleLocator;
    private String textLocator;
    private String testIdLocator;
    private String cssLocator;
    private String xpathLocator;

    public InspectedElement() {}

    // Getters and Setters
    public String getTag() { return tag; }
    public void setTag(String tag) { this.tag = tag; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public String getAccessibleName() { return accessibleName; }
    public void setAccessibleName(String accessibleName) { this.accessibleName = accessibleName; }

    public String getAssociatedLabel() { return associatedLabel; }
    public void setAssociatedLabel(String associatedLabel) { this.associatedLabel = associatedLabel; }

    public String getVisibleText() { return visibleText; }
    public void setVisibleText(String visibleText) { this.visibleText = visibleText; }

    public String getInputType() { return inputType; }
    public void setInputType(String inputType) { this.inputType = inputType; }

    public String getPlaceholder() { return placeholder; }
    public void setPlaceholder(String placeholder) { this.placeholder = placeholder; }

    public String getSafeValue() { return safeValue; }
    public void setSafeValue(String safeValue) { this.safeValue = safeValue; }

    public boolean isVisible() { return visible; }
    public void setVisible(boolean visible) { this.visible = visible; }

    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }

    public String getDomPath() { return domPath; }
    public void setDomPath(String domPath) { this.domPath = domPath; }

    public String getParentTag() { return parentTag; }
    public void setParentTag(String parentTag) { this.parentTag = parentTag; }

    public String getContainerClass() { return containerClass; }
    public void setContainerClass(String containerClass) { this.containerClass = containerClass; }

    public String getTestId() { return testId; }
    public void setTestId(String testId) { this.testId = testId; }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCssClasses() { return cssClasses; }
    public void setCssClasses(String cssClasses) { this.cssClasses = cssClasses; }

    public Map<String, String> getAttributes() { return attributes; }
    public void setAttributes(Map<String, String> attributes) { this.attributes = attributes; }

    public double getX() { return x; }
    public void setX(double x) { this.x = x; }

    public double getY() { return y; }
    public void setY(double y) { this.y = y; }

    public double getWidth() { return width; }
    public void setWidth(double width) { this.width = width; }

    public double getHeight() { return height; }
    public void setHeight(double height) { this.height = height; }

    public String getPrimaryLocator() { return primaryLocator; }
    public void setPrimaryLocator(String primaryLocator) { this.primaryLocator = primaryLocator; }

    public String getAccessibleLocator() { return accessibleLocator; }
    public void setAccessibleLocator(String accessibleLocator) { this.accessibleLocator = accessibleLocator; }

    public String getTextLocator() { return textLocator; }
    public void setTextLocator(String textLocator) { this.textLocator = textLocator; }

    public String getTestIdLocator() { return testIdLocator; }
    public void setTestIdLocator(String testIdLocator) { this.testIdLocator = testIdLocator; }

    public String getCssLocator() { return cssLocator; }
    public void setCssLocator(String cssLocator) { this.cssLocator = cssLocator; }

    public String getXpathLocator() { return xpathLocator; }
    public void setXpathLocator(String xpathLocator) { this.xpathLocator = xpathLocator; }
}
