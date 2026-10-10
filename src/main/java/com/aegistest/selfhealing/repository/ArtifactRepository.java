package com.aegistest.selfhealing.repository;

import com.aegistest.selfhealing.entity.ArtifactEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ArtifactRepository extends JpaRepository<ArtifactEntity, String> {
    List<ArtifactEntity> findByRunIdOrderByCreatedAtAsc(String runId);
}
