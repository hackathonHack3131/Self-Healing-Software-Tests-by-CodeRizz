package com.aegistest.selfhealing.dto;

import java.util.ArrayList;
import java.util.List;

public class DemoComparisonResponse {
    private VersionDetails versionA;
    private VersionDetails versionB;
    private List<StructuralDiff> structuralDifferences = new ArrayList<>();

    public static class VersionDetails {
        private String checkoutSelector;
        private String domTree;
        private String buttonText;
        private String containerClass;

        public VersionDetails() {}

        public VersionDetails(String checkoutSelector, String buttonText, String containerClass, String domTree) {
            this.checkoutSelector = checkoutSelector;
            this.buttonText = buttonText;
            this.containerClass = containerClass;
            this.domTree = domTree;
        }

        public String getCheckoutSelector() { return checkoutSelector; }
        public void setCheckoutSelector(String checkoutSelector) { this.checkoutSelector = checkoutSelector; }

        public String getDomTree() { return domTree; }
        public void setDomTree(String domTree) { this.domTree = domTree; }

        public String getButtonText() { return buttonText; }
        public void setButtonText(String buttonText) { this.buttonText = buttonText; }

        public String getContainerClass() { return containerClass; }
        public void setContainerClass(String containerClass) { this.containerClass = containerClass; }
    }

    public static class StructuralDiff {
        private String field;
        private String impact;
        private String original;
        private String modified;

        public StructuralDiff() {}

        public StructuralDiff(String field, String impact, String original, String modified) {
            this.field = field;
            this.impact = impact;
            this.original = original;
            this.modified = modified;
        }

        public String getField() { return field; }
        public void setField(String field) { this.field = field; }

        public String getImpact() { return impact; }
        public void setImpact(String impact) { this.impact = impact; }

        public String getOriginal() { return original; }
        public void setOriginal(String original) { this.original = original; }

        public String getModified() { return modified; }
        public void setModified(String modified) { this.modified = modified; }
    }

    public DemoComparisonResponse() {}

    public VersionDetails getVersionA() { return versionA; }
    public void setVersionA(VersionDetails versionA) { this.versionA = versionA; }

    public VersionDetails getVersionB() { return versionB; }
    public void setVersionB(VersionDetails versionB) { this.versionB = versionB; }

    public List<StructuralDiff> getStructuralDifferences() { return structuralDifferences; }
    public void setStructuralDifferences(List<StructuralDiff> structuralDifferences) { this.structuralDifferences = structuralDifferences; }
}
