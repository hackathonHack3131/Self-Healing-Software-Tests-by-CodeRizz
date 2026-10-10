-- AegisTest Database Schema V1

CREATE TABLE IF NOT EXISTS test_cases (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    target_url VARCHAR(1024) NOT NULL,
    intent TEXT NOT NULL,
    environment VARCHAR(32) DEFAULT 'staging',
    browser VARCHAR(32) DEFAULT 'chromium',
    self_healing_enabled BOOLEAN DEFAULT TRUE,
    max_healing_attempts INT DEFAULT 3,
    expected_outcome TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run_at TIMESTAMP NULL,
    status VARCHAR(32) DEFAULT 'never_run'
);

CREATE TABLE IF NOT EXISTS test_runs (
    id VARCHAR(64) PRIMARY KEY,
    test_id VARCHAR(64) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    target_url VARCHAR(1024) NOT NULL,
    intent TEXT NOT NULL,
    status VARCHAR(32) NOT NULL,
    current_step_index INT DEFAULT 0,
    total_steps INT DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    duration_ms BIGINT DEFAULT 0,
    initial_result VARCHAR(32) NULL,
    final_result VARCHAR(32) NULL,
    healing_count INT DEFAULT 0,
    is_simulated BOOLEAN DEFAULT FALSE,
    current_screenshot TEXT NULL,
    final_verified BOOLEAN DEFAULT FALSE,
    final_evidence_text TEXT NULL,
    final_target_selector VARCHAR(255) NULL,
    error_summary TEXT NULL,
    CONSTRAINT fk_test_run_test_case FOREIGN KEY (test_id) REFERENCES test_cases(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS execution_steps (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    step_number INT NOT NULL,
    description TEXT,
    original_action VARCHAR(255) NOT NULL,
    original_selector VARCHAR(512),
    repaired_action VARCHAR(255) NULL,
    repaired_selector VARCHAR(512) NULL,
    status VARCHAR(32) NOT NULL,
    duration_ms BIGINT DEFAULT 0,
    error_message TEXT NULL,
    screenshot_before TEXT NULL,
    screenshot_after TEXT NULL,
    CONSTRAINT fk_execution_step_run FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS healing_attempts (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    step_id VARCHAR(64) NOT NULL,
    step_number INT NOT NULL,
    failed_selector VARCHAR(512) NOT NULL,
    failure_reason TEXT NOT NULL,
    strategy VARCHAR(64) NOT NULL,
    repaired_action VARCHAR(255) NOT NULL,
    repaired_selector VARCHAR(512) NOT NULL,
    confidence_score DOUBLE NOT NULL,
    duration_ms BIGINT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    candidates_json MEDIUMTEXT NULL,
    selected_candidate_json MEDIUMTEXT NULL,
    attempt_status VARCHAR(32) DEFAULT 'SUCCESS',
    repair_explanation TEXT NULL,
    CONSTRAINT fk_healing_attempt_run FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assertion_results (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    assertion_type VARCHAR(64),
    expected_outcome TEXT,
    actual_outcome TEXT,
    passed BOOLEAN NOT NULL,
    evidence TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assertion_run FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS execution_events (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload_json MEDIUMTEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_event_run FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ui_changes (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NULL,
    element_description VARCHAR(255) NOT NULL,
    change_type VARCHAR(64) NOT NULL,
    previous_dom_snippet TEXT,
    new_dom_snippet TEXT,
    impact_score VARCHAR(32) DEFAULT 'medium',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artifacts (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    artifact_type VARCHAR(64) NOT NULL,
    storage_path VARCHAR(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_artifact_run FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE INDEX idx_runs_test_id ON test_runs(test_id);
CREATE INDEX idx_steps_run_id ON execution_steps(run_id);
CREATE INDEX idx_healing_run_id ON healing_attempts(run_id);
CREATE INDEX idx_events_run_id ON execution_events(run_id);
