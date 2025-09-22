-- Create analyst_profile table with all required columns
-- This script creates the missing analyst_profile table for the EC2 deployment

CREATE TABLE IF NOT EXISTS analyst_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    full_name VARCHAR(200),
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    analyst_id VARCHAR(50) UNIQUE,
    last_login DATETIME,
    login_count INTEGER DEFAULT 0,
    university_name VARCHAR(200),
    age INTEGER,
    date_of_birth DATE,
    department VARCHAR(100),
    specialization VARCHAR(200),
    experience_years INTEGER,
    certifications TEXT,
    specializations TEXT,
    sebi_registration VARCHAR(100),
    bio TEXT,
    brief_description TEXT,
    profile_image VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    plan VARCHAR(50) DEFAULT 'free',
    daily_usage_date DATE,
    daily_usage_count INTEGER DEFAULT 0,
    plan_notes TEXT,
    plan_expires_at DATETIME,
    daily_llm_prompt_count INTEGER DEFAULT 0,
    daily_llm_token_count INTEGER DEFAULT 0,
    daily_run_count INTEGER DEFAULT 0,
    corporate_field VARCHAR(100),
    field_specialization VARCHAR(200),
    talent_program_level VARCHAR(50),
    total_reports INTEGER DEFAULT 0,
    avg_quality_score FLOAT DEFAULT 0.0,
    improvement_trend VARCHAR(20) DEFAULT 'stable',
    last_report_date DATETIME
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_analyst_email ON analyst_profile(email);
CREATE INDEX IF NOT EXISTS idx_analyst_id ON analyst_profile(analyst_id);
CREATE INDEX IF NOT EXISTS idx_analyst_active ON analyst_profile(is_active);