import streamlit as st
from database.db import run_query

def render_traffic_lights():
    st.header("🚥 Management Traffic Light Dashboard")
    st.caption("Real-Time Operational & Performance Health Indicators")

    # Metrics Query
    query = """
        SELECT 
            COUNT(opportunity_id) as total_deals,
            SUM(CASE WHEN deal_status = 'Success (Order Won)' THEN 1 ELSE 0 END) as won_deals,
            SUM(quotation_amount) as total_quoted,
            SUM(amount_paid) as total_paid,
            SUM(quotation_amount - amount_paid) as total_ar,
            SUM(CASE WHEN strftime('%Y-%m-%d', next_followup_date) < DATE('now') AND deal_status = 'Pipeline' THEN 1 ELSE 0 END) as overdue_followups
        FROM opportunities;
    """
    df = run_query(query).iloc[0]
    
    total_deals = df['total_deals'] or 1
    win_rate = (df['won_deals'] / total_deals) * 100
    overdue = df['overdue_followups'] or 0
    collection_rate = (df['total_paid'] / df['total_quoted'] * 100) if df['total_quoted'] else 0

    col1, col2, col3 = st.columns(3)

    # Indicator 1: Win Rate
    with col1:
        if win_rate >= 35:
            st.success(f"🟢 **Win Rate Health: EXCELLENT ({win_rate:.1f}%)**\n\nConversion exceeds target threshold (>35%).")
        elif win_rate >= 20:
            st.warning(f"🟡 **Win Rate Health: WARNING ({win_rate:.1f}%)**\n\nConversion rate is moderate (20-35%).")
        else:
            st.error(f"🔴 **Win Rate Health: CRITICAL ({win_rate:.1f}%)**\n\nConversion is below acceptable levels (<20%).")

    # Indicator 2: Collections & Debt
    with col2:
        if collection_rate >= 75:
            st.success(f"🟢 **Collection Health: GOOD ({collection_rate:.1f}%)**\n\nCash flow collections are on track.")
        elif collection_rate >= 50:
            st.warning(f"🟡 **Collection Health: FAIR ({collection_rate:.1f}%)**\n\nOutstanding balance needs attention.")
        else:
            st.error(f"🔴 **Collection Health: ACTION REQUIRED ({collection_rate:.1f}%)**\n\nHigh ratio of uncollected revenue.")

    # Indicator 3: Operational Pipeline / Follow-ups
    with col3:
        if overdue == 0:
            st.success("🟢 **Follow-up Health: CLEAN**\n\nNo overdue client interactions.")
        elif overdue <= 5:
            st.warning(f"🟡 **Follow-up Health: ATTENTION ({overdue} Overdue)**\n\nFew pending follow-ups past deadline.")
        else:
            st.error(f"🔴 **Follow-up Health: BOTTLENECK ({overdue} Overdue)**\n\nMultiple client follow-ups are lagging.")