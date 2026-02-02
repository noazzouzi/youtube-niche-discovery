-- =====================================================
-- YOUTUBE NICHE DISCOVERY ENGINE - DATABASE SCHEMA
-- =====================================================
-- Version: 1.0
-- Database: PostgreSQL 14+
-- Features: JSONB, UUID, Partitioning, Full-Text Search
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =====================================================
-- CORE TABLES
-- =====================================================

-- Users table for authentication and authorization
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'premium')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}',
    
    -- Indexes
    CONSTRAINT users_email_valid CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Categories for organizing niches
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    color VARCHAR(7), -- Hex color code
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_name_trgm ON categories USING gin(name gin_trgm_ops);

-- Data sources configuration
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL, -- 'youtube', 'tiktok', 'reddit', 'google_trends'
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    api_endpoint VARCHAR(500),
    api_key_encrypted TEXT, -- Encrypted API keys
    config JSONB DEFAULT '{}', -- Platform-specific configuration
    rate_limit_per_hour INTEGER DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP WITH TIME ZONE,
    last_successful_scrape TIMESTAMP WITH TIME ZONE,
    error_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT sources_platform_check CHECK (platform IN ('youtube', 'tiktok', 'reddit', 'google_trends', 'instagram', 'twitter'))
);

CREATE INDEX idx_sources_platform ON sources(platform);
CREATE INDEX idx_sources_is_active ON sources(is_active);
CREATE INDEX idx_sources_last_scraped ON sources(last_scraped);

-- Main niches table
CREATE TABLE niches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    keywords TEXT[], -- Array of related keywords
    tags JSONB DEFAULT '[]', -- Flexible tagging system
    
    -- Scoring metrics (0-100 scale)
    overall_score DECIMAL(5,2) DEFAULT 0.00 CHECK (overall_score >= 0 AND overall_score <= 100),
    competition_score DECIMAL(5,2) DEFAULT 0.00 CHECK (competition_score >= 0 AND competition_score <= 100),
    demand_score DECIMAL(5,2) DEFAULT 0.00 CHECK (demand_score >= 0 AND demand_score <= 100),
    monetization_score DECIMAL(5,2) DEFAULT 0.00 CHECK (monetization_score >= 0 AND monetization_score <= 100),
    trend_score DECIMAL(5,2) DEFAULT 0.00 CHECK (trend_score >= 0 AND trend_score <= 100),
    
    -- Status and metadata
    status VARCHAR(50) DEFAULT 'discovered' CHECK (status IN ('discovered', 'analyzing', 'validated', 'rejected', 'archived')),
    discovery_source VARCHAR(50),
    validation_status VARCHAR(50) DEFAULT 'pending' CHECK (validation_status IN ('pending', 'in_progress', 'completed', 'failed')),
    
    -- Timestamps
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP WITH TIME ZONE,
    validated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}',
    
    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
        setweight(to_tsvector('english', array_to_string(keywords, ' ')), 'C')
    ) STORED
);

-- Indexes for niches table
CREATE INDEX idx_niches_slug ON niches(slug);
CREATE INDEX idx_niches_category_id ON niches(category_id);
CREATE INDEX idx_niches_overall_score ON niches(overall_score DESC);
CREATE INDEX idx_niches_status ON niches(status);
CREATE INDEX idx_niches_discovered_at ON niches(discovered_at DESC);
CREATE INDEX idx_niches_keywords_gin ON niches USING gin(keywords);
CREATE INDEX idx_niches_search_vector ON niches USING gin(search_vector);
CREATE INDEX idx_niches_tags_gin ON niches USING gin(tags);
CREATE INDEX idx_niches_composite_score_date ON niches(overall_score DESC, discovered_at DESC);

