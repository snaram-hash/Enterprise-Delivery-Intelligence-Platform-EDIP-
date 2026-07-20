import streamlit as st
import sqlite3
import pandas as pd
import sys
import os

# Add Application Layer to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'application'))
from traceability_service import TraceabilityService
from approval_service import ApprovalService

# --- CONFIGURATION ---
st.set_page_config(page_title="ERDMP | Executive Portal", layout="wide", page_icon="📝")
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "erdmp_enterprise.db")

# Initialize Services
trace_svc = TraceabilityService(db_path)
appr_svc = ApprovalService(db_path)

# --- MOCK AUTHENTICATION ---
# In a real enterprise app, this would be SAML/SSO
st.sidebar.title("🔐 Simulated SSO")
user_role = st.sidebar.selectbox("Log in as:", [
    "U002 (David Chen - Business Sponsor)", 
    "U001 (Sarah Jenkins - Lead BA)",
    "U003 (Marcus Johnson - Lead Engineer)",
    "U004 (Elena Rodriguez - QA/Compliance)"
])
active_user_id = user_role.split(' ')[0]

st.sidebar.markdown("---")
st.sidebar.info("Enterprise Requirements & Decision Management Platform v1.0")

# --- NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "✅ My Approvals Queue", "🔗 Traceability & Compliance Audit"])

# -----------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# -----------------------------------------
with tab1:
    st.header("Enterprise Requirement Health")
    
    conn = sqlite3.connect(db_path)
    
    # KPI Metrics
    c1, c2, c3 = st.columns(3)
    total_reqs = pd.read_sql_query("SELECT COUNT(*) as c FROM requirements WHERE is_active=1", conn).iloc[0]['c']
    pending_reqs = pd.read_sql_query("SELECT COUNT(*) as c FROM requirements WHERE status='PendingReview' AND is_active=1", conn).iloc[0]['c']
    missing_tests = trace_svc.get_missing_test_coverage()
    
    c1.metric("Total Active Requirements", total_reqs)
    c2.metric("Pending Approvals Bottleneck", pending_reqs, delta=f"{pending_reqs} delaying sprint", delta_color="inverse")
    
    if len(missing_tests) > 0:
        c3.metric("Missing Test Coverage", len(missing_tests), delta="Compliance Risk", delta_color="inverse")
    else:
        c3.metric("Missing Test Coverage", 0, delta="100% Traced", delta_color="normal")
        
    st.divider()
    st.subheader("Recent Audit Ledger (System of Record)")
    audit_df = pd.read_sql_query('''
        SELECT a.timestamp, u.name as actor, a.action_type, r.title, a.old_status, a.new_status 
        FROM audit_logs a
        JOIN users u ON a.user_id = u.user_id
        JOIN requirements r ON a.req_id = r.req_id
        ORDER BY a.timestamp DESC LIMIT 10
    ''', conn)
    st.dataframe(audit_df, use_container_width=True)
    
    conn.close()

# -----------------------------------------
# TAB 2: MY APPROVALS QUEUE
# -----------------------------------------
with tab2:
    st.header(f"Action Required Queue")
    
    pending = appr_svc.get_pending_approvals_for_user(active_user_id)
    
    if not pending:
        st.success("Your approval queue is clear. No blockers assigned to you.")
    else:
        for req in pending:
            with st.expander(f"🔴 PENDING SIGNATURE: {req['req_id']} - {req['title']} (v{req['version']})", expanded=True):
                # Pull full details
                conn = sqlite3.connect(db_path)
                desc = pd.read_sql_query(f"SELECT description FROM requirements WHERE req_id='{req['req_id']}' AND is_active=1", conn).iloc[0]['description']
                stories = pd.read_sql_query(f"SELECT story_id, i_want_to, acceptance_criteria FROM user_stories WHERE req_id='{req['req_id']}'", conn)
                conn.close()
                
                st.markdown(f"**Business Justification:** {desc}")
                
                st.markdown("**Linked Engineering Specs (User Stories):**")
                st.table(stories)
                
                comments = st.text_input("Approval / Rejection Comments", key=f"comment_{req['approval_id']}")
                
                col1, col2 = st.columns(2)
                if col1.button("✅ Approve & Digitally Sign", key=f"app_{req['approval_id']}", type="primary"):
                    appr_svc.sign_approval(req['approval_id'], active_user_id, "Approve", comments)
                    st.success("Signed!")
                    st.rerun()
                if col2.button("❌ Reject back to Draft", key=f"rej_{req['approval_id']}"):
                    appr_svc.sign_approval(req['approval_id'], active_user_id, "Reject", comments)
                    st.error("Rejected.")
                    st.rerun()

# -----------------------------------------
# TAB 3: TRACEABILITY & COMPLIANCE AUDIT
# -----------------------------------------
with tab3:
    st.header("Requirement Traceability Matrix (RTM)")
    st.markdown("Bi-directional linkage proving that every engineered feature maps to an approved Business Rule.")
    
    df_matrix = trace_svc.get_full_traceability_matrix()
    st.dataframe(df_matrix, use_container_width=True)
    
    st.divider()
    st.subheader("Compliance Exception Report")
    if len(missing_tests) > 0:
        st.warning("⚠️ The following User Stories are orphaned (no linked Test Cases). They cannot pass UAT compliance.")
        st.dataframe(missing_tests, use_container_width=True)
    else:
        st.success("All User Stories have full Test Case coverage.")
