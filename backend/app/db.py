# db.py — SQLite database helpers (converted from MySQL)
import sqlite3
import os
from flask import current_app

def get_conn(no_db=False):
    """Get SQLite database connection"""
    cfg = current_app.config
    db_path = cfg.get("DB_PATH", "gradehub.db")
    
    # Create database file if it doesn't exist
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
    
    conn = sqlite3.connect(db_path)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def create_db_if_not_exists():
    """Create database if not exists - for SQLite this is handled in get_conn"""
    # SQLite automatically creates the database file when connecting
    # This function is kept for compatibility with the existing code
    cfg = current_app.config
    db_path = cfg.get("DB_PATH", "gradehub.db")
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()