-- Metrics table for storing various niche metrics
CREATE TABLE niche_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    niche_id UUID NOT NULL REFERENCES niches(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id),
    metric_type VARCHAR(100) NOT NULL, -- 'search_volume', 'competition', 'cpc', etc.
    value DECIMAL(15,4),
    value_text TEXT, -- For non-numeric metrics
    unit VARCHAR(20), -- 'count', 'percentage', 'currency', etc.
    confidence_score DECIMAL(5,2) DEFAULT 0.00 CHECK (confidence_score >= 0 AND confidence_score <= 100),
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    -- Composite unique constraint to prevent duplicates
    UNIQUE(niche_id, source_id, metric_type, collected_at)
);

-- Partition niche_metrics by month for better performance
CREATE TABLE niche_metrics_y2026m02 PARTITION OF niche_metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE niche_metrics_y2026m03 PARTITION OF niche_metrics
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Indexes for niche_metrics
CREATE INDEX idx_niche_metrics_niche_id ON niche_metrics(niche_id);
CREATE INDEX idx_niche_metrics_source_id ON niche_metrics(source_id);
CREATE INDEX idx_niche_metrics_type ON niche_metrics(metric_type);
CREATE INDEX idx_niche_metrics_collected_at ON niche_metrics(collected_at DESC);
CREATE INDEX idx_niche_metrics_composite ON niche_metrics(niche_id, metric_type, collected_at DESC);

-- Historical trend data (partitioned by time)
CREATE TABLE trend_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    niche_id UUID NOT NULL REFERENCES niches(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Trend metrics
    search_volume INTEGER,
    search_volume_change DECIMAL(5,2), -- Percentage change
    competition_level VARCHAR(20), -- 'low', 'medium', 'high'
    trending_keywords TEXT[],
    social_mentions INTEGER,
    social_sentiment DECIMAL(3,2) CHECK (social_sentiment >= -1 AND social_sentiment <= 1),
    
    -- YouTube specific metrics
    youtube_videos_count INTEGER,
    youtube_avg_views INTEGER,
    youtube_top_channels TEXT[],
    
    -- TikTok specific metrics
    tiktok_hashtag_views BIGINT,
    tiktok_videos_count INTEGER,
    tiktok_engagement_rate DECIMAL(5,2),
    
    -- Additional data
    raw_data JSONB DEFAULT '{}',
    
    -- Partition key
    PARTITION BY RANGE (timestamp)
);

-- Create monthly partitions for trend_data
CREATE TABLE trend_data_y2026m02 PARTITION OF trend_data
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE trend_data_y2026m03 PARTITION OF trend_data
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Indexes for trend_data
CREATE INDEX idx_trend_data_niche_id ON trend_data(niche_id);
CREATE INDEX idx_trend_data_timestamp ON trend_data(timestamp DESC);
CREATE INDEX idx_trend_data_composite ON trend_data(niche_id, timestamp DESC);

-- =====================================================
-- OPERATIONAL TABLES
-- =====================================================

-- Scraping jobs tracking
CREATE TABLE scraping_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(50) NOT NULL, -- 'discovery', 'validation', 'update'
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    
    -- Job configuration
    source_id UUID REFERENCES sources(id),
    niche_id UUID REFERENCES niches(id),
    config JSONB DEFAULT '{}',
    
    -- Execution details
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- Results
    items_processed INTEGER DEFAULT 0,
    items_successful INTEGER DEFAULT 0,
    items_failed INTEGER DEFAULT 0,
    result_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX idx_scraping_jobs_job_type ON scraping_jobs(job_type);
CREATE INDEX idx_scraping_jobs_created_at ON scraping_jobs(created_at DESC);
CREATE INDEX idx_scraping_jobs_priority ON scraping_jobs(priority DESC);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PARTITION BY RANGE (timestamp)
);

-- Create daily partitions for API usage (example for current day)
CREATE TABLE api_usage_y2026m02d02 PARTITION OF api_usage
    FOR VALUES FROM ('2026-02-02') TO ('2026-02-03');

CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_timestamp ON api_usage(timestamp DESC);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);

