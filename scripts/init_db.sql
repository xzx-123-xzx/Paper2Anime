CREATE DATABASE IF NOT EXISTS paper2anime CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE paper2anime;

-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    document_id VARCHAR(36),
    settings JSON,
    status VARCHAR(50) DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    current_stage VARCHAR(100),
    script TEXT,
    storyboard JSON,
    characters JSON,
    final_video_url VARCHAR(500),
    thumbnail_url VARCHAR(500),
    error_message TEXT,
    cost_estimate DECIMAL(10, 2) DEFAULT 0.0,
    cost_actual DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_type VARCHAR(20),
    file_size BIGINT,
    parsed_content JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- 工作流表
CREATE TABLE IF NOT EXISTS workflows (
    workflow_id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    current_node VARCHAR(100),
    node_statuses JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_project_id (project_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);
