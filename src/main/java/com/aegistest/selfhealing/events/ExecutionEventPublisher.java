package com.aegistest.selfhealing.events;

import com.aegistest.selfhealing.entity.ExecutionEventEntity;
import com.aegistest.selfhealing.repository.ExecutionEventRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Component
public class ExecutionEventPublisher {

    private static final Logger log = LoggerFactory.getLogger(ExecutionEventPublisher.class);

    private final Map<String, List<SseEmitter>> emitters = new ConcurrentHashMap<>();
    private final ExecutionEventRepository eventRepository;
    private final ObjectMapper objectMapper;

    public ExecutionEventPublisher(ExecutionEventRepository eventRepository, ObjectMapper objectMapper) {
        this.eventRepository = eventRepository;
        this.objectMapper = objectMapper;
    }

    /**
     * Registers a new SSE client for a given run ID.
     */
    public SseEmitter subscribe(String runId) {
        // 10 minutes timeout
        SseEmitter emitter = new SseEmitter(600_000L);

        emitters.computeIfAbsent(runId, k -> new CopyOnWriteArrayList<>()).add(emitter);

        emitter.onCompletion(() -> removeEmitter(runId, emitter));
        emitter.onTimeout(() -> removeEmitter(runId, emitter));
        emitter.onError(e -> removeEmitter(runId, emitter));

        // Send initial connect handshake
        try {
            emitter.send(SseEmitter.event()
                    .name("connected")
                    .data(Map.of("runId", runId, "message", "Connected to live execution event stream")));
        } catch (IOException e) {
            removeEmitter(runId, emitter);
        }

        return emitter;
    }

    /**
     * Publishes a live execution event to all connected listeners and persists to database.
     */
    public void publish(String runId, String eventType, Map<String, Object> payload) {
        ExecutionEventPayload event = new ExecutionEventPayload(runId, eventType);
        if (payload != null) {
            event.getData().putAll(payload);
        }

        // Persist to database
        try {
            String json = objectMapper.writeValueAsString(event);
            ExecutionEventEntity entity = new ExecutionEventEntity(
                    "evt-" + UUID.randomUUID().toString(),
                    runId,
                    eventType,
                    json,
                    Instant.now()
            );
            eventRepository.save(entity);
        } catch (Exception e) {
            log.error("Failed to persist execution event: {}", e.getMessage());
        }

        // Dispatch to SSE emitters
        List<SseEmitter> runEmitters = emitters.get(runId);
        if (runEmitters != null && !runEmitters.isEmpty()) {
            for (SseEmitter emitter : runEmitters) {
                try {
                    emitter.send(SseEmitter.event()
                            .name(eventType)
                            .data(event));
                } catch (Exception e) {
                    removeEmitter(runId, emitter);
                }
            }
        }
    }

    private void removeEmitter(String runId, SseEmitter emitter) {
        List<SseEmitter> list = emitters.get(runId);
        if (list != null) {
            list.remove(emitter);
            if (list.isEmpty()) {
                emitters.remove(runId);
            }
        }
    }
}
