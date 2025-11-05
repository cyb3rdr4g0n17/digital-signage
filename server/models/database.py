"""
Database models and initialization
"""
import sqlite3
import json
import hashlib
from datetime import datetime
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Media table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filetype TEXT NOT NULL,
                path TEXT NOT NULL,
                size INTEGER,
                duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Playlists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                json_items TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Schedule table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                device_id INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                days_of_week TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id),
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                uuid TEXT UNIQUE NOT NULL,
                assigned_playlist_id INTEGER,
                ip_address TEXT,
                token TEXT,
                last_sync TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_playlist_id) REFERENCES playlists(id)
            )
        ''')

        # Tickers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                speed INTEGER DEFAULT 50,
                font_size INTEGER DEFAULT 24,
                font_color TEXT DEFAULT '#FFFFFF',
                background_color TEXT DEFAULT '#000000',
                position TEXT DEFAULT 'bottom',
                is_active INTEGER DEFAULT 1,
                device_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')

        conn.commit()
        conn.close()

        # Create default admin user if not exists
        self.create_default_user()

    def create_default_user(self):
        """Create default admin user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if admin exists
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            # Default password: admin (change in production!)
            password_hash = hashlib.sha256('admin'.encode()).hexdigest()
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                ('admin', password_hash)
            )
            conn.commit()

        conn.close()

    # User operations
    def authenticate_user(self, username, password):
        """Authenticate user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            'SELECT id, username FROM users WHERE username = ? AND password = ?',
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    # Media operations
    def add_media(self, filename, filetype, path, size=None, duration=None):
        """Add media to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO media (filename, filetype, path, size, duration) VALUES (?, ?, ?, ?, ?)',
            (filename, filetype, path, size, duration)
        )
        media_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return media_id

    def get_media(self, media_id=None):
        """Get media by ID or all media"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if media_id:
            cursor.execute('SELECT * FROM media WHERE id = ?', (media_id,))
            media = cursor.fetchone()
            conn.close()
            return dict(media) if media else None
        else:
            cursor.execute('SELECT * FROM media ORDER BY created_at DESC')
            media_list = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return media_list

    def delete_media(self, media_id):
        """Delete media"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM media WHERE id = ?', (media_id,))
        conn.commit()
        conn.close()

    # Playlist operations
    def create_playlist(self, name, items):
        """Create new playlist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        json_items = json.dumps(items)
        cursor.execute(
            'INSERT INTO playlists (name, json_items) VALUES (?, ?)',
            (name, json_items)
        )
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return playlist_id

    def update_playlist(self, playlist_id, name=None, items=None):
        """Update playlist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if items:
            json_items = json.dumps(items)
            cursor.execute(
                'UPDATE playlists SET json_items = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (json_items, playlist_id)
            )
        if name:
            cursor.execute(
                'UPDATE playlists SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (name, playlist_id)
            )
        conn.commit()
        conn.close()

    def get_playlist(self, playlist_id):
        """Get playlist by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM playlists WHERE id = ?', (playlist_id,))
        playlist = cursor.fetchone()
        conn.close()
        if playlist:
            playlist_dict = dict(playlist)
            playlist_dict['items'] = json.loads(playlist_dict['json_items'])
            return playlist_dict
        return None

    def get_all_playlists(self):
        """Get all playlists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM playlists ORDER BY created_at DESC')
        playlists = []
        for row in cursor.fetchall():
            playlist_dict = dict(row)
            playlist_dict['items'] = json.loads(playlist_dict['json_items'])
            playlists.append(playlist_dict)
        conn.close()
        return playlists

    # Device operations
    def register_device(self, name, uuid, ip_address=None):
        """Register new device"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Generate token
        token = hashlib.sha256(f"{uuid}{datetime.now()}".encode()).hexdigest()[:32]
        cursor.execute(
            'INSERT OR REPLACE INTO devices (name, uuid, ip_address, token, last_seen) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)',
            (name, uuid, ip_address, token)
        )
        device_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return device_id, token

    def get_device(self, device_id=None, uuid=None):
        """Get device by ID or UUID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if device_id:
            cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        elif uuid:
            cursor.execute('SELECT * FROM devices WHERE uuid = ?', (uuid,))
        else:
            conn.close()
            return None
        device = cursor.fetchone()
        conn.close()
        return dict(device) if device else None

    def get_all_devices(self):
        """Get all devices"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM devices ORDER BY last_seen DESC')
        devices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return devices

    def assign_playlist_to_device(self, device_id, playlist_id):
        """Assign playlist to device"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE devices SET assigned_playlist_id = ? WHERE id = ?',
            (playlist_id, device_id)
        )
        conn.commit()
        conn.close()

    def update_device_sync(self, device_id):
        """Update device last sync time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE devices SET last_sync = CURRENT_TIMESTAMP, last_seen = CURRENT_TIMESTAMP WHERE id = ?',
            (device_id,)
        )
        conn.commit()
        conn.close()

    # Schedule operations
    def create_schedule(self, playlist_id, start_time, end_time, device_id=None, days_of_week=None):
        """Create schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO schedule (playlist_id, device_id, start_time, end_time, days_of_week) VALUES (?, ?, ?, ?, ?)',
            (playlist_id, device_id, start_time, end_time, days_of_week)
        )
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id

    def get_active_schedule(self, device_id):
        """Get active schedule for device"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM schedule 
               WHERE (device_id = ? OR device_id IS NULL) 
               AND datetime('now') >= datetime(start_time) 
               AND datetime('now') <= datetime(end_time)
               ORDER BY created_at DESC LIMIT 1''',
            (device_id,)
        )
        schedule = cursor.fetchone()
        conn.close()
        return dict(schedule) if schedule else None

    # Ticker operations
    def create_ticker(self, name, text, speed=50, font_size=24, font_color='#FFFFFF', 
                      background_color='#000000', position='bottom', device_id=None):
        """Create new ticker"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO tickers (name, text, speed, font_size, font_color, 
               background_color, position, device_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, text, speed, font_size, font_color, background_color, position, device_id)
        )
        ticker_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticker_id

    def update_ticker(self, ticker_id, **kwargs):
        """Update ticker"""
        conn = self.get_connection()
        cursor = conn.cursor()
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in ['name', 'text', 'speed', 'font_size', 'font_color', 
                       'background_color', 'position', 'is_active', 'device_id']:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(ticker_id)
            cursor.execute(
                f'UPDATE tickers SET {", ".join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                values
            )
            conn.commit()
        conn.close()

    def get_ticker(self, ticker_id):
        """Get ticker by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickers WHERE id = ?', (ticker_id,))
        ticker = cursor.fetchone()
        conn.close()
        return dict(ticker) if ticker else None

    def get_all_tickers(self):
        """Get all tickers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickers ORDER BY created_at DESC')
        tickers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tickers

    def get_active_ticker_for_device(self, device_id):
        """Get active ticker for device"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM tickers 
               WHERE is_active = 1 AND (device_id = ? OR device_id IS NULL)
               ORDER BY device_id DESC, created_at DESC LIMIT 1''',
            (device_id,)
        )
        ticker = cursor.fetchone()
        conn.close()
        return dict(ticker) if ticker else None

    def delete_ticker(self, ticker_id):
        """Delete ticker"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tickers WHERE id = ?', (ticker_id,))
        conn.commit()
        conn.close()


# Global database instance
db = Database()

