package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.TestCaseEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TestCaseRepository extends JpaRepository<TestCaseEntity, String> {
    List<TestCaseEntity> findAllByOrderByCreatedAtDesc();
}
