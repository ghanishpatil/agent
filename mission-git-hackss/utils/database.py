"""Database for storing challenges, exploits, and results"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.challenge import Challenge, ChallengeResult


class Database:
    """SQLite database for MD-EXPLOIT-ENGINE"""
    
    def __init__(self, db_path: str = 'data/md-exploit-engine.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Challenges table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    points INTEGER DEFAULT 0,
                    url TEXT,
                    host TEXT,
                    port INTEGER,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    challenge_id INTEGER,
                    success INTEGER DEFAULT 0,
                    flag TEXT,
                    error TEXT,
                    method TEXT,
                    duration REAL DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    logs TEXT,
                    artifacts TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
                )
            ''')
            
            # Exploits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exploits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    code TEXT,
                    success_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Flags table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    flag TEXT UNIQUE NOT NULL,
                    challenge_id INTEGER,
                    submitted INTEGER DEFAULT 0,
                    verified INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
                )
            ''')
            
            conn.commit()
    
    def save_challenge(self, challenge: Challenge) -> int:
        """Save challenge to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO challenges (name, category, description, points, url, host, port, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                challenge.name,
                challenge.category,
                challenge.description,
                challenge.points,
                challenge.url,
                challenge.host,
                challenge.port,
                json.dumps(challenge.metadata)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_result(self, result: ChallengeResult, challenge_id: Optional[int] = None) -> int:
        """Save result to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO results (challenge_id, success, flag, error, method, duration, attempts, logs, artifacts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                challenge_id,
                1 if result.success else 0,
                result.flag,
                result.error,
                result.method,
                result.duration,
                result.attempts,
                json.dumps(result.logs),
                json.dumps(result.artifacts)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_flag(self, flag: str, challenge_id: Optional[int] = None) -> bool:
        """Save flag to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO flags (flag, challenge_id)
                    VALUES (?, ?)
                ''', (flag, challenge_id))
                conn.commit()
                return cursor.rowcount > 0
        except:
            return False
    
    def get_challenges(self, category: Optional[str] = None) -> List[Dict]:
        """Get challenges from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute('SELECT * FROM challenges WHERE category = ?', (category,))
            else:
                cursor.execute('SELECT * FROM challenges')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_results(self, success_only: bool = False) -> List[Dict]:
        """Get results from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if success_only:
                cursor.execute('SELECT * FROM results WHERE success = 1')
            else:
                cursor.execute('SELECT * FROM results')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_flags(self) -> List[str]:
        """Get all flags from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT flag FROM flags')
            return [row[0] for row in cursor.fetchall()]
    
    def flag_exists(self, flag: str) -> bool:
        """Check if flag already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM flags WHERE flag = ?', (flag,))
            return cursor.fetchone() is not None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute('SELECT COUNT(*) FROM challenges')
            stats['total_challenges'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM results WHERE success = 1')
            stats['solved_challenges'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM flags')
            stats['total_flags'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT category, COUNT(*) FROM challenges GROUP BY category')
            stats['by_category'] = dict(cursor.fetchall())
            
            cursor.execute('SELECT AVG(duration) FROM results WHERE success = 1')
            stats['avg_solve_time'] = cursor.fetchone()[0] or 0
            
            return stats
