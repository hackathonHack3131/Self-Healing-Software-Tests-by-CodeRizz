package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.UiChangeEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UiChangeRepository extends JpaRepository<UiChangeEntity, String> {
    List<UiChangeEntity> findByRunIdOrderByDetectedAtDesc(String runId);
    List<UiChangeEntity> findTop10ByOrderByDetectedAtDesc();
}
