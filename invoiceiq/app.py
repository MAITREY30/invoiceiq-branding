import streamlit as st
import time
import os
import sys

# Setup
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.stats_utils import refresh_invoice_counts
from config import settings

# Page config
st.set_page_config(
    page_title=settings.PRODUCT_SHORT_NAME,
    page_icon=settings.PRODUCT_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "invoices_data" not in st.session_state:
    st.session_state.invoices_data = refresh_invoice_counts()

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Auto-refresh every 30 seconds
if time.time() - st.session_state.last_refresh > 30:
    st.session_state.invoices_data = refresh_invoice_counts()
    st.session_state.last_refresh = time.time()

# Sidebar
st.sidebar.title(f"{settings.PRODUCT_SHORT_NAME} Hub")
st.sidebar.markdown("---")

st.sidebar.markdown("""
### About This System
InvoiceIQ is a modern invoice review platform featuring:
- 🤖 Automated data extraction
- ✅ Adaptive validation orchestration
- 👤 Collaborative review workflow
- 💬 RAG-driven knowledge assistant
- 📊 Live operational dashboards
""")

st.sidebar.markdown("---")
st.sidebar.info("💡 Use the navigation above to access different modules")

# Main Dashboard
st.title("📊 Dashboard")
st.markdown("Real-time invoice processing analytics and insights")

data = st.session_state.invoices_data

# Add refresh button
col_title, col_refresh = st.columns([6, 1])
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state.invoices_data = refresh_invoice_counts()
        st.session_state.last_refresh = time.time()
        st.rerun()

st.divider()

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📥 Total Invoices",
        value=data["total_received"],
        help="Total number of invoices received"
    )

with col2:
    st.metric(
        label="✅ Successfully Processed",
        value=data["successfully_processed"],
        delta=f"{data['auto_processing_rate']:.1f}% auto",
        help="Invoices that passed validation"
    )

with col3:
    st.metric(
        label="⏳ Pending Review",
        value=data["pending_review"],
        delta_color="inverse",
        help="Invoices awaiting human review"
    )

with col4:
    st.metric(
        label="❌ Rejected",
        value=data["rejected"],
        delta_color="inverse",
        help="Invoices that were rejected"
    )

st.divider()

st.markdown("#### 🔐 Invoice Health Summary")
health_col1, health_col2, health_col3 = st.columns(3)

with health_col1:
    st.metric(
        label="⚠️ Risk Score",
        value=f"{data['risk_score']:.0f}%",
        delta="Higher means more manual remediation",
        help="Composite risk estimate based on pending and rejected invoices"
    )

with health_col2:
    st.metric(
        label="💚 Health Score",
        value=f"{data['health_score']:.0f}%",
        help="Operational health rating for invoice processing"
    )

with health_col3:
    st.metric(
        label="🚀 Review Efficiency",
        value=f"{data['review_efficiency']:.0f}%",
        help="Estimated share of invoices processed without delay"
    )

st.divider()

# Performance Indicators
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 Acceptance Rate")
    acceptance_rate = min(data["acceptance_rate"] / 100, 1.0)
    st.progress(acceptance_rate)
    
    # Color-coded status
    if data["acceptance_rate"] >= 90:
        status_color = "🟢"
        status_text = "Excellent"
    elif data["acceptance_rate"] >= 75:
        status_color = "🟡"
        status_text = "Good"
    else:
        status_color = "🔴"
        status_text = "Needs Attention"
    
    st.markdown(f"**{data['acceptance_rate']:.1f}%** of invoices accepted {status_color} *{status_text}*")

with col2:
    st.markdown("#### ⚡ Automatic Processing Rate")
    auto_rate = min(data["auto_processing_rate"] / 100, 1.0)
    st.progress(auto_rate)
    
    # Color-coded status
    if data["auto_processing_rate"] >= 80:
        status_color = "🟢"
        status_text = "Excellent"
    elif data["auto_processing_rate"] >= 60:
        status_color = "🟡"
        status_text = "Good"
    else:
        status_color = "🔴"
        status_text = "Needs Attention"
    
    st.markdown(f"**{data['auto_processing_rate']:.1f}%** processed automatically {status_color} *{status_text}*")

st.divider()

# Status Distribution
st.markdown("#### 📊 Invoice Status Distribution")

status_data = {
    "Auto-Processed": data["auto_processed"],
    "Pending Review": data["pending_review"],
    "Approved": data["approved"],
    "Rejected": data["rejected"]
}

col1, col2 = st.columns([2, 1])

with col1:
    st.bar_chart(status_data, height=300)

with col2:
    st.markdown("##### Status Breakdown")
    for status, count in status_data.items():
        if count > 0:
            percentage = (count / data["total_received"] * 100) if data["total_received"] > 0 else 0
            st.metric(status, count, f"{percentage:.1f}%")

st.divider()

# Quick Actions
st.markdown("#### ⚡ Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if data["pending_review"] > 0:
        if st.button("🔍 Review Pending Invoices", use_container_width=True, type="primary"):
            st.switch_page("pages/2_🔍_Review_Queue.py")
    else:
        st.button("🔍 Review Pending Invoices", use_container_width=True, disabled=True)
        st.caption("✅ No invoices pending review")

with col2:
    if st.button("💬 Ask Chatbot", use_container_width=True):
        st.switch_page("pages/1_💬_Chatbot.py")

with col3:
    if st.button("📡 Monitor Pipeline", use_container_width=True):
        st.switch_page("pages/3_📡_Monitor.py")

# Footer
st.divider()
st.caption(f"Last refreshed: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.session_state.last_refresh))} • Auto-refresh every 30 seconds")