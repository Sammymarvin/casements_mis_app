import streamlit as st
import pandas as pd
import datetime
from database.db import run_query
from ui.theme import render_header

def calculate_traffic_light(metric_type, actual, target):
    """Calculates status indicator color based on Casements Management Traffic Light Rules."""
    if target == 0:
        return "⚪ N/A"
    
    pct = (actual / target) * 100
    
    if metric_type == "revenue":
        if pct >= 100: return "🟢 Green (Above Target)"
        elif pct >= 80: return "🟡 Orange (80-99%)"
        else: return "🔴 Red (Below 80%)"
        
    elif metric_type == "quotations":
        if actual >= 80: return "🟢 Green (Above 80)"
        elif actual >= 60: return "🟡 Orange (60-79)"
        else: return "🔴 Red (Below 60)"
        
    elif metric_type == "collections":
        if pct >= 95: return "🟢 Green (Above 95%)"
        elif pct >= 90: return "🟡 Orange (90-94%)"
        else: return "🔴 Red (Below 90%)"
        
    elif metric_type == "pipeline":
        if actual >= 3000000000: return "🟢 Green (> UGX 3B)"
        elif actual >= 2000000000: return "🟡 Orange (UGX 2B - 3B)"
        else: return "🔴 Red (< UGX 2B)"
        
    return "⚪ N/A"

