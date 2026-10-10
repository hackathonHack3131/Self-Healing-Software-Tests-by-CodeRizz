package com.aegistest.selfhealing.controller;

import com.aegistest.selfhealing.dto.TestCaseRequest;
import com.aegistest.selfhealing.dto.TestCaseResponse;
import com.aegistest.selfhealing.dto.TestRunResponse;
import com.aegistest.selfhealing.service.TestManagementService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tests")
public class TestController {

    private final TestManagementService testService;

    public TestController(TestManagementService testService) {
        this.testService = testService;
    }

    @GetMapping
    public ResponseEntity<List<TestCaseResponse>> getAllTests() {
        return ResponseEntity.ok(testService.getAllTests());
    }

    @PostMapping
    public ResponseEntity<TestCaseResponse> createTest(@Valid @RequestBody TestCaseRequest req) {
        TestCaseResponse created = testService.createTest(req);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TestCaseResponse> getTestById(@PathVariable String id) {
        return ResponseEntity.ok(testService.getTestById(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<TestCaseResponse> updateTest(@PathVariable String id, @RequestBody TestCaseRequest req) {
        return ResponseEntity.ok(testService.updateTest(id, req));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTest(@PathVariable String id) {
        testService.deleteTest(id);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{id}/run")
    public ResponseEntity<TestRunResponse> runTest(@PathVariable String id) {
        TestRunResponse run = testService.startTestRun(id);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(run);
    }
}
