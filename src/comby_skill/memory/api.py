"""
Memory Layer API

Provides high-level API for storing and querying analysis results.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MemoryAPI:
    """High-level API for memory operations."""

    def __init__(self, db_path: str = ".comby_skill/memory.db"):
        """Initialize memory API.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self.conn = sqlite3.connect(db_path)
        self._init_tables()

    def _ensure_db_dir(self):
        """Ensure database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    def _init_tables(self):
        """Initialize database tables."""
        cursor = self.conn.cursor()

        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                findings_count INTEGER DEFAULT 0,
                severity_counts TEXT,
                results_json TEXT,
                metadata TEXT
            )
        """)

        # Patterns found table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns_found (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
                pattern_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                severity TEXT,
                context TEXT,
                matched_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Files indexed table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files_indexed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL UNIQUE,
                language TEXT,
                file_hash TEXT,
                file_size INTEGER,
                last_analyzed TIMESTAMP,
                line_count INTEGER,
                complexity_score REAL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                snapshot_data TEXT
            )
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_results_file
            ON analysis_results(file_path)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_results_type
            ON analysis_results(analysis_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_type
            ON patterns_found(pattern_type)
        """)

        self.conn.commit()

    def store_analysis(
        self,
        file_path: str,
        analysis_type: str,
        results: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Store analysis results.

        Args:
            file_path: Path to analyzed file
            analysis_type: Type of analysis (security, quality, etc.)
            results: Analysis results
            metadata: Additional metadata

        Returns:
            Analysis ID
        """
        cursor = self.conn.cursor()

        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for result in results:
            sev = result.get("severity", "low")
            if sev in severity_counts:
                severity_counts[sev] += 1

        # Insert analysis
        cursor.execute("""
            INSERT INTO analysis_results
            (file_path, analysis_type, findings_count, severity_counts, results_json, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            analysis_type,
            len(results),
            json.dumps(severity_counts),
            json.dumps(results),
            json.dumps(metadata) if metadata else None,
        ))

        analysis_id = cursor.lastrowid

        # Insert individual patterns
        for result in results:
            cursor.execute("""
                INSERT INTO patterns_found
                (analysis_id, pattern_type, file_path, line_number, severity, context, matched_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                result.get("pattern_type", "unknown"),
                result.get("file", file_path),
                result.get("line"),
                result.get("severity"),
                result.get("context"),
                result.get("text"),
            ))

        self.conn.commit()
        return analysis_id

    def get_analysis_history(
        self,
        file_path: Optional[str] = None,
        analysis_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get analysis history.

        Args:
            file_path: Filter by file path
            analysis_type: Filter by analysis type
            limit: Maximum results

        Returns:
            List of analysis records
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM analysis_results WHERE 1=1"
        params = []

        if file_path:
            query += " AND file_path = ?"
            params.append(file_path)

        if analysis_type:
            query += " AND analysis_type = ?"
            params.append(analysis_type)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "file_path": row[1],
                "analysis_type": row[2],
                "created_at": row[3],
                "findings_count": row[4],
                "severity_counts": json.loads(row[5]) if row[5] else {},
                "metadata": json.loads(row[6]) if row[6] else {},
            })

        return results

    def find_similar(
        self,
        pattern_type: Optional[str] = None,
        severity: Optional[str] = None,
        file_pattern: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Find similar patterns.

        Args:
            pattern_type: Filter by pattern type
            severity: Filter by severity
            file_pattern: File path pattern

        Returns:
            List of matching patterns
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM patterns_found WHERE 1=1"
        params = []

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        if file_pattern:
            query += " AND file_path LIKE ?"
            params.append(f"%{file_pattern}%")

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "analysis_id": row[1],
                "pattern_type": row[2],
                "file_path": row[3],
                "line_number": row[4],
                "severity": row[5],
                "context": row[6],
                "matched_text": row[7],
                "created_at": row[8],
            })

        return results

    def create_snapshot(
        self,
        name: str,
        description: str = "",
    ) -> int:
        """Create a snapshot of current state.

        Args:
            name: Snapshot name
            description: Snapshot description

        Returns:
            Snapshot ID
        """
        # Gather current state
        cursor = self.conn.cursor()

        # Get all recent analyses
        cursor.execute("""
            SELECT * FROM analysis_results
            ORDER BY created_at DESC
            LIMIT 1000
        """)

        analyses = []
        for row in cursor.fetchall():
            analyses.append({
                "id": row[0],
                "file_path": row[1],
                "analysis_type": row[2],
                "created_at": row[3],
                "findings_count": row[4],
                "severity_counts": row[5],
                "results_json": row[6],
            })

        snapshot_data = {
            "analyses": analyses,
            "created_at": datetime.now().isoformat(),
        }

        # Store snapshot
        cursor.execute("""
            INSERT INTO snapshots (name, description, snapshot_data)
            VALUES (?, ?, ?)
        """, (name, description, json.dumps(snapshot_data)))

        self.conn.commit()
        return cursor.lastrowid

    def get_snapshot(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        """Get snapshot by ID.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            Snapshot data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM snapshots WHERE id = ?
        """, (snapshot_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "created_at": row[3],
            "snapshot_data": json.loads(row[4]) if row[4] else {},
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Statistics dictionary
        """
        cursor = self.conn.cursor()

        # Count analyses
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        total_analyses = cursor.fetchone()[0]

        # Count patterns
        cursor.execute("SELECT COUNT(*) FROM patterns_found")
        total_patterns = cursor.fetchone()[0]

        # Count files
        cursor.execute("SELECT COUNT(*) FROM files_indexed")
        total_files = cursor.fetchone()[0]

        # Count snapshots
        cursor.execute("SELECT COUNT(*) FROM snapshots")
        total_snapshots = cursor.fetchone()[0]

        # Most common patterns
        cursor.execute("""
            SELECT pattern_type, COUNT(*) as count
            FROM patterns_found
            GROUP BY pattern_type
            ORDER BY count DESC
            LIMIT 10
        """)
        common_patterns = [
            {"pattern": row[0], "count": row[1]}
            for row in cursor.fetchall()
        ]

        return {
            "total_analyses": total_analyses,
            "total_patterns": total_patterns,
            "total_files": total_files,
            "total_snapshots": total_snapshots,
            "common_patterns": common_patterns,
        }

    def close(self):
        """Close database connection."""
        self.conn.close()


# Convenience functions
def store_analysis(
    file_path: str,
    analysis_type: str,
    results: List[Dict[str, Any]],
    db_path: str = ".comby_skill/memory.db",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """Store analysis results.

    Args:
        file_path: Path to analyzed file
        analysis_type: Type of analysis
        results: Analysis results
        db_path: Database path
        metadata: Additional metadata

    Returns:
        Analysis ID
    """
    api = MemoryAPI(db_path)
    result = api.store_analysis(file_path, analysis_type, results, metadata)
    api.close()
    return result


def get_history(
    db_path: str = ".comby_skill/memory.db",
    **filters,
) -> List[Dict[str, Any]]:
    """Get analysis history.

    Args:
        db_path: Database path
        **filters: Filter parameters

    Returns:
        List of analysis records
    """
    api = MemoryAPI(db_path)
    result = api.get_analysis_history(**filters)
    api.close()
    return result


def get_statistics(
    db_path: str = ".comby_skill/memory.db",
) -> Dict[str, Any]:
    """Get memory statistics.

    Args:
        db_path: Database path

    Returns:
        Statistics dictionary
    """
    api = MemoryAPI(db_path)
    result = api.get_statistics()
    api.close()
    return result
