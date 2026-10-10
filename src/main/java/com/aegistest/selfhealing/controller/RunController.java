package com.aegistest.selfhealing.controller;

import com.aegistest.selfhealing.dto.ReportResponse;
import com.aegistest.selfhealing.dto.TestRunResponse;
import com.aegistest.selfhealing.events.ExecutionEventPublisher;
import com.aegistest.selfhealing.service.ReportService;
import com.aegistest.selfhealing.service.TestManagementService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/runs")
public class RunController {

    private final TestManagementService testService;
    private final ReportService reportService;
    private final ExecutionEventPublisher eventPublisher;

    public RunController(TestManagementService testService,
                         ReportService reportService,
                         ExecutionEventPublisher eventPublisher) {
        this.testService = testService;
        this.reportService = reportService;
        this.eventPublisher = eventPublisher;
    }

    @GetMapping("/{id}")
    public ResponseEntity<TestRunResponse> getRun(@PathVariable String id) {
        return ResponseEntity.ok(testService.getRunById(id));
    }

    @GetMapping(value = "/{id}/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter getRunEvents(@PathVariable String id) {
        return eventPublisher.subscribe(id);
    }

    @GetMapping("/{id}/report")
    public ResponseEntity<ReportResponse> getRunReport(@PathVariable String id) {
        return ResponseEntity.ok(reportService.getReportByRunId(id));
    }

    @PostMapping("/{id}/cancel")
    public ResponseEntity<TestRunResponse> cancelRun(@PathVariable String id) {
        return ResponseEntity.ok(testService.cancelRun(id));
    }
}
