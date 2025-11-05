-- AetherEdge Database Initialization Script
-- Creates necessary databases, extensions, and initial schema

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create additional databases for different services
CREATE DATABASE aetheredge_metrics;
CREATE DATABASE aetheredge_logs;
CREATE DATABASE aetheredge_analytics;

-- Connect to the main database
\c aetheredge;

-- Create schemas for different modules
CREATE SCHEMA IF NOT EXISTS brahma;
CREATE SCHEMA IF NOT EXISTS vishnu;
CREATE SCHEMA IF NOT EXISTS shiva;
CREATE SCHEMA IF NOT EXISTS lakshmi;
CREATE SCHEMA IF NOT EXISTS kali;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Create core tables for telemetry data
CREATE TABLE IF NOT EXISTS telemetry_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    labels JSONB,
    metadata JSONB
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('telemetry_data', 'timestamp', if_not_exists => TRUE);

-- Create index for efficient queries
CREATE INDEX IF NOT EXISTS idx_telemetry_source_time 
ON telemetry_data (source, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_telemetry_metric_time 
ON telemetry_data (metric_name, timestamp DESC);

-- Create GIN index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_telemetry_labels 
ON telemetry_data USING GIN (labels);

CREATE INDEX IF NOT EXISTS idx_telemetry_metadata 
ON telemetry_data USING GIN (metadata);

-- Create infrastructure monitoring tables
CREATE TABLE IF NOT EXISTS infrastructure_health (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    component_name VARCHAR(100) NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('healthy', 'warning', 'critical', 'unknown')),
    cpu_usage DOUBLE PRECISION,
    memory_usage DOUBLE PRECISION,
    disk_usage DOUBLE PRECISION,
    network_in DOUBLE PRECISION,
    network_out DOUBLE PRECISION,
    details JSONB
);

SELECT create_hypertable('infrastructure_health', 'timestamp', if_not_exists => TRUE);

-- Create security events table (Kali module)
CREATE TABLE IF NOT EXISTS kali.security_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    threat_level VARCHAR(20) NOT NULL CHECK (threat_level IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    metadata JSONB,
    remediation_actions TEXT[],
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'resolved', 'investigating')),
    resolved_at TIMESTAMPTZ,
    resolution TEXT
);

