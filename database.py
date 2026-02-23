"""
Idea Tracker - Database Module
Stores business ideas and research findings
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "ideas.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            problem TEXT NOT NULL,
            description TEXT,
            existing_solutions TEXT,
            source TEXT,
            category TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            research_notes TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS research_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT,
            source TEXT,
            findings TEXT,
            researched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_idea(title, problem, description="", existing_solutions="", source="", category="", research_notes=""):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO ideas (title, problem, description, existing_solutions, source, category, research_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, problem, description, existing_solutions, source, category, research_notes))
    conn.commit()
    idea_id = c.lastrowid
    conn.close()
    return idea_id

def get_all_ideas():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM ideas ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ideas_by_status(status):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM ideas WHERE status = ? ORDER BY created_at DESC', (status,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_idea_status(idea_id, status):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE ideas SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (status, idea_id))
    conn.commit()
    conn.close()

def log_research(search_term, source, findings):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO research_log (search_term, source, findings) VALUES (?, ?, ?)', 
              (search_term, source, findings))
    conn.commit()
    conn.close()

def get_research_log():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM research_log ORDER BY researched_at DESC LIMIT 20')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM ideas WHERE category != ""')
    rows = c.fetchall()
    conn.close()
    return [r['category'] for r in rows if r['category']]

def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) as total FROM ideas')
    total = c.fetchone()['total']
    
    c.execute("SELECT COUNT(*) as count FROM ideas WHERE status = 'new'")
    new_count = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM ideas WHERE status = 'interesting'")
    interesting = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM ideas WHERE status = 'reject'")
    rejected = c.fetchone()['count']
    
    c.execute('SELECT COUNT(*) as count FROM ideas WHERE status = "validated"')
    validated = c.fetchone()['count']
    
    conn.close()
    
    return {"total": total, "new": new_count, "interesting": interesting, "rejected": rejected, "validated": validated}

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