-- Rate limiting data
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    identifier VARCHAR(255) NOT NULL, -- User ID, IP address, API key
    identifier_type VARCHAR(50) NOT NULL, -- 'user', 'ip', 'api_key'
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration_seconds INTEGER NOT NULL,
    request_count INTEGER DEFAULT 0,
    limit_exceeded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(identifier, identifier_type, window_start)
);

CREATE INDEX idx_rate_limits_identifier ON rate_limits(identifier, identifier_type);
CREATE INDEX idx_rate_limits_window_start ON rate_limits(window_start);

-- Notifications/Alerts
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- 'high_score_niche', 'system_alert', 'job_completed'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    
    -- Delivery channels
    channels TEXT[] DEFAULT '{"email"}', -- 'email', 'slack', 'webhook'
    delivery_status VARCHAR(50) DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'sent', 'failed', 'read')),
    delivery_attempts INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_delivery_status ON notifications(delivery_status);

-- =====================================================
-- AUDIT AND LOGGING
-- =====================================================

-- Audit log for tracking changes
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    user_id UUID REFERENCES users(id),
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    
    PARTITION BY RANGE (timestamp)
);

-- Create monthly partitions for audit log
CREATE TABLE audit_log_y2026m02 PARTITION OF audit_log
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for niche summary with latest metrics
CREATE VIEW niche_summary AS
SELECT 
    n.id,
    n.name,
    n.slug,
    n.overall_score,
    n.status,
    n.discovered_at,
    c.name as category_name,
    (
        SELECT COUNT(*) 
        FROM niche_metrics nm 
        WHERE nm.niche_id = n.id 
        AND nm.collected_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
    ) as recent_metrics_count,
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'type', metric_type,
                'value', value,
                'collected_at', collected_at
            )
        )
        FROM niche_metrics nm
        WHERE nm.niche_id = n.id
        AND nm.collected_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
        ORDER BY nm.collected_at DESC
        LIMIT 10
    ) as recent_metrics
FROM niches n
LEFT JOIN categories c ON n.category_id = c.id;

-- View for trending niches (based on recent score improvements)
CREATE VIEW trending_niches AS
WITH score_changes AS (
    SELECT 
        n.id,
        n.name,
        n.overall_score as current_score,
        LAG(n.overall_score) OVER (PARTITION BY n.id ORDER BY n.updated_at) as previous_score,
        n.updated_at
    FROM niches n
    WHERE n.status = 'validated'
    AND n.updated_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
)
SELECT 
    sc.id,
    sc.name,
    sc.current_score,
    sc.previous_score,
    (sc.current_score - COALESCE(sc.previous_score, 0)) as score_change,
    CASE 
        WHEN sc.previous_score IS NULL THEN NULL
        ELSE ((sc.current_score - sc.previous_score) / sc.previous_score * 100)
    END as score_change_percentage
