"""Database schema definitions."""

from docdiff.database.connection import DatabaseConnection


def create_tables(connection: DatabaseConnection) -> None:
    """Create all database tables.

    Args:
        connection: Database connection
    """
    # Document nodes table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS document_nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            level INTEGER,
            title TEXT,
            label TEXT,
            name TEXT,
            caption TEXT,
            language TEXT,
            parent_id TEXT,
            file_path TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            content_hash TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (parent_id) REFERENCES document_nodes(id)
        )
    """)

    # Create index for file_path queries
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_file_path 
        ON document_nodes(file_path)
    """)

    # Create index for label queries
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_label 
        ON document_nodes(label)
    """)

    # Create index for parent_id queries
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_nodes_parent_id 
        ON document_nodes(parent_id)
    """)

    # Node children relationship table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS node_children (
            parent_id TEXT NOT NULL,
            child_id TEXT NOT NULL,
            position INTEGER NOT NULL,
            PRIMARY KEY (parent_id, child_id),
            FOREIGN KEY (parent_id) REFERENCES document_nodes(id),
            FOREIGN KEY (child_id) REFERENCES document_nodes(id)
        )
    """)

    # Translation units table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS translation_units (
            id TEXT PRIMARY KEY,
            source_node_id TEXT NOT NULL,
            source_content TEXT NOT NULL,
            target_content TEXT,
            source_lang TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            status TEXT NOT NULL,
            source_hash TEXT,
            translated_hash TEXT,
            translated_at TEXT,
            reviewed_at TEXT,
            FOREIGN KEY (source_node_id) REFERENCES document_nodes(id)
        )
    """)

    # Create index for source_node_id queries
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_translations_source_node 
        ON translation_units(source_node_id)
    """)

    # Create index for status queries
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_translations_status 
        ON translation_units(status)
    """)

    # References table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS document_references (
            id TEXT PRIMARY KEY,
            from_node_id TEXT NOT NULL,
            to_label TEXT NOT NULL,
            to_node_id TEXT,
            reference_type TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            file_path TEXT,
            FOREIGN KEY (from_node_id) REFERENCES document_nodes(id),
            FOREIGN KEY (to_node_id) REFERENCES document_nodes(id)
        )
    """)

    # Create index for from_node_id queries
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_references_from_node 
        ON document_references(from_node_id)
    """)

    # Create index for unresolved references
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_references_unresolved 
        ON document_references(to_node_id) 
        WHERE to_node_id IS NULL
    """)

    connection.commit()
