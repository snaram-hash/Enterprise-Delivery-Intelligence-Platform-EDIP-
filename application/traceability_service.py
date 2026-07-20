import sqlite3
import pandas as pd
import os

class TraceabilityService:
    def __init__(self, db_path=None):
        if not db_path:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "erdmp_enterprise.db")
        else:
            self.db_path = db_path

    def get_full_traceability_matrix(self):
        """
        Retrieves the multi-level hierarchy: Requirement -> User Story -> Test Case
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT 
            r.req_id, r.title AS requirement_title, r.status AS req_status,
            u.story_id, u.as_a, u.i_want_to,
            t.test_id, t.test_description, t.execution_status
        FROM requirements r
        LEFT JOIN user_stories u ON r.req_id = u.req_id
        LEFT JOIN test_cases t ON u.story_id = t.story_id
        WHERE r.is_active = 1
        ORDER BY r.req_id, u.story_id, t.test_id
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_missing_test_coverage(self):
        """
        Returns a list of User Stories that have 0 linked Test Cases.
        This is critical for Compliance Audit readiness.
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT u.story_id, u.i_want_to, r.req_id 
        FROM user_stories u
        LEFT JOIN test_cases t ON u.story_id = t.story_id
        JOIN requirements r ON u.req_id = r.req_id
        WHERE t.test_id IS NULL AND r.is_active = 1
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