CREATE INDEX IF NOT EXISTS idx_security_events_time 
ON kali.security_events (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_security_events_level 
ON kali.security_events (threat_level, timestamp DESC);

-- Create AI blueprint execution logs (Brahma module)
CREATE TABLE IF NOT EXISTS brahma.blueprint_executions (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    blueprint_name VARCHAR(100) NOT NULL,
    cloud_provider VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    infrastructure_score DOUBLE PRECISION,
    cost_estimate DOUBLE PRECISION,
    compliance_score DOUBLE PRECISION,
    generated_resources JSONB,
    execution_logs TEXT,
    error_details TEXT,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_blueprint_executions_time 
ON brahma.blueprint_executions (timestamp DESC);

-- Create policy compliance tracking (Vishnu module)
CREATE TABLE IF NOT EXISTS vishnu.policy_compliance (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    policy_id VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    compliance_status VARCHAR(20) NOT NULL CHECK (compliance_status IN ('compliant', 'non_compliant', 'warning')),
    compliance_score DOUBLE PRECISION,
    violations JSONB,
    remediation_actions TEXT[],
    last_checked TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policy_compliance_time 
ON vishnu.policy_compliance (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_policy_compliance_status 
ON vishnu.policy_compliance (compliance_status, timestamp DESC);

-- Create AI healing operations (Shiva module)
CREATE TABLE IF NOT EXISTS shiva.healing_operations (
    id SERIAL PRIMARY KEY,
    operation_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    incident_type VARCHAR(50) NOT NULL,
    affected_resources TEXT[],
    anomaly_score DOUBLE PRECISION,
    healing_plan JSONB,
    execution_status VARCHAR(20) NOT NULL CHECK (execution_status IN ('pending', 'executing', 'completed', 'failed')),
    success_rate DOUBLE PRECISION,
    execution_logs TEXT,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_healing_operations_time 
ON shiva.healing_operations (timestamp DESC);

-- Create FinOps cost tracking (Lakshmi module)
CREATE TABLE IF NOT EXISTS lakshmi.cost_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cloud_provider VARCHAR(50) NOT NULL,
    account_id VARCHAR(100),
    service_name VARCHAR(100) NOT NULL,
    resource_id VARCHAR(200),
    cost_amount DOUBLE PRECISION NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    billing_period DATE NOT NULL,
    cost_category VARCHAR(50),
    tags JSONB,
    optimization_potential DOUBLE PRECISION
);

SELECT create_hypertable('lakshmi.cost_data', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_cost_data_provider_time 
ON lakshmi.cost_data (cloud_provider, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_cost_data_service_time 
ON lakshmi.cost_data (service_name, timestamp DESC);

-- Create analytics aggregation tables
CREATE TABLE IF NOT EXISTS analytics.daily_metrics (
    date DATE PRIMARY KEY,
    total_incidents INTEGER DEFAULT 0,
    resolved_incidents INTEGER DEFAULT 0,
    total_cost DOUBLE PRECISION DEFAULT 0,
    cost_savings DOUBLE PRECISION DEFAULT 0,
    compliance_score DOUBLE PRECISION DEFAULT 0,
    security_events INTEGER DEFAULT 0,
    infrastructure_health DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create monitoring alerts table
CREATE TABLE IF NOT EXISTS monitoring.alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(50) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    source VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    labels JSONB,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved')),
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_time 
ON monitoring.alerts (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_severity 
ON monitoring.alerts (severity, timestamp DESC);

-- Create stored procedures for common operations

-- Function to get current system health
CREATE OR REPLACE FUNCTION get_system_health()
RETURNS TABLE (
    component VARCHAR(100),
    status VARCHAR(20),
    last_update TIMESTAMPTZ,
    cpu_avg DOUBLE PRECISION,
    memory_avg DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ih.component_name,
        ih.status,
        MAX(ih.timestamp) as last_update,
        AVG(ih.cpu_usage) as cpu_avg,
        AVG(ih.memory_usage) as memory_avg
    FROM infrastructure_health ih
    WHERE ih.timestamp >= NOW() - INTERVAL '1 hour'
    GROUP BY ih.component_name, ih.status
    ORDER BY last_update DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get security threat summary
CREATE OR REPLACE FUNCTION get_security_summary()
RETURNS TABLE (
    threat_level VARCHAR(20),
    event_count BIGINT,
    latest_event TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        se.threat_level,
        COUNT(*) as event_count,
        MAX(se.timestamp) as latest_event
    FROM kali.security_events se
    WHERE se.status = 'active'
    GROUP BY se.threat_level
    ORDER BY 
        CASE se.threat_level
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END;
END;
$$ LANGUAGE plpgsql;

-- Function to get cost optimization opportunities
CREATE OR REPLACE FUNCTION get_cost_optimization_opportunities()
RETURNS TABLE (
    service_name VARCHAR(100),
    total_cost DOUBLE PRECISION,
    optimization_potential DOUBLE PRECISION,
    potential_savings DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cd.service_name,
        SUM(cd.cost_amount) as total_cost,
        AVG(cd.optimization_potential) as optimization_potential,
        SUM(cd.cost_amount * COALESCE(cd.optimization_potential, 0) / 100) as potential_savings
    FROM lakshmi.cost_data cd
    WHERE cd.timestamp >= NOW() - INTERVAL '30 days'
    GROUP BY cd.service_name
    HAVING SUM(cd.cost_amount * COALESCE(cd.optimization_potential, 0) / 100) > 0
    ORDER BY potential_savings DESC;
END;
$$ LANGUAGE plpgsql;

-- Create data retention policies
SELECT add_retention_policy('telemetry_data', INTERVAL '90 days');
SELECT add_retention_policy('infrastructure_health', INTERVAL '180 days');
SELECT add_retention_policy('lakshmi.cost_data', INTERVAL '730 days'); -- 2 years for cost data

-- Create continuous aggregates for performance
CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', timestamp) AS bucket,
    source,
    metric_name,
    AVG(metric_value) as avg_value,
    MAX(metric_value) as max_value,
    MIN(metric_value) as min_value,
    COUNT(*) as sample_count
FROM telemetry_data
GROUP BY bucket, source, metric_name;

-- Add refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Create users and permissions
CREATE USER aetheredge_readonly WITH PASSWORD 'readonly123';
CREATE USER aetheredge_app WITH PASSWORD 'app123';
CREATE USER aetheredge_analytics WITH PASSWORD 'analytics123';

-- Grant permissions
GRANT CONNECT ON DATABASE aetheredge TO aetheredge_readonly;
GRANT CONNECT ON DATABASE aetheredge TO aetheredge_app;
GRANT CONNECT ON DATABASE aetheredge TO aetheredge_analytics;

GRANT USAGE ON SCHEMA public, brahma, vishnu, shiva, lakshmi, kali, analytics, monitoring 
TO aetheredge_readonly;

GRANT SELECT ON ALL TABLES IN SCHEMA public, brahma, vishnu, shiva, lakshmi, kali, analytics, monitoring 
TO aetheredge_readonly;

GRANT USAGE ON SCHEMA public, brahma, vishnu, shiva, lakshmi, kali, analytics, monitoring 
TO aetheredge_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public, brahma, vishnu, shiva, lakshmi, kali, analytics, monitoring 
TO aetheredge_app;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public, brahma, vishnu, shiva, lakshmi, kali, analytics, monitoring 
TO aetheredge_app;

-- Grant analytics user broader permissions
GRANT ALL PRIVILEGES ON SCHEMA analytics TO aetheredge_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA public, brahma, vishnu, shiva, lakshmi, kali, monitoring 
TO aetheredge_analytics;

-- Initial data population
INSERT INTO analytics.daily_metrics (date) VALUES (CURRENT_DATE)
ON CONFLICT (date) DO NOTHING;

-- Log initialization completion
INSERT INTO monitoring.alerts (
    alert_id, alert_name, severity, source, message, status
) VALUES (
    'DB_INIT_' || EXTRACT(EPOCH FROM NOW())::TEXT,
    'Database Initialization Complete',
    'info',
    'database',
    'AetherEdge database has been successfully initialized with all schemas, tables, and functions.',
    'resolved'
);

COMMIT;
