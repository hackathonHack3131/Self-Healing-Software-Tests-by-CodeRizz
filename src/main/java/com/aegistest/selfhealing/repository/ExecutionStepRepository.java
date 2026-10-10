package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.ExecutionStepEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ExecutionStepRepository extends JpaRepository<ExecutionStepEntity, String> {
    List<ExecutionStepEntity> findByRunIdOrderByStepNumberAsc(String runId);
}
