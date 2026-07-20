import sqlite3
import pandas as pd
import os

class DeliveryAnalyticsService:
    def __init__(self, db_path=None):
        if not db_path:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "edip_enterprise.db")
        else:
            self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_volatility_metrics(self):
        """
        Calculates the average version number.
        High average version indicates requirements are changing rapidly AFTER approval (Rework).
        """
        conn = self.get_connection()
        query = '''
        SELECT 
            u.department,
            COUNT(r.req_id) as total_requirements,
            AVG(r.version) as avg_version_volatility,
            SUM(r.business_value_est) as total_business_value
        FROM requirements r
        JOIN users u ON r.sponsor_id = u.user_id
        WHERE r.is_active = 1
        GROUP BY u.department
        ORDER BY avg_version_volatility DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_approval_bottlenecks(self):
        """
        Calculates the average days a requirement sits in "PendingReview" before Approval.
        Identifies which sponsors/departments are blocking delivery.
        """
        conn = self.get_connection()
        
        # We find the time difference between Submission (Draft->Pending) and Approval (Pending->Approved)
        query = '''
        WITH submissions AS (
            SELECT req_id, timestamp as submitted_at
            FROM audit_logs
            WHERE new_status = 'PendingReview'
        ),
        approvals AS (
            SELECT req_id, user_id as approver_id, timestamp as approved_at
            FROM audit_logs
            WHERE new_status = 'Approved' AND action_type = 'Stakeholder Signoff'
        )
        SELECT 
            u.name as sponsor_name,
            u.department,
            COUNT(a.req_id) as approved_count,
            AVG(JULIANDAY(a.approved_at) - JULIANDAY(s.submitted_at)) as avg_approval_days
        FROM approvals a
        JOIN submissions s ON a.req_id = s.req_id
        JOIN users u ON a.approver_id = u.user_id
        GROUP BY u.name, u.department
        ORDER BY avg_approval_days DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_uat_quality_metrics(self):
        """
        Calculates First-Pass Yield (Test cases passing on Cycle 1).
        High test cycles indicate poor initial engineering or poor requirement clarity.
        """
        conn = self.get_connection()
        query = '''
        SELECT 
            r.req_id,
            r.title,
            u.department,
            MAX(t.test_cycle) as max_rework_cycles,
            SUM(CASE WHEN t.execution_status = 'Fail' THEN 1 ELSE 0 END) as defect_count
        FROM requirements r
        JOIN user_stories us ON r.req_id = us.req_id
        JOIN test_cases t ON us.story_id = t.story_id
        JOIN users u ON r.sponsor_id = u.user_id
        WHERE r.is_active = 1
        GROUP BY r.req_id, r.title, u.department
        ORDER BY max_rework_cycles DESC, defect_count DESC
        LIMIT 20
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_killer_metrics(self):
        """
        Calculates the macro 'Killer Dashboard' metrics for the CIO view.
        """
        conn = self.get_connection()
        
        # 1. Average Approval Delay (across all)
        query_delay = '''
            WITH submissions AS (SELECT req_id, timestamp as submitted_at FROM audit_logs WHERE new_status = 'PendingReview'),
                 approvals AS (SELECT req_id, timestamp as approved_at FROM audit_logs WHERE new_status = 'Approved' AND action_type = 'Stakeholder Signoff')
            SELECT AVG(JULIANDAY(a.approved_at) - JULIANDAY(s.submitted_at)) as avg_delay
            FROM approvals a JOIN submissions s ON a.req_id = s.req_id
        '''
        avg_delay = pd.read_sql_query(query_delay, conn).iloc[0]['avg_delay']
        if pd.isna(avg_delay): avg_delay = 0
        
        # 2. Requirements Changed After Approval (Volatility)
        query_volatility = "SELECT COUNT(*) as c FROM requirements WHERE version > 1.0 AND is_active = 1"
        changed_reqs = pd.read_sql_query(query_volatility, conn).iloc[0]['c']
        
        # 3. Projects at Risk & Business Value at Risk
        # Risk defined as: version > 1.2 OR in PendingReview for > 7 days
        query_risk = '''
            SELECT COUNT(*) as risk_count, SUM(business_value_est) as risk_value
            FROM requirements r
            WHERE is_active = 1 AND (version > 1.2 OR status = 'PendingReview')
        '''
        risk_data = pd.read_sql_query(query_risk, conn).iloc[0]
        projects_at_risk = risk_data['risk_count'] or 0
        value_at_risk = risk_data['risk_value'] or 0
        
        # 4. Release Health Score (Heuristic: 100 - (projects at risk * 2) - (avg delay))
        health_score = max(0, min(100, 100 - (projects_at_risk * 1.5) - (avg_delay * 2)))
        
        # 5. Predicted Release Delay (Heuristic based on approval delay and rework)
        predicted_delay = avg_delay * 1.4 # Rough multiplier for UAT delays
        
        conn.close()
        
        return {
            'health_score': int(health_score),
            'projects_at_risk': int(projects_at_risk),
            'avg_approval_delay': round(avg_delay, 1),
            'requirements_changed': int(changed_reqs),
            'predicted_delay': round(predicted_delay, 1),
            'value_at_risk': int(value_at_risk)
        }