def render_metric_card(title, value, subtitle="", status_color="#2563EB", icon="📊"):
    """Helper to render modern styled executive KPI cards."""
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(229, 231, 235, 0.2);
        border-left: 5px solid {status_color};
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <div style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #6B7280; letter-spacing: 0.5px;">
            {icon} {title}
        </div>
        <div style="font-size: 1.6rem; font-weight: 700; margin: 6px 0; color: #1F2937;">
            {value}
        </div>
        <div style="font-size: 0.8rem; font-weight: 500; color: {status_color};">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_analytics():
    render_header(
        title="📊 Casements MIS 2026 - Executive Performance Hub", 
        subtitle="Business Turnaround Strategy Dashboard | Sales & Marketing Analytics"
    )

    # Sidebar View Selector
    menu = st.sidebar.radio(
        "Analytics Views", 
        [
            "🚦 Executive Traffic Light Panel", 
            "🎯 Corporate KPI Scorecard", 
            "📆 Daily Sales Activity Dashboard",
            "🏆 Sales Executive Leaderboard", 
            "📉 Sales Funnel & Pipeline",
            "🏢 Market Segment & Product Scope"
        ]
    )

    # Query Base Opportunities Data
    query_opps = """
        SELECT 
            o.opportunity_id,
            o.record_code AS [Code],
            o.date_entered AS [Date],
            u.full_name AS [Sales Exec],
            c.company_name AS [Client],
            o.project_type AS [Project Type],
            o.scope_of_work AS [Scope],
            o.quotation_amount AS [Quotation],
            o.amount_paid AS [Paid],
            (o.quotation_amount - o.amount_paid) AS [Balance],
            o.deal_status AS [Status],
            o.reason_for_loss AS [Reason for Loss]
        FROM opportunities o
        LEFT JOIN users u ON o.sales_executive_id = u.user_id
        LEFT JOIN clients c ON o.client_id = c.client_id
    """
    df = run_query(query_opps)

    if df.empty:
        st.info("No sales records available to generate performance analytics. Create records in the Master Entry module.")
        return

    # Clean numerical values
    df['Quotation'] = df['Quotation'].fillna(0.0).astype(float)
    df['Paid'] = df['Paid'].fillna(0.0).astype(float)
    df['Balance'] = df['Balance'].fillna(0.0).astype(float)

    # Key Aggregated Metrics
    total_pipeline_val = df['Quotation'].sum()
    total_revenue_collected = df['Paid'].sum()
    total_quotations_issued = len(df)
    orders_won = len(df[df['Status'] == 'Success (Order Won)'])
    conversion_rate = (orders_won / total_quotations_issued * 100) if total_quotations_issued > 0 else 0.0
    collection_rate = (total_revenue_collected / total_pipeline_val * 100) if total_pipeline_val > 0 else 0.0

    # ==========================================
    # VIEW 1: EXECUTIVE TRAFFIC LIGHT PANEL
    # ==========================================
    if menu == "🚦 Executive Traffic Light Panel":
        st.markdown("### 🚥 Management Traffic Light Report")
        st.caption("Strategic alignment monitoring based on executive target thresholds.")

        target_revenue = 1000000000.0  # UGX 1 Billion Monthly Target
        target_quotes = 80
        target_pipeline = 3000000000.0  # UGX 3 Billion Pipeline Target

        rev_status = calculate_traffic_light("revenue", total_revenue_collected, target_revenue)
        quote_status = calculate_traffic_light("quotations", total_quotations_issued, target_quotes)
        coll_status = calculate_traffic_light("collections", collection_rate, 95.0)
        pipe_status = calculate_traffic_light("pipeline", total_pipeline_val, target_pipeline)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            render_metric_card("Monthly Revenue", f"UGX {total_revenue_collected:,.0f}", f"Target: UGX 1B | {rev_status}", "#059669" if "Green" in rev_status else "#DC2626", "💰")

        with c2:
            render_metric_card("Quotations Issued", f"{total_quotations_issued}", f"Target: {target_quotes} | {quote_status}", "#2563EB" if "Green" in quote_status else "#D97706", "📄")

        with c3:
            render_metric_card("Collection Rate", f"{collection_rate:.1f}%", f"Target: 95.0% | {coll_status}", "#059669" if "Green" in coll_status else "#DC2626", "🏦")

        with c4:
            render_metric_card("Pipeline Value", f"UGX {total_pipeline_val:,.0f}", f"Target: UGX 3B | {pipe_status}", "#7C3AED" if "Green" in pipe_status else "#D97706", "📈")

        st.divider()

        st.markdown("#### 📋 Executive Summary Status Table")
        summary_data = [
            {"KPI Indicator": "Monthly Revenue (UGX)", "Target": "1,000,000,000", "Actual": f"{total_revenue_collected:,.0f}", "Status": rev_status},
            {"KPI Indicator": "Quotations Submitted", "Target": "80", "Actual": f"{total_quotations_issued}", "Status": quote_status},
            {"KPI Indicator": "Quotation Conversion Rate", "Target": "35.0%", "Actual": f"{conversion_rate:.1f}%", "Status": "🟢 Green" if conversion_rate >= 35 else "🔴 Red"},
            {"KPI Indicator": "Outstanding Collections Rate", "Target": "95.0%", "Actual": f"{collection_rate:.1f}%", "Status": coll_status},
            {"KPI Indicator": "Total Pipeline Value (UGX)", "Target": "3,000,000,000", "Actual": f"{total_pipeline_val:,.0f}", "Status": pipe_status},
        ]
        st.table(pd.DataFrame(summary_data))

    # ==========================================
    # VIEW 2: CORPORATE KPI SCORECARD
    # ==========================================
    elif menu == "🎯 Corporate KPI Scorecard":
        st.markdown("### 🎯 Departmental KPI Scorecard")
        st.caption("Sales & Marketing Target vs. Actual Variance Analysis")

        scorecard_df = pd.DataFrame([
            {"KPI Metric": "Monthly Revenue", "Target": 1000000000.0, "Actual": total_revenue_collected, "Unit": "UGX"},
            {"KPI Metric": "Orders Won", "Target": 80, "Actual": orders_won, "Unit": "Deals"},
            {"KPI Metric": "Quotations Issued", "Target": 80, "Actual": total_quotations_issued, "Unit": "Quotes"},
            {"KPI Metric": "Quotation Conversion Rate", "Target": 35.0, "Actual": conversion_rate, "Unit": "%"},
            {"KPI Metric": "Collection Percentage", "Target": 95.0, "Actual": collection_rate, "Unit": "%"},
        ])

        scorecard_df['Variance'] = scorecard_df['Actual'] - scorecard_df['Target']
        scorecard_df['Achievement %'] = (scorecard_df['Actual'] / scorecard_df['Target'] * 100).round(1)

        st.dataframe(
            scorecard_df.style.format({
                "Target": "{:,.1f}",
                "Actual": "{:,.1f}",
                "Variance": "{:,.1f}",
                "Achievement %": "{:.1f}%"
            }),
            use_container_width=True
        )

        st.divider()
        st.markdown("### 📅 Monthly Sales Revenue Goal Progress")
        st.progress(min(float(total_revenue_collected / 1000000000.0), 1.0))

    # ==========================================
    # VIEW 3: DAILY SALES ACTIVITY DASHBOARD
    # ==========================================
    elif menu == "📆 Daily Sales Activity Dashboard":
        st.markdown("### 📆 Individual & Team Daily Sales Activity Dashboard")
        st.caption("Tracking field execution, telephone calls, meetings, and lead generation.")

        # Updated query matching daily_activity_logs table schema
        query_logs = """
            SELECT 
                dal.log_date AS [Date],
                u.full_name AS [Sales Exec],
                dal.new_companies_visited AS [Companies Visited],
                dal.telephone_calls AS [Calls Made],
                dal.emails_sent AS [Emails Sent],
                dal.meetings_held AS [Meetings Held],
                dal.new_leads_generated AS [New Leads],
                dal.daily_challenges AS [Challenges],
                dal.management_support_needed AS [Mgmt Support],
                dal.remarks AS [Remarks]
            FROM daily_activity_logs dal
            LEFT JOIN users u ON dal.sales_executive_id = u.user_id
            ORDER BY dal.log_date DESC
        """
        try:
            df_logs = run_query(query_logs)
        except Exception:
            df_logs = pd.DataFrame()

        if df_logs.empty:
            st.info("No daily activity log records found in 'daily_activity_logs'.")
        else:
            # Aggregate Daily Summary Cards
            c_a, c_b, c_c, c_d = st.columns(4)
            with c_a:
                render_metric_card("Telephone Calls", f"{df_logs['Calls Made'].sum():,.0f}", "Target: 20 / Exec / Day", "#2563EB", "📞")
            with c_b:
                render_metric_card("Companies Visited", f"{df_logs['Companies Visited'].sum():,.0f}", "Target: 5 / Exec / Day", "#059669", "🏢")
            with c_c:
                render_metric_card("Meetings Held", f"{df_logs['Meetings Held'].sum():,.0f}", "Target: 3 / Exec / Day", "#7C3AED", "🤝")
            with c_d:
                render_metric_card("New Leads", f"{df_logs['New Leads'].sum():,.0f}", "Target: 5 / Exec / Day", "#D97706", "⚡")

            st.divider()

            st.markdown("#### 👤 Daily Activity Totals by Sales Executive")
            exec_logs = df_logs.groupby('Sales Exec').agg({
                'Companies Visited': 'sum',
                'Calls Made': 'sum',
                'Emails Sent': 'sum',
                'Meetings Held': 'sum',
                'New Leads': 'sum'
            }).reset_index()

            st.dataframe(exec_logs, use_container_width=True)

            st.divider()
            st.markdown("#### 📊 Activity Comparison across Team")
            st.bar_chart(exec_logs.set_index('Sales Exec')[['Calls Made', 'Companies Visited', 'Meetings Held', 'New Leads']])

            # Challenges & Support Feedback
            with st.expander("💬 View Daily Field Challenges & Management Support Notes"):
                st.dataframe(
                    df_logs[['Date', 'Sales Exec', 'Challenges', 'Mgmt Support', 'Remarks']], 
                    use_container_width=True
                )

    # ==========================================
    # VIEW 4: SALES EXECUTIVE LEADERBOARD
    # ==========================================
    elif menu == "🏆 Sales Executive Leaderboard":
        st.markdown("### 🏆 Executive Sales Performance Dashboard")

        exec_summary = df.groupby('Sales Exec').agg(
            Quotations=('opportunity_id', 'count'),
            Orders_Won=('Status', lambda x: (x == 'Success (Order Won)').sum()),
            Total_Quoted=('Quotation', 'sum'),
            Total_Collected=('Paid', 'sum'),
            Outstanding_Balance=('Balance', 'sum')
        ).reset_index()

        exec_summary['Conversion Rate (%)'] = (exec_summary['Orders_Won'] / exec_summary['Quotations'] * 100).round(1)
        exec_summary['Collection Rate (%)'] = (exec_summary['Total_Collected'] / exec_summary['Total_Quoted'] * 100).round(1)
        exec_summary = exec_summary.sort_values(by='Total_Quoted', ascending=False)

        st.dataframe(
            exec_summary.style.format({
                "Total_Quoted": "UGX {:,.0f}",
                "Total_Collected": "UGX {:,.0f}",
                "Outstanding_Balance": "UGX {:,.0f}",
                "Conversion Rate (%)": "{:.1f}%",
                "Collection Rate (%)": "{:.1f}%"
            }),
            use_container_width=True
        )

        st.divider()
        st.markdown("#### 💵 Revenue vs Outstanding Collections by Sales Executive")
        st.bar_chart(exec_summary.set_index('Sales Exec')[['Total_Collected', 'Outstanding_Balance']])

    # ==========================================
    # VIEW 5: SALES FUNNEL & PIPELINE
    # ==========================================
    elif menu == "📉 Sales Funnel & Pipeline":
        st.markdown("### 📉 Monthly Sales Funnel & Deal Pipeline")

        stage_summary = df.groupby('Status').agg(
            Deal_Count=('opportunity_id', 'count'),
            Total_Value=('Quotation', 'sum')
        ).reset_index()

        col_f1, col_f2 = st.columns(2)

        with col_f1:
            st.markdown("#### Deal Value by Stage")
            st.bar_chart(stage_summary.set_index('Status')['Total_Value'])

        with col_f2:
            st.markdown("#### Stage Count Distribution")
            st.dataframe(stage_summary, use_container_width=True)

        st.divider()
        st.markdown("#### ❌ Lost Deal Reason Analysis")
        lost_df = df[df['Reason for Loss'].notnull() & (df['Reason for Loss'] != 'N/A') & (df['Reason for Loss'] != '')]
        if not lost_df.empty:
            loss_counts = lost_df['Reason for Loss'].value_counts()
            st.bar_chart(loss_counts)
        else:
            st.info("No lost deal reasons recorded in system.")

    # ==========================================
    # VIEW 6: MARKET SEGMENT & PRODUCT SCOPE
    # ==========================================
    elif menu == "🏢 Market Segment & Product Scope":
        st.markdown("### 🏗️ Market Segment & Product Breakdown")

        m1, m2 = st.columns(2)

        with m1:
            st.markdown("#### Performance by Market Sector")
            sector_df = df.groupby('Project Type')['Quotation'].sum().reset_index()
            st.bar_chart(sector_df.set_index('Project Type'))

        with m2:
            st.markdown("#### Performance by Product Scope")
            product_df = df.groupby('Scope')['Quotation'].sum().reset_index()
            st.bar_chart(product_df.set_index('Scope'))