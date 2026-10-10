package com.aegistest.selfhealing;

import com.aegistest.selfhealing.entity.TestRunEntity;
import com.aegistest.selfhealing.service.TestManagementService;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ReportAndLifecycleTest {

    @Test
    void testDistinguishesPassedFromHealed() {
        TestRunEntity normalPassedRun = new TestRunEntity();
        normalPassedRun.setStatus("passed");
        normalPassedRun.setInitialResult("passed");
        normalPassedRun.setFinalResult("passed");
        normalPassedRun.setHealingCount(0);

        TestRunEntity healedRun = new TestRunEntity();
        healedRun.setStatus("passed");
        healedRun.setInitialResult("failed");
        healedRun.setFinalResult("healed");
        healedRun.setHealingCount(1);

        assertEquals("passed", normalPassedRun.getFinalResult());
        assertEquals(0, normalPassedRun.getHealingCount());

        assertEquals("healed", healedRun.getFinalResult());
        assertEquals("failed", healedRun.getInitialResult());
        assertEquals(1, healedRun.getHealingCount());
    }
}
