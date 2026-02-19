-- Comby Skill Memory Layer SQLite Schema
-- Stores analysis results, patterns, file indexes, and snapshots

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    analysis_type TEXT NOT NULL,  -- security, quality, complexity, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    findings_count INTEGER DEFAULT 0,
    severity_counts TEXT,  -- JSON: {"critical": 0, "high": 0, "medium": 0, "low": 0}
    results_json TEXT,  -- Full results as JSON
    metadata TEXT  -- Additional metadata as JSON
);

-- Patterns found table
CREATE TABLE IF NOT EXISTS patterns_found (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    pattern_type TEXT NOT NULL,  -- sql_injection, xss, etc.
    file_path TEXT NOT NULL,
    line_number INTEGER,
    severity TEXT,
    context TEXT,
    matched_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Files indexed table
CREATE TABLE IF NOT EXISTS files_indexed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    language TEXT,
    file_hash TEXT,  -- Hash of file content
    file_size INTEGER,
    last_analyzed TIMESTAMP,
    last_modified TIMESTAMP,
    complexity_score REAL,
    line_count INTEGER,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Snapshots table
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    snapshot_data TEXT  -- JSON containing analysis state
);

-- Pattern families table
CREATE TABLE IF NOT EXISTS pattern_families (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_name TEXT NOT NULL UNIQUE,
    description TEXT,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code embeddings table (for similarity search)
CREATE TABLE IF NOT EXISTS code_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    function_name TEXT,
    line_start INTEGER,
    line_end INTEGER,
    embedding BLOB,  -- Vector embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_path, function_name, line_start)
);

-- Graph relations table
CREATE TABLE IF NOT EXISTS graph_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    target_file TEXT,
    relation_type TEXT NOT NULL,  -- imports, calls, inherits, etc.
    metadata TEXT,  -- Additional relation info as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis history table
CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_type TEXT NOT NULL,
    scope TEXT NOT NULL,  -- file, directory, project
    target_path TEXT NOT NULL,
    duration_ms INTEGER,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_analysis_results_file ON analysis_results(file_path);
CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_created ON analysis_results(created_at);
CREATE INDEX IF NOT EXISTS idx_patterns_found_type ON patterns_found(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_found_file ON patterns_found(file_path);
CREATE INDEX IF NOT EXISTS idx_files_indexed_path ON files_indexed(file_path);
CREATE INDEX IF NOT EXISTS idx_files_indexed_language ON files_indexed(language);
CREATE INDEX IF NOT EXISTS idx_code_embeddings_file ON code_embeddings(file_path);
CREATE INDEX IF NOT EXISTS idx_graph_relations_source ON graph_relations(source_file);
CREATE INDEX IF NOT EXISTS idx_graph_relations_target ON graph_relations(target_file);
CREATE INDEX IF NOT EXISTS idx_analysis_history_type ON analysis_history(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_history_target ON analysis_history(target_path);

-- Triggers for automatic updates
CREATE TRIGGER IF NOT EXISTS update_analysis_timestamp
AFTER UPDATE ON files_indexed
BEGIN
    UPDATE files_indexed SET last_analyzed = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
