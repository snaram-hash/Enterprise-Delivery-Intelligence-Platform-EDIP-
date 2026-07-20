import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="erdmp_enterprise.db"):
        # Put DB in root folder
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_name)
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;") # Enforce relational integrity
        return conn

    def initialize_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. USERS (Reference Data)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        
        # 2. REQUIREMENTS (Core Entity - Type 2 SCD)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS requirements (
            req_id TEXT PRIMARY KEY,
            version REAL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL, 
            author_id TEXT NOT NULL,
            created_at TIMESTAMP,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            FOREIGN KEY (author_id) REFERENCES users (user_id)
        )
        ''')
        
        # 3. USER STORIES (Child Entity)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stories (
            story_id TEXT PRIMARY KEY,
            req_id TEXT NOT NULL,
            as_a TEXT NOT NULL,
            i_want_to TEXT NOT NULL,
            so_that TEXT NOT NULL,
            acceptance_criteria TEXT NOT NULL,
            FOREIGN KEY (req_id) REFERENCES requirements (req_id)
        )
        ''')
        
        # 4. TEST CASES (Validation Layer)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_cases (
            test_id TEXT PRIMARY KEY,
            story_id TEXT NOT NULL,
            test_description TEXT NOT NULL,
            execution_status TEXT NOT NULL,
            FOREIGN KEY (story_id) REFERENCES user_stories (story_id)
        )
        ''')
        
        # 5. APPROVALS (Junction Table)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS approvals (
            approval_id TEXT PRIMARY KEY,
            req_id TEXT NOT NULL,
            approver_id TEXT NOT NULL,
            status TEXT NOT NULL,
            comments TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (req_id) REFERENCES requirements (req_id),
            FOREIGN KEY (approver_id) REFERENCES users (user_id)
        )
        ''')
        
        # 6. AUDIT LOGS (Immutable Ledger)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            req_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT,
            action_type TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (req_id) REFERENCES requirements (req_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        # CREATE INDEXES FOR DASHBOARD PERFORMANCE
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_req_status ON requirements(status);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_req ON audit_logs(req_id);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_story_req ON user_stories(req_id);')

        conn.commit()
        conn.close()
        
    def seed_mock_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Seed Users
        users = [
            ('U001', 'Sarah Jenkins', 'BA'),
            ('U002', 'David Chen', 'Sponsor'),
            ('U003', 'Marcus Johnson', 'LeadEng'),
            ('U004', 'Elena Rodriguez', 'QA')
        ]
        cursor.executemany('INSERT INTO users VALUES (?,?,?)', users)
        
        # Seed Requirements
        reqs = [
            ('REQ-1042', 1.0, 'Automate Fraud Alert Routing', 'Routing manual fraud alerts takes 4 hours/day. Auto-route based on IP.', 'PendingReview', 'U001', now, 1),
            ('REQ-1043', 1.0, 'Update Payment Gateway API', 'Stripe API v2 deprecation requires update to v3.', 'Approved', 'U001', now, 1),
            ('REQ-1044', 1.0, 'Customer Churn Dashboard', 'Create a new PowerBI dashboard for executive churn tracking.', 'Draft', 'U001', now, 1)
        ]
        cursor.executemany('INSERT INTO requirements VALUES (?,?,?,?,?,?,?,?)', reqs)
        
        # Seed Stories
        stories = [
            ('US-991', 'REQ-1042', 'Support Agent', 'have alerts auto-route', 'I save manual assignment time', '1. Given a new alert, When IP is EU, Then route to EU queue.'),
            ('US-992', 'REQ-1042', 'Manager', 'override routing rules', 'I can handle edge cases manually', '1. Given a routed alert, When Manager clicks override, Then queue changes.'),
            ('US-993', 'REQ-1043', 'System', 'connect to Stripe v3', 'payments do not fail next month', '1. Given a checkout, When user pays, Then Stripe v3 endpoint is hit.')
        ]
        cursor.executemany('INSERT INTO user_stories VALUES (?,?,?,?,?,?)', stories)
        
        # Seed Approvals
        approvals = [
            ('APP-001', 'REQ-1042', 'U002', 'Pending', '', now),
            ('APP-002', 'REQ-1042', 'U003', 'Approved', 'Technical feasibility confirmed.', now),
            ('APP-003', 'REQ-1043', 'U002', 'Approved', 'Approved for Q3 budget.', now),
            ('APP-004', 'REQ-1043', 'U003', 'Approved', 'Dev team is ready.', now)
        ]
        cursor.executemany('INSERT INTO approvals VALUES (?,?,?,?,?,?)', approvals)
        
        # Seed Audit Log
        audits = [
            ('REQ-1042', 'U001', 'Draft', 'PendingReview', 'Status Transition', now),
            ('REQ-1042', 'U003', 'PendingReview', 'PendingReview', 'Technical Sign-off', now)
        ]
        cursor.executemany('INSERT INTO audit_logs (req_id, user_id, old_status, new_status, action_type, timestamp) VALUES (?,?,?,?,?,?)', audits)
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.initialize_database()
    db.seed_mock_data()
    print("Enterprise DB initialized and seeded.")
