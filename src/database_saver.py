import sqlite3, configparser, datetime
from typing import Literal

def _read_config(config_path):
    global database_path
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_path)
    database_path = config.get("Paths", "database_path")

class ReportSaver:
    def __init__(self):
        _read_config("src/potop.cfg")
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()
        self._create_tables()
    
    def _create_tables(self):
        # Пиковые значения
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS peak_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_type TEXT NOT NULL,
                peak_value REAL NOT NULL,
                peak_time_seconds REAL,
                peak_time_full TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Отчёты
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                avg_value REAL,
                max_value REAL,
                max_time_full TEXT,
                data_points TEXT
            )
        """)
        self.connection.commit()
    
    def save_peak(self, window_type: str, peak_value: float, 
                  peak_time_seconds: float, peak_time_full: str):
        self.cursor.execute("""
            INSERT INTO peak_values (window_type, peak_value, peak_time_seconds, 
                                    peak_time_full, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (window_type, peak_value, peak_time_seconds, 
              peak_time_full, datetime.datetime.now().isoformat()))
        self.connection.commit()
    
    def save_report(self, window_type: str, avg_value: float, 
                    max_value: float, max_time_full: str, data_points: str):
        self.cursor.execute("""
            INSERT INTO reports (window_type, created_at, avg_value, 
                                max_value, max_time_full, data_points)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (window_type, datetime.datetime.now().isoformat(), 
              avg_value, max_value, max_time_full, data_points))
        self.connection.commit()
    
    def get_peaks(self, window_type: str = None):
        if window_type:
            self.cursor.execute(
                "SELECT * FROM peak_values WHERE window_type=? ORDER BY timestamp DESC", 
                (window_type,))
        else:
            self.cursor.execute(
                "SELECT * FROM peak_values ORDER BY timestamp DESC")
        return self.cursor.fetchall()
    
    def get_reports(self, window_type: str = None):
        if window_type:
            self.cursor.execute(
                "SELECT * FROM reports WHERE window_type=? ORDER BY created_at DESC", 
                (window_type,))
        else:
            self.cursor.execute(
                "SELECT * FROM reports ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def close(self):
        self.connection.close()