import sqlite3
import os
import random
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_name="edip_enterprise.db"):
        # Put DB in root folder, rename to edip_enterprise
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_name)
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;") 
        return conn

    def initialize_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. USERS (Reference Data) - Include Teams/Departments for Analytics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL
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
            sponsor_id TEXT NOT NULL,
            business_value_est INTEGER,
            created_at TIMESTAMP,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            FOREIGN KEY (author_id) REFERENCES users (user_id),
            FOREIGN KEY (sponsor_id) REFERENCES users (user_id)
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
            test_cycle INTEGER NOT NULL DEFAULT 1,
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
            
        print("Seeding Enterprise Delivery Intelligence Platform with 500+ historical records...")
        
        # Seed Users (BAs, Sponsors, QA, Eng) across different departments
        depts = ['Retail Banking', 'Wealth Management', 'Risk & Compliance', 'Digital Channels']
        sponsors = [(f'S{i:03d}', f'Sponsor {i}', 'Sponsor', random.choice(depts)) for i in range(1, 11)]
        bas = [(f'B{i:03d}', f'Analyst {i}', 'BA', random.choice(depts)) for i in range(1, 16)]
        qas = [(f'Q{i:03d}', f'QA {i}', 'QA', random.choice(depts)) for i in range(1, 11)]
        engs = [(f'E{i:03d}', f'Engineer {i}', 'LeadEng', random.choice(depts)) for i in range(1, 11)]
        
        all_users = sponsors + bas + qas + engs
        cursor.executemany('INSERT INTO users VALUES (?,?,?,?)', all_users)
        
        # Generate 500 Historical Requirements over the last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        reqs = []
        stories = []
        test_cases = []
        approvals = []
        audits = []
        
        story_counter = 1
        test_counter = 1
        app_counter = 1
        
        for i in range(1, 501):
            req_id = f'REQ-{i:04d}'
            ba = random.choice(bas)[0]
            sponsor = random.choice(sponsors)
            sponsor_id = sponsor[0]
            dept = sponsor[3]
            
            # Simulate creation date
            days_offset = random.randint(0, 350)
            created_at = start_date + timedelta(days=days_offset)
            
            # Analytics Generation Logic
            # 1. Volatility: 20% chance of high volatility (versions 1.2 to 2.5)
            # 2. Cycle Time Delays: 'Risk & Compliance' dept has artificially longer approval times
            # 3. UAT Failures: 15% chance of multiple test cycles before passing
            
            is_volatile = random.random() < 0.20
            version = 1.0 + (random.randint(1, 15)/10.0 if is_volatile else random.choice([0.0, 0.1, 0.2]))
            
            # Status distribution
            status_rand = random.random()
            if status_rand < 0.05:
                status = 'Draft'
            elif status_rand < 0.20:
                status = 'PendingReview'
            elif status_rand < 0.35:
                status = 'InUAT'
            else:
                status = 'Deployed'
                
            business_value = random.randint(10000, 500000)
            
            reqs.append((req_id, version, f'Automate Process in {dept}', f'Description for {req_id}', status, ba, sponsor_id, business_value, created_at.strftime("%Y-%m-%d %H:%M:%S"), 1))
            
            # Generate 2-5 Stories per Requirement
            num_stories = random.randint(2, 5)
            for s in range(num_stories):
                story_id = f'US-{story_counter:05d}'
                stories.append((story_id, req_id, 'User', 'do something', 'I get value', 'Criteria XYZ'))
                
                # Generate 1-3 Test Cases per Story
                num_tests = random.randint(1, 3)
                for t in range(num_tests):
                    test_id = f'TC-{test_counter:05d}'
                    
                    # 15% chance of high rework (Test Cycle > 1)
                    test_cycle = random.randint(2, 4) if random.random() < 0.15 else 1
                    
                    tc_status = 'Pass' if status in ['Deployed', 'Approved'] else random.choice(['Pass', 'Fail', 'Pending'])
                    if status == 'InUAT' and random.random() < 0.3:
                        tc_status = 'Fail' # Active defects
                        
                    test_cases.append((test_id, story_id, 'Verify something', tc_status, test_cycle))
                    test_counter += 1
                
                story_counter += 1
                
            # Audit and Approvals Generation
            if status != 'Draft':
                # Submission to Pending
                submit_date = created_at + timedelta(days=random.randint(1, 5))
                audits.append((req_id, ba, 'Draft', 'PendingReview', 'Submission', submit_date.strftime("%Y-%m-%d %H:%M:%S")))
                
                if status in ['InUAT', 'Deployed']:
                    # Simulate approval bottlenecks
                    delay_days = random.randint(10, 25) if dept == 'Risk & Compliance' else random.randint(1, 5)
                    approve_date = submit_date + timedelta(days=delay_days)
                    
                    approvals.append((f'APP-{app_counter}', req_id, sponsor_id, 'Approved', 'Looks good', approve_date.strftime("%Y-%m-%d %H:%M:%S")))
                    app_counter += 1
                    
                    audits.append((req_id, sponsor_id, 'PendingReview', 'Approved', 'Stakeholder Signoff', approve_date.strftime("%Y-%m-%d %H:%M:%S")))
                    
                    # UAT and Deploy
                    if status == 'Deployed':
                        deploy_date = approve_date + timedelta(days=random.randint(14, 30))
                        audits.append((req_id, ba, 'Approved', 'Deployed', 'Release', deploy_date.strftime("%Y-%m-%d %H:%M:%S")))

        cursor.executemany('INSERT INTO requirements VALUES (?,?,?,?,?,?,?,?,?,?)', reqs)
        cursor.executemany('INSERT INTO user_stories VALUES (?,?,?,?,?,?)', stories)
        cursor.executemany('INSERT INTO test_cases VALUES (?,?,?,?,?)', test_cases)
        cursor.executemany('INSERT INTO approvals VALUES (?,?,?,?,?,?)', approvals)
        cursor.executemany('INSERT INTO audit_logs (req_id, user_id, old_status, new_status, action_type, timestamp) VALUES (?,?,?,?,?,?)', audits)
        
        conn.commit()
        conn.close()
        print("Data generation complete!")

if __name__ == "__main__":
    db = DatabaseManager()
    db.initialize_database()
    db.seed_mock_data()
