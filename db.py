import sqlite3
import hashlib
import json
import time
from datetime import datetime

DB_FILE = 'app_data.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Incidents Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            ips_count INTEGER,
            risk_level TEXT,
            raw_data TEXT,  -- JSON string of full analysis
            summary TEXT
        )
    ''')
    
    # Settings Table (Key-Value)
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Create Admin if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_pass = hashlib.sha256(str.encode('admin123')).hexdigest()
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ('admin', admin_pass, 'admin'))
        
    conn.commit()
    conn.close()

# --- User Management ---
def get_user_hash(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row['password_hash'] if row else None

def create_user(username, password_hash, role='user'):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  (username, password_hash, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# --- Incident Management ---
def add_incident(incident_data):
    conn = get_connection()
    c = conn.cursor()
    
    # Serialize complex data to JSON for storage
    raw_json = json.dumps(incident_data.get('data', {}))
    
    c.execute('''
        INSERT INTO incidents (id, timestamp, ips_count, risk_level, raw_data, summary)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        incident_data['id'],
        incident_data['time'],
        incident_data['ips_found'],
        incident_data['status'],
        raw_json,
        incident_data.get('summary', '')
    ))
    conn.commit()
    conn.close()

def get_incidents():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM incidents ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    # Convert rows back to dicts
    history = []
    for row in rows:
        history.append({
            'id': row['id'],
            'time': row['timestamp'],
            'ips_found': row['ips_count'],
            'status': row['risk_level'],
            'data': json.loads(row['raw_data']),
            'summary': row['summary']
        })
    return history

# --- Settings Management ---
def save_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row['value'] if row else None
