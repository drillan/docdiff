"""Add multi-language support to database schema."""

from docdiff.database.connection import DatabaseConnection


def upgrade(conn: DatabaseConnection) -> None:
    """Apply migration: add language support."""

    # Add new columns to existing table
    conn.execute("""
        ALTER TABLE document_nodes 
        ADD COLUMN doc_language TEXT DEFAULT 'en'
    """)

    conn.execute("""
        ALTER TABLE document_nodes 
        ADD COLUMN source_file_hash TEXT
    """)

    conn.execute("""
        ALTER TABLE document_nodes 
        ADD COLUMN last_modified TEXT
    """)

    # Create translation pairs table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS translation_pairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_node_id TEXT NOT NULL,
            target_node_id TEXT,
            source_language TEXT NOT NULL DEFAULT 'en',
            target_language TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            similarity_score REAL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (source_node_id) REFERENCES document_nodes(id),
            FOREIGN KEY (target_node_id) REFERENCES document_nodes(id)
        )
    """)

    # Create indices for performance
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_language 
        ON document_nodes(doc_language)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_pairs_langs 
        ON translation_pairs(source_language, target_language)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_pairs_source 
        ON translation_pairs(source_node_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_pairs_target 
        ON translation_pairs(target_node_id)
    """)

    conn.commit()


def downgrade(conn: DatabaseConnection) -> None:
    """Revert migration."""
    # This is a destructive operation - handle with care
    # For now, we'll just pass as downgrade is not critical for Phase 1.5
    pass
