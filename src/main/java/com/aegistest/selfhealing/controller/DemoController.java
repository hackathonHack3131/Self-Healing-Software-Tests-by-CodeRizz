package com.aegistest.selfhealing.controller;

import com.aegistest.selfhealing.dto.DemoComparisonResponse;
import com.aegistest.selfhealing.dto.DemoRunRequest;
import com.aegistest.selfhealing.dto.TestRunResponse;
import com.aegistest.selfhealing.service.DemoManagerService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/demo")
public class DemoController {

    private final DemoManagerService demoService;

    public DemoController(DemoManagerService demoService) {
        this.demoService = demoService;
    }

    @PostMapping("/reset")
    public ResponseEntity<Map<String, Object>> resetDemo() {
        return ResponseEntity.ok(demoService.resetToVersionA());
    }

    @PostMapping("/version-b")
    public ResponseEntity<Map<String, Object>> setVersionB() {
        return ResponseEntity.ok(demoService.switchToVersionB());
    }

    @PostMapping("/run")
    public ResponseEntity<TestRunResponse> runDemo(@RequestBody(required = false) DemoRunRequest req) {
        if (req == null) req = new DemoRunRequest("A", true);
        return ResponseEntity.ok(demoService.runDemoWorkflow(req));
    }

    @GetMapping("/compare")
    public ResponseEntity<DemoComparisonResponse> compareDemo() {
        return ResponseEntity.ok(demoService.getDemoComparison());
    }
}
