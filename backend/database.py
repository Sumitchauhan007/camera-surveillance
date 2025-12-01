"""
Database Module for AI Surveillance System
Stores detection events, face data, and system logs
"""
import sqlite3
from datetime import datetime
import config
import os

class SurveillanceDB:
    def __init__(self):
        """Initialize database connection"""
        self.db_path = config.DATABASE_PATH
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to SQLite database"""
        try:
            # Use check_same_thread=False for Flask multithreading
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.conn.cursor()
            print(f"Database connected: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
    
    def _ensure_connection(self):
        """Ensure database connection is alive"""
        try:
            if self.conn is None:
                self.connect()
            else:
                # Test connection
                self.conn.execute("SELECT 1")
        except sqlite3.Error:
            print("Database connection lost, reconnecting...")
            self.connect()
    
    def create_tables(self):
        """Create necessary database tables"""
        # Detection events table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                person_id TEXT,
                person_name TEXT,
                confidence REAL,
                face_image_path TEXT,
                video_path TEXT,
                camera_id TEXT,
                notes TEXT
            )
        ''')
        
        # Known persons table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS known_persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                date_added TEXT NOT NULL,
                image_path TEXT,
                notes TEXT
            )
        ''')
        
        # System logs table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # Alerts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                person_id TEXT,
                person_name TEXT,
                description TEXT,
                acknowledged INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def log_detection(self, person_id, person_name=None, confidence=0, 
                     face_image_path=None, video_path=None, camera_id="0"):
        """Log a face detection event"""
        timestamp = datetime.now().isoformat()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO detection_events 
                (timestamp, person_id, person_name, confidence, face_image_path, video_path, camera_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, person_id, person_name, confidence, face_image_path, video_path, camera_id))
            
            self.conn.commit()
            lastrowid = cursor.lastrowid
            cursor.close()
            return lastrowid
        except sqlite3.Error as e:
            print(f"Error logging detection: {e}")
            return None
    
    def add_known_person(self, name, image_path=None, notes=None):
        """Add a known person to the database"""
        self._ensure_connection()
        timestamp = datetime.now().isoformat()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO known_persons (name, date_added, image_path, notes)
                VALUES (?, ?, ?, ?)
            ''', (name, timestamp, image_path, notes))
            
            self.conn.commit()
            person_id = cursor.lastrowid
            print(f"✅ Added known person to database: {name} (ID: {person_id})")
            
            # Verify the insert
            cursor.execute('SELECT COUNT(*) FROM known_persons WHERE id = ?', (person_id,))
            count = cursor.fetchone()[0]
            print(f"✅ Verification: Person with ID {person_id} exists: {count == 1}")
            cursor.close()
            
            return True
        except sqlite3.IntegrityError:
            print(f"⚠️ Person '{name}' already exists in database")
            self.conn.rollback()
            return False
        except sqlite3.Error as e:
            print(f"❌ Error adding known person: {e}")
            self.conn.rollback()
            return False
    
    def get_known_persons(self):
        """Get list of all known persons"""
        self._ensure_connection()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM known_persons ORDER BY date_added DESC')
            results = cursor.fetchall()
            cursor.close()
            print(f"Retrieved {len(results)} known persons from database")
            return results
        except sqlite3.Error as e:
            print(f"Error fetching known persons: {e}")
            return []
    
    def log_system_event(self, level, message, details=None):
        """Log a system event"""
        timestamp = datetime.now().isoformat()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO system_logs (timestamp, level, message, details)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, level, message, details))
            
            self.conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print(f"Error logging system event: {e}")
    
    def create_alert(self, alert_type, person_id=None, person_name=None, description=None):
        """Create a new alert"""
        timestamp = datetime.now().isoformat()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts 
                (timestamp, alert_type, person_id, person_name, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, alert_type, person_id, person_name, description))
            
            self.conn.commit()
            lastrowid = cursor.lastrowid
            cursor.close()
            return lastrowid
        except sqlite3.Error as e:
            print(f"Error creating alert: {e}")
            return None
    
    def get_recent_detections(self, limit=50):
        """Get recent detection events"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM detection_events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except sqlite3.Error as e:
            print(f"Error fetching recent detections: {e}")
            return []
    
    def get_detections_by_person(self, person_name):
        """Get all detections for a specific person"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM detection_events 
                WHERE person_name = ? 
                ORDER BY timestamp DESC
            ''', (person_name,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except sqlite3.Error as e:
            print(f"Error fetching detections by person: {e}")
            return []
    
    def get_unacknowledged_alerts(self):
        """Get all unacknowledged alerts"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM alerts 
                WHERE acknowledged = 0 
                ORDER BY timestamp DESC
            ''')
            results = cursor.fetchall()
            cursor.close()
            return results
        except sqlite3.Error as e:
            print(f"Error fetching alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id):
        """Mark an alert as acknowledged"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE alerts 
                SET acknowledged = 1 
                WHERE id = ?
            ''', (alert_id,))
            
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Error acknowledging alert: {e}")
            return False
    
    def get_statistics(self):
        """Get system statistics"""
        stats = {}
        
        try:
            cursor = self.conn.cursor()
            
            # Total detections
            cursor.execute('SELECT COUNT(*) FROM detection_events')
            stats['total_detections'] = cursor.fetchone()[0]
            
            # Known persons count
            cursor.execute('SELECT COUNT(*) FROM known_persons')
            stats['known_persons'] = cursor.fetchone()[0]
            
            # Unacknowledged alerts
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE acknowledged = 0')
            stats['pending_alerts'] = cursor.fetchone()[0]
            
            # Detections today
            today = datetime.now().date().isoformat()
            cursor.execute('''
                SELECT COUNT(*) FROM detection_events 
                WHERE date(timestamp) = ?
            ''', (today,))
            stats['detections_today'] = cursor.fetchone()[0]
            
            cursor.close()
        except sqlite3.Error as e:
            print(f"Error fetching statistics: {e}")
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
