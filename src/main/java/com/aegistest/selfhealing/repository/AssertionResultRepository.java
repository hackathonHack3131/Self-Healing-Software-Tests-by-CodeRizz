package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.AssertionResultEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AssertionResultRepository extends JpaRepository<AssertionResultEntity, String> {
    List<AssertionResultEntity> findByRunIdOrderByCreatedAtAsc(String runId);
}
