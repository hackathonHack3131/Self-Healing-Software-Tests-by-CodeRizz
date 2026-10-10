package com.aegistest.selfhealing.controller;

import com.aegistest.selfhealing.dto.ReportResponse;
import com.aegistest.selfhealing.service.ReportService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.charset.StandardCharsets;
import java.util.List;

@RestController
@RequestMapping("/api/reports")
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    @GetMapping
    public ResponseEntity<List<ReportResponse>> getAllReports() {
        return ResponseEntity.ok(reportService.getAllReports());
    }

    @GetMapping("/{id}")
    public ResponseEntity<ReportResponse> getReportById(@PathVariable String id) {
        String runId = id.replace("report-", "");
        return ResponseEntity.ok(reportService.getReportByRunId(runId));
    }

    @GetMapping("/{id}/export")
    public ResponseEntity<byte[]> exportReport(@PathVariable String id) {
        String md = reportService.exportReportAsMarkdown(id);
        byte[] bytes = md.getBytes(StandardCharsets.UTF_8);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"report-" + id + ".md\"")
                .contentType(MediaType.TEXT_MARKDOWN)
                .body(bytes);
    }
}
