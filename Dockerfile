# Multi-stage Dockerfile for AegisTest Self-Healing Engine
FROM eclipse-temurin:21-jdk-jammy AS builder

WORKDIR /app
COPY pom.xml .
COPY src ./src

# Install maven and package without tests for fast build
RUN apt-get update && apt-get install -y maven
RUN mvn clean package -DskipTests

# Runtime stage with Playwright prerequisites
FROM mcr.microsoft.com/playwright/java:v1.47.0-jammy

WORKDIR /app

# Copy the built spring boot application
COPY --from=builder /app/target/self-healing-engine-1.0.0.jar app.jar

# Setup artifact storage directory
RUN mkdir -p /app/artifacts

EXPOSE 8000

ENV PORT=8000
ENV ARTIFACTS_DIR=/app/artifacts
ENV BROWSER_HEADLESS=true

ENTRYPOINT ["java", "-jar", "app.jar"]