FROM score_changes sc
WHERE sc.current_score > COALESCE(sc.previous_score, 0)
ORDER BY score_change DESC
LIMIT 100;

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_niches_updated_at BEFORE UPDATE ON niches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scraping_jobs_updated_at BEFORE UPDATE ON scraping_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate overall niche score
CREATE OR REPLACE FUNCTION calculate_overall_score(
    competition_score DECIMAL,
    demand_score DECIMAL,
    monetization_score DECIMAL,
    trend_score DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    -- Weighted average: Competition 20%, Demand 30%, Monetization 35%, Trend 15%
    RETURN ROUND(
        (competition_score * 0.20 + 
         demand_score * 0.30 + 
         monetization_score * 0.35 + 
         trend_score * 0.15),
        2
    );
END;
$$ LANGUAGE plpgsql;

-- Function to update overall score when component scores change
CREATE OR REPLACE FUNCTION update_niche_overall_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.overall_score = calculate_overall_score(
        NEW.competition_score,
        NEW.demand_score,
        NEW.monetization_score,
        NEW.trend_score
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_niche_score BEFORE INSERT OR UPDATE ON niches
    FOR EACH ROW EXECUTE FUNCTION update_niche_overall_score();

-- Function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log(table_name, record_id, action, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log(table_name, record_id, action, old_values, new_values)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, record_id, action, old_values)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, to_jsonb(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to important tables
CREATE TRIGGER audit_niches AFTER INSERT OR UPDATE OR DELETE ON niches
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();

-- =====================================================
-- SAMPLE DATA
-- =====================================================

-- Insert default categories
INSERT INTO categories (name, slug, description) VALUES
('Technology', 'technology', 'Tech-related niches including gadgets, software, and innovation'),
('Health & Fitness', 'health-fitness', 'Health, wellness, fitness, and nutrition content'),
('Entertainment', 'entertainment', 'Movies, music, gaming, and general entertainment'),
('Education', 'education', 'Learning, tutorials, and educational content'),
('Business & Finance', 'business-finance', 'Business advice, finance, investing, and entrepreneurship'),
('Lifestyle', 'lifestyle', 'Lifestyle, fashion, travel, and personal development');

-- Insert default data sources
INSERT INTO sources (platform, name, base_url, config) VALUES
('youtube', 'YouTube Data API v3', 'https://www.googleapis.com/youtube/v3', '{"api_version": "v3", "max_results": 50}'),
('google_trends', 'Google Trends', 'https://trends.google.com', '{"geo": "US", "timeframe": "today 12-m"}'),
('reddit', 'Reddit API', 'https://www.reddit.com', '{"user_agent": "NicheDiscoveryBot/1.0"}'),
('tiktok', 'TikTok Research API', 'https://api.tiktok.com', '{"version": "v2"}');

-- =====================================================
-- PERFORMANCE OPTIMIZATION
-- =====================================================

-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_niches_score_range_90_plus ON niches (overall_score) 
WHERE overall_score >= 90;

CREATE INDEX CONCURRENTLY idx_niches_recent_discoveries ON niches (discovered_at) 
WHERE discovered_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Partial index for active sources
CREATE INDEX CONCURRENTLY idx_sources_active ON sources (platform, last_scraped) 
WHERE is_active = TRUE;

-- =====================================================
-- MAINTENANCE PROCEDURES
-- =====================================================

-- Procedure to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data(older_than_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Clean up old API usage data
    DELETE FROM api_usage 
    WHERE timestamp < CURRENT_TIMESTAMP - (older_than_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Clean up old audit logs (keep 2 years)
    DELETE FROM audit_log 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '2 years';
    
    -- Clean up completed scraping jobs older than 90 days
    DELETE FROM scraping_jobs 
    WHERE status IN ('completed', 'failed') 
    AND completed_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SECURITY
-- =====================================================

-- Row Level Security policies (examples)
ALTER TABLE niches ENABLE ROW LEVEL SECURITY;

-- Users can only see their own discovered niches (if we add user_id to niches)
-- CREATE POLICY niches_user_policy ON niches
-- FOR ALL TO authenticated_users
-- USING (user_id = current_setting('app.user_id')::UUID);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON DATABASE niche_discovery IS 'YouTube Niche Discovery Engine Database';

COMMENT ON TABLE niches IS 'Core table storing discovered niches with scoring metrics';
COMMENT ON COLUMN niches.overall_score IS 'Calculated overall score (0-100) based on weighted component scores';
COMMENT ON COLUMN niches.search_vector IS 'Full-text search vector for efficient text search';

COMMENT ON TABLE niche_metrics IS 'Time-series metrics data for niches from various sources';
COMMENT ON TABLE trend_data IS 'Historical trend data partitioned by time for performance';
COMMENT ON TABLE scraping_jobs IS 'Tracking table for all background scraping operations';

COMMENT ON FUNCTION calculate_overall_score IS 'Weighted calculation: Competition 20%, Demand 30%, Monetization 35%, Trend 15%';

-- =====================================================
-- END OF SCHEMA
-- =====================================================