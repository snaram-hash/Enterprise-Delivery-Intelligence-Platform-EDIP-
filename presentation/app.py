import streamlit as st
import sqlite3
import pandas as pd
import sys
import os

# Add Application Layer to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'application'))
from traceability_service import TraceabilityService
from analytics_service import DeliveryAnalyticsService

# --- CONFIGURATION ---
st.set_page_config(page_title="EDIP | Executive Delivery Intelligence", layout="wide", page_icon="📈")
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "edip_enterprise.db")

# Initialize Services
trace_svc = TraceabilityService(db_path)
analytics_svc = DeliveryAnalyticsService(db_path)

# --- HEADER ---
st.title("Enterprise Delivery Intelligence Platform")
st.markdown("Turning software delivery data into executive decisions.")
st.divider()

# --- KILLER DASHBOARD (The CIO View) ---
st.header("Executive Release Health")

metrics = analytics_svc.get_killer_metrics()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Release Health Score", f"{metrics['health_score']}/100", delta="-2 from last week", delta_color="inverse")
col2.metric("Projects at Risk", metrics['projects_at_risk'], delta="Requires Intervention", delta_color="inverse")
col3.metric("Avg Approval Delay", f"{metrics['avg_approval_delay']} days")
col4.metric("Reqs Changed (Post-Approval)", metrics['requirements_changed'], delta="Scope Creep", delta_color="inverse")
col5.metric("Predicted Release Delay", f"{metrics['predicted_delay']} days")

# Format currency nicely
val = metrics['value_at_risk']
formatted_val = f"₹{val/10000000:.1f} Cr" if val >= 10000000 else f"₹{val:,.0f}"
col6.metric("Business Value at Risk", formatted_val)

st.divider()

# --- NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["📊 Portfolio Health Analysis", "⏳ Approval Bottlenecks", "🔗 Traceability & UAT Quality"])

# -----------------------------------------
# TAB 1: PORTFOLIO HEALTH ANALYSIS
# -----------------------------------------
with tab1:
    st.header("Requirement Volatility & Value Delivery")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Department Volatility Index")
        st.markdown("High average versions indicate requirements are changing post-approval (Ghost Edits/Scope Creep).")
        vol_df = analytics_svc.get_volatility_metrics()
        
        # Use Streamlit's native bar chart for quick visualization
        st.bar_chart(data=vol_df, x='department', y='avg_version_volatility', color="#FF5630")
        
    with col_b:
        st.subheader("Business Value by Department")
        st.markdown("Total estimated business value of active requirements.")
        st.bar_chart(data=vol_df, x='department', y='total_business_value', color="#0052CC")
        
    st.dataframe(vol_df, use_container_width=True)

# -----------------------------------------
# TAB 2: APPROVAL BOTTLENECKS
# -----------------------------------------
with tab2:
    st.header("SLA Breach & Approval Delay Analysis")
    st.markdown("Identifies which Sponsors are delaying the delivery pipeline by sitting on 'PendingReview' requests.")
    
    bottleneck_df = analytics_svc.get_approval_bottlenecks()
    
    # Highlight the biggest offender
    if not bottleneck_df.empty:
        worst_offender = bottleneck_df.iloc[0]
        st.error(f"🚨 **Critical Bottleneck Detected:** {worst_offender['sponsor_name']} ({worst_offender['department']}) averages **{worst_offender['avg_approval_days']:.1f} days** to approve requirements.")
        
    st.dataframe(bottleneck_df.style.highlight_max(subset=['avg_approval_days'], color='#ffcccc'), use_container_width=True)

# -----------------------------------------
# TAB 3: TRACEABILITY & UAT QUALITY
# -----------------------------------------
with tab3:
    st.header("UAT First-Pass Yield & Defect Heatmap")
    st.markdown("Analyzes engineering quality by tracking how many test cycles (rework) a requirement undergoes.")
    
    uat_df = analytics_svc.get_uat_quality_metrics()
    
    if not uat_df.empty:
        st.warning("Top 20 Requirements with Highest Rework (Test Cycles > 1)")
        st.dataframe(uat_df.style.background_gradient(subset=['max_rework_cycles'], cmap='Reds'), use_container_width=True)
    
    st.divider()
    
    st.subheader("Orphaned User Stories (Compliance Risk)")
    missing_tests = trace_svc.get_missing_test_coverage()
    if len(missing_tests) > 0:
        st.error(f"⚠️ Found {len(missing_tests)} User Stories with NO linked test cases. These will fail compliance audit.")
        st.dataframe(missing_tests, use_container_width=True)
    else:
        st.success("100% Test Case Coverage Achieved.")
