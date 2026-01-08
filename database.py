import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path="reports.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_prompt TEXT NOT NULL,
                enhanced_prompt TEXT NOT NULL,
                generated_code TEXT NOT NULL,
                original_code TEXT NOT NULL,
                detected_language TEXT,
                analysis_results TEXT,
                fix_attempts INTEGER DEFAULT 0,
                had_high_severity BOOLEAN DEFAULT FALSE,
                analysis_history TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                html_content TEXT
            )
        ''')
        
        # Create analysis_history table for better tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                attempt_number INTEGER,
                code_version TEXT,
                analysis_result TEXT,
                vulnerabilities_found TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_report(self, report_data):
        """Save report to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (
                user_prompt, enhanced_prompt, generated_code, original_code,
                detected_language, analysis_results, fix_attempts, had_high_severity,
                analysis_history, html_content
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_data['user_prompt'],
            report_data['enhanced_prompt'],
            report_data['generated_code'],
            report_data.get('original_code', ''),
            report_data.get('detected_language', 'Unknown'),
            json.dumps(report_data.get('analysis_results', {})),
            report_data.get('fix_attempts', 0),
            report_data.get('had_high_severity', False),
            json.dumps(report_data.get('analysis_history', [])),
            report_data.get('html_content', '')
        ))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return report_id
    
    def get_report(self, report_id):
        """Get report by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Convert row to dictionary
        columns = [description[0] for description in cursor.description]
        report = dict(zip(columns, row))
        
        # Parse JSON fields
        report['analysis_results'] = json.loads(report['analysis_results']) if report['analysis_results'] else {}
        report['analysis_history'] = json.loads(report['analysis_history']) if report['analysis_history'] else []
        
        conn.close()
        return report
    
    def get_all_reports(self, limit=50):
        """Get all reports with limit, sorted by most recent first"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_prompt, detected_language, timestamp, fix_attempts, had_high_severity
            FROM reports 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        reports = []
        for row in rows:
            report = dict(zip(columns, row))
            # Format timestamp for display
            if report['timestamp']:
                try:
                    dt = datetime.fromisoformat(report['timestamp'].replace('Z', '+00:00'))
                    report['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            reports.append(report)
        
        conn.close()
        return reports
    
    def save_analysis_history(self, report_id, attempt_data):
        """Save analysis history for a report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history (
                report_id, attempt_number, code_version, analysis_result, vulnerabilities_found
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            report_id,
            attempt_data['attempt_number'],
            attempt_data['code_version'],
            attempt_data['analysis_result'],
            attempt_data['vulnerabilities_found']
        ))
        
        conn.commit()
        conn.close()
    
    def get_analysis_history(self, report_id):
        """Get analysis history for a report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM analysis_history 
            WHERE report_id = ? 
            ORDER BY attempt_number ASC
        ''', (report_id,))
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        history = []
        for row in rows:
            history.append(dict(zip(columns, row)))
        
        conn.close()
        return history
    
    def update_report_html(self, report_id, html_content):
        """Update HTML content for a report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reports SET html_content = ? WHERE id = ?
        ''', (html_content, report_id))
        
        conn.commit()
        conn.close()
    
    def delete_report(self, report_id):
        """Delete a report and its history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete analysis history first
        cursor.execute('DELETE FROM analysis_history WHERE report_id = ?', (report_id,))
        # Delete report
        cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
        
        conn.commit()
        conn.close()

# Global database instance
db = Database()

