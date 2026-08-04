import streamlit as st
import pandas as pd
from database.db import run_query

def render_dashboard():
    st.header("📈 Executive Management Dashboard")
    
    # Query summary metrics
    query = """
        SELECT 
            COUNT(opportunity_id) as total_deals,
            COALESCE(SUM(quotation_amount), 0) as total_quoted,
            COALESCE(SUM(amount_paid), 0) as total_collected,
            COALESCE(SUM(CASE WHEN deal_status = 'Success (Order Won)' THEN quotation_amount ELSE 0 END), 0) as total_revenue_won,
            COALESCE(SUM(quotation_amount - amount_paid), 0) as total_outstanding
        FROM opportunities;
    """
    df_metrics = run_query(query)

    row = df_metrics.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Deals Logged", int(row["total_deals"]))
    col2.metric("Total Quoted (UGX)", f"{row['total_quoted']:,.0f}")
    col3.metric("Total Revenue Won (UGX)", f"{row['total_revenue_won']:,.0f}")
    col4.metric("Outstanding Collection (UGX)", f"{row['total_outstanding']:,.0f}")
    
    st.markdown("---")
    
    # Executive Leaderboard
    st.subheader("🏆 Sales Executive Leaderboard")
    leaderboard_query = """
        SELECT 
            u.full_name as 'Sales Executive',
            COUNT(o.opportunity_id) as 'Total Deals',
            COALESCE(SUM(o.quotation_amount), 0) as 'Quoted Value (UGX)',
            COALESCE(SUM(CASE WHEN o.deal_status = 'Success (Order Won)' THEN o.quotation_amount ELSE 0 END), 0) as 'Revenue Won (UGX)',
            COALESCE(SUM(o.amount_paid), 0) as 'Collections (UGX)'
        FROM users u
        LEFT JOIN opportunities o ON u.user_id = o.sales_executive_id
        GROUP BY u.user_id, u.full_name
        ORDER BY 'Revenue Won (UGX)' DESC;
    """
    df_leaderboard = run_query(leaderboard_query)
    st.dataframe(df_leaderboard, use_container_width=True)
