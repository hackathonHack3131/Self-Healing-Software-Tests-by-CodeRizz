package com.aegistest.selfhealing.controller;

import com.aegistest.selfhealing.dto.DashboardMetricsResponse;
import com.aegistest.selfhealing.service.DashboardService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping
    public ResponseEntity<DashboardMetricsResponse> getDashboard() {
        return ResponseEntity.ok(dashboardService.getDashboardMetrics());
    }
}
