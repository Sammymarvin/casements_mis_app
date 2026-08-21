import streamlit as st
import pandas as pd
from database.db import run_query

def render_dashboard():
    st.header("📈 Executive Management Dashboard")
    
    # ----------------------------------------------------
    # DYNAMIC MONTH SELECTION
    # ----------------------------------------------------
    months_query = """
        SELECT DISTINCT TO_CHAR(date_entered, 'YYYY-MM') as month_val 
        FROM opportunities 
        WHERE date_entered IS NOT NULL 
        ORDER BY month_val DESC;
    """
    try:
        df_months = run_query(months_query)
        available_months = df_months["month_val"].dropna().tolist() if not df_months.empty else []
    except Exception:
        available_months = []

    month_options = ["All Time"] + available_months
    
    # Month Filter Control
    selected_month = st.selectbox("📅 Filter Performance by Month", month_options, index=0)
    
    # ----------------------------------------------------
    # 1. EXECUTIVE SUMMARY METRICS QUERY
    # ----------------------------------------------------
    if selected_month != "All Time":
        metrics_query = """
            SELECT 
                COUNT(opportunity_id) as total_deals,
                COALESCE(SUM(quotation_amount), 0) as total_quoted,
                COALESCE(SUM(amount_paid), 0) as total_collected,
                COALESCE(SUM(CASE WHEN deal_status = 'Success (Order Won)' THEN quotation_amount ELSE 0 END), 0) as total_revenue_won,
                COALESCE(SUM(quotation_amount - amount_paid), 0) as total_outstanding
            FROM opportunities
            WHERE TO_CHAR(date_entered, 'YYYY-MM) = %s;
        """
        metrics_params = (selected_month,)
    else:
        metrics_query = """
            SELECT 
                COUNT(opportunity_id) as total_deals,
                COALESCE(SUM(quotation_amount), 0) as total_quoted,
                COALESCE(SUM(amount_paid), 0) as total_collected,
                COALESCE(SUM(CASE WHEN deal_status = 'Success (Order Won)' THEN quotation_amount ELSE 0 END), 0) as total_revenue_won,
                COALESCE(SUM(quotation_amount - amount_paid), 0) as total_outstanding
            FROM opportunities;
        """
        metrics_params = None
    
    df_metrics = run_query(metrics_query, metrics_params)
    row = df_metrics.iloc[0] if not df_metrics.empty else {
        "total_deals": 0, "total_quoted": 0, "total_revenue_won": 0, "total_outstanding": 0
    }
    
    # Metrics Layout Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Deals Logged", int(row["total_deals"]))
    col2.metric("Total Quoted (UGX)", f"{row['total_quoted']:,.0f}")
    col3.metric("Total Revenue Won (UGX)", f"{row['total_revenue_won']:,.0f}")
    col4.metric("Outstanding Collection (UGX)", f"{row['total_outstanding']:,.0f}")
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # 2. EXECUTIVE LEADERBOARD QUERY
    # ----------------------------------------------------
    st.subheader(f"🏆 Sales Executive Leaderboard ({selected_month})")
    
    # Using a raw string without f-string formatting to avoid any % character conflict
    leaderboard_query = """
        SELECT 
            u.full_name as "Sales Executive",
            COUNT(o.opportunity_id) as "Total Deals",
            COALESCE(SUM(o.quotation_amount), 0) as "Quoted Value (UGX)",
            COALESCE(SUM(CASE WHEN o.deal_status = 'Success (Order Won)' THEN o.quotation_amount ELSE 0 END), 0) as "Revenue Won (UGX)",
            COALESCE(SUM(o.amount_paid), 0) as "Collections (UGX)"
        FROM users u
        LEFT JOIN opportunities o ON u.user_id = o.sales_executive_id 
            AND (%s = 'All Time' OR TO_CHAR(o.date_entered, 'YYYY-MM') = %s)
        WHERE u.role IN ('Sales Executive', 'General Manager')
        GROUP BY u.user_id, u.full_name
        ORDER BY COALESCE(SUM(CASE WHEN o.deal_status = 'Success (Order Won)' THEN o.quotation_amount ELSE 0 END), 0) DESC,
                 COUNT(o.opportunity_id) DESC;
    """
    
    leaderboard_params = (selected_month, selected_month)
    df_leaderboard = run_query(leaderboard_query, leaderboard_params)
        
    st.dataframe(df_leaderboard, use_container_width=True, hide_index=True)