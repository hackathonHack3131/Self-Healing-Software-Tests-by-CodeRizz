package com.aegistest.selfhealing.dto;

import java.util.HashMap;
import java.util.Map;

public class CandidateElementDto {
    private String id;
    private String selector;
    private String tag;
    private String text;
    private String role;
    private Map<String, String> attributes = new HashMap<>();
    private double confidence;
    private MatchBreakdown matchBreakdown = new MatchBreakdown();
    private String reasoning;

    public static class MatchBreakdown {
        private double semanticIntent;
        private double textSimilarity;
        private double domContext;
        private double visualPosition;

        public MatchBreakdown() {}

        public MatchBreakdown(double semanticIntent, double textSimilarity, double domContext, double visualPosition) {
            this.semanticIntent = semanticIntent;
            this.textSimilarity = textSimilarity;
            this.domContext = domContext;
            this.visualPosition = visualPosition;
        }

        public double getSemanticIntent() { return semanticIntent; }
        public void setSemanticIntent(double semanticIntent) { this.semanticIntent = semanticIntent; }

        public double getTextSimilarity() { return textSimilarity; }
        public void setTextSimilarity(double textSimilarity) { this.textSimilarity = textSimilarity; }

        public double getDomContext() { return domContext; }
        public void setDomContext(double domContext) { this.domContext = domContext; }

        public double getVisualPosition() { return visualPosition; }
        public void setVisualPosition(double visualPosition) { this.visualPosition = visualPosition; }
    }

    public CandidateElementDto() {}

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getSelector() { return selector; }
    public void setSelector(String selector) { this.selector = selector; }

    public String getTag() { return tag; }
    public void setTag(String tag) { this.tag = tag; }

    public String getText() { return text; }
    public void setText(String text) { this.text = text; }

    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }

    public Map<String, String> getAttributes() { return attributes; }
    public void setAttributes(Map<String, String> attributes) { this.attributes = attributes; }

    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }

    public MatchBreakdown getMatchBreakdown() { return matchBreakdown; }
    public void setMatchBreakdown(MatchBreakdown matchBreakdown) { this.matchBreakdown = matchBreakdown; }

    public String getReasoning() { return reasoning; }
    public void setReasoning(String reasoning) { this.reasoning = reasoning; }
}
