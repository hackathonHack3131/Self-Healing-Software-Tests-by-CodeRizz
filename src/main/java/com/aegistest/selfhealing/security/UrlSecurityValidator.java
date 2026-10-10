package com.aegistest.selfhealing.security;

import org.springframework.stereotype.Component;

import java.net.URI;
import java.util.Set;

@Component
public class UrlSecurityValidator {

    private static final Set<String> BLOCKED_HOSTS = Set.of(
            "169.254.169.254", // AWS/Cloud metadata
            "metadata.google.internal",
            "instance-data"
    );

    private static final Set<String> ALLOWED_SCHEMES = Set.of("http", "https");

    /**
     * Validates whether a target URL is permissible for testing.
     * Allows localhost, 127.0.0.1, standard demo domains, while blocking cloud metadata and file/internal protocols.
     */
    public boolean isValidTargetUrl(String urlString) {
        if (urlString == null || urlString.trim().isEmpty()) {
            return false;
        }

        try {
            URI uri = URI.create(urlString.trim());
            String scheme = uri.getScheme();
            if (scheme == null || !ALLOWED_SCHEMES.contains(scheme.toLowerCase())) {
                return false;
            }

            String host = uri.getHost();
            if (host == null || host.trim().isEmpty()) {
                return false;
            }

            if (BLOCKED_HOSTS.contains(host.toLowerCase())) {
                return false;
            }

            // Reject internal AWS/GCP metadata query paths
            if (uri.getPath() != null && uri.getPath().contains("latest/meta-data")) {
                return false;
            }

            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
