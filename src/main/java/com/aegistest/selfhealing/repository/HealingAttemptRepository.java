package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.HealingAttemptEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface HealingAttemptRepository extends JpaRepository<HealingAttemptEntity, String> {
    List<HealingAttemptEntity> findByRunIdOrderByTimestampAsc(String runId);
    List<HealingAttemptEntity> findByRunIdAndStepNumber(String runId, int stepNumber);
}
