package com.aegistest.selfhealing;

import com.aegistest.selfhealing.security.UrlSecurityValidator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class UrlSecurityValidatorTest {

    private UrlSecurityValidator validator;

    @BeforeEach
    void setUp() {
        validator = new UrlSecurityValidator();
    }

    @Test
    void testPermitsValidLocalAndDemoUrls() {
        assertTrue(validator.isValidTargetUrl("http://localhost:5173"));
        assertTrue(validator.isValidTargetUrl("http://localhost:8000/demo/index.html"));
        assertTrue(validator.isValidTargetUrl("http://127.0.0.1:3000"));
        assertTrue(validator.isValidTargetUrl("https://example.com/checkout"));
    }

    @Test
    void testBlocksCloudMetadataAndSSRF() {
        assertFalse(validator.isValidTargetUrl("http://169.254.169.254/latest/meta-data/"));
        assertFalse(validator.isValidTargetUrl("http://metadata.google.internal/computeMetadata/v1/"));
        assertFalse(validator.isValidTargetUrl("file:///etc/passwd"));
        assertFalse(validator.isValidTargetUrl("ftp://localhost/script.sh"));
        assertFalse(validator.isValidTargetUrl(""));
        assertFalse(validator.isValidTargetUrl(null));
    }
}
