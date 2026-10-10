package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.TestRunEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TestRunRepository extends JpaRepository<TestRunEntity, String> {
    List<TestRunEntity> findByTestIdOrderByStartedAtDesc(String testId);
    List<TestRunEntity> findAllByOrderByStartedAtDesc();
    long countByStatus(String status);
    long countByFinalResult(String finalResult);
}
