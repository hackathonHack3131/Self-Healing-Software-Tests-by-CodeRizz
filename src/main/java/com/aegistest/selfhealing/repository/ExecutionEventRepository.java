package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.ExecutionEventEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ExecutionEventRepository extends JpaRepository<ExecutionEventEntity, String> {
    List<ExecutionEventEntity> findByRunIdOrderByTimestampAsc(String runId);
}
