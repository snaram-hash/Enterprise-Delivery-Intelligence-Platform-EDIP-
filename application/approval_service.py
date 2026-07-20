import sqlite3
import os
from datetime import datetime

class ApprovalService:
    def __init__(self, db_path=None):
        if not db_path:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "erdmp_enterprise.db")
        else:
            self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_pending_approvals_for_user(self, user_id):
        conn = self.get_connection()
        query = '''
        SELECT a.approval_id, r.req_id, r.title, r.version, a.status 
        FROM approvals a
        JOIN requirements r ON a.req_id = r.req_id
        WHERE a.approver_id = ? AND a.status = 'Pending' AND r.is_active = 1
        '''
        cursor = conn.execute(query, (user_id,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def sign_approval(self, approval_id, user_id, action="Approve", comments=""):
        """
        Executes the digital signature.
        If 'Approve', it checks if all other approvers for this req have also approved.
        If so, it transitions the main Requirement state to 'Approved'.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Update the junction table
        new_app_status = 'Approved' if action == 'Approve' else 'Rejected'
        cursor.execute('''
            UPDATE approvals 
            SET status = ?, comments = ?, timestamp = ? 
            WHERE approval_id = ? AND approver_id = ?
        ''', (new_app_status, comments, now, approval_id, user_id))

        # 2. Find the parent Requirement ID
        cursor.execute("SELECT req_id FROM approvals WHERE approval_id = ?", (approval_id,))
        req_id = cursor.fetchone()['req_id']

        # 3. Check global state machine
        if new_app_status == 'Rejected':
            # Fast fail: One rejection pushes the whole requirement back to Draft
            self._transition_requirement_state(cursor, req_id, user_id, 'Draft', 'Rejected by Stakeholder')
        else:
            # Check if all approvers are now 'Approved'
            cursor.execute("SELECT COUNT(*) as count FROM approvals WHERE req_id = ? AND status != 'Approved'", (req_id,))
            pending_count = cursor.fetchone()['count']
            
            if pending_count == 0:
                self._transition_requirement_state(cursor, req_id, user_id, 'Approved', 'All Signatures Gathered')

        conn.commit()
        conn.close()

    def _transition_requirement_state(self, cursor, req_id, user_id, new_status, reason):
        """
        Internal state machine transactor with IMMUTABLE AUDIT LOGGING.
        """
        cursor.execute("SELECT status FROM requirements WHERE req_id = ? AND is_active = 1", (req_id,))
        old_status = cursor.fetchone()['status']

        if old_status == new_status:
            return

        # Update core entity
        cursor.execute("UPDATE requirements SET status = ? WHERE req_id = ? AND is_active = 1", (new_status, req_id))
        
        # Write to immutable audit ledger
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO audit_logs (req_id, user_id, old_status, new_status, action_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (req_id, user_id, old_status, new_status, reason, now))
