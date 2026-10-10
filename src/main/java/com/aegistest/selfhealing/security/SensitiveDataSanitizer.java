package com.aegistest.selfhealing.security;

import org.springframework.stereotype.Component;

import java.util.regex.Pattern;

@Component
public class SensitiveDataSanitizer {

    private static final Pattern CARD_PATTERN = Pattern.compile("\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\\b");
    private static final Pattern CVV_PATTERN = Pattern.compile("(?i)(cvv|cvc)[:= ]+([0-9]{3,4})");

    /**
     * Masks sensitive tokens and card credentials in logs or payloads
     */
    public String sanitize(String input) {
        if (input == null) return null;

        String sanitized = CARD_PATTERN.matcher(input).replaceAll("4242 •••• •••• 4242");
        sanitized = CVV_PATTERN.matcher(sanitized).replaceAll("$1: •••");
        return sanitized;
    }
}
