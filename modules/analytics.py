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

    # ----------------------------------------------------
    # MONTH FILTER CONTROL (PostgreSQL Compatible)
    # ----------------------------------------------------
    months_query = """
        SELECT DISTINCT TO_CHAR(date_entered, 'YYYY-MM') as month_val 
        FROM opportunities 
        WHERE date_entered IS NOT NULL
        ORDER BY month_val DESC;
    """
    df_months = run_query(months_query)
    available_months = df_months["month_val"].dropna().tolist() if not df_months.empty else []
    month_options = ["All Time"] + available_months
    
    col_filter, col_empty = st.columns([1, 2])
    with col_filter:
        selected_month = st.selectbox("📅 Filter Performance by Month", month_options, index=0)

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

    # SQL WHERE Clause for Opportunities
    where_opps = ""
    params_opps = []
    if selected_month != "All Time":
        where_opps = "WHERE TO_CHAR(o.date_entered, 'YYYY-MM') = %s"
        params_opps = [selected_month]

    # Query Base Opportunities Data (Quoted PostgreSQL Column Names)
    query_opps = f"""
        SELECT 
            o.opportunity_id,
            o.record_code AS "Code",
            o.date_entered AS "Date",
            u.full_name AS "Sales_Exec",
            c.company_name AS "Client",
            o.project_type AS "Project_Type",
            o.scope_of_work AS "Scope",
            o.quotation_amount AS "Quotation",
            o.amount_paid AS "Paid",
            (o.quotation_amount - o.amount_paid) AS "Balance",
            o.deal_status AS "Status",
            o.reason_for_loss AS "Reason_for_Loss"
        FROM opportunities o
        LEFT JOIN users u ON o.sales_executive_id = u.user_id
        LEFT JOIN clients c ON o.client_id = c.client_id
        {where_opps}
    """
    df = run_query(query_opps, params_opps) if params_opps else run_query(query_opps)

    if df.empty:
        st.info(f"No sales records available for '{selected_month}'.")
        return

    # Fail-safe: Map capitalized keys cleanly regardless of driver case-folding
    column_mapping = {col.lower(): col for col in df.columns}
    
    def get_col(name):
        return df[column_mapping.get(name.lower(), name)]

    # Clean numerical values
    quotation_col = column_mapping.get('quotation', 'Quotation')
    paid_col = column_mapping.get('paid', 'Paid')
    balance_col = column_mapping.get('balance', 'Balance')
    status_col = column_mapping.get('status', 'Status')
    sales_exec_col = column_mapping.get('sales_exec', 'Sales_Exec')
    reason_col = column_mapping.get('reason_for_loss', 'Reason_for_Loss')
    project_type_col = column_mapping.get('project_type', 'Project_Type')
    scope_col = column_mapping.get('scope', 'Scope')

    df[quotation_col] = df[quotation_col].fillna(0.0).astype(float)
    df[paid_col] = df[paid_col].fillna(0.0).astype(float)
    df[balance_col] = df[balance_col].fillna(0.0).astype(float)

    # Key Aggregated Metrics
    total_pipeline_val = df[quotation_col].sum()
    total_revenue_collected = df[paid_col].sum()
    total_quotations_issued = len(df)
    orders_won = len(df[df[status_col] == 'Success (Order Won)'])
    conversion_rate = (orders_won / total_quotations_issued * 100) if total_quotations_issued > 0 else 0.0
    collection_rate = (total_revenue_collected / total_pipeline_val * 100) if total_pipeline_val > 0 else 0.0

    # ==========================================
    # VIEW 1: EXECUTIVE TRAFFIC LIGHT PANEL
    # ==========================================
    if menu == "🚦 Executive Traffic Light Panel":
        st.markdown(f"### 🚥 Management Traffic Light Report ({selected_month})")
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
        st.markdown(f"### 🎯 Departmental KPI Scorecard ({selected_month})")
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
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.markdown("### 📅 Monthly Sales Revenue Goal Progress")
        st.progress(min(float(total_revenue_collected / 1000000000.0), 1.0))

    # ==========================================
    # VIEW 3: DAILY SALES ACTIVITY DASHBOARD
    # ==========================================
    elif menu == "📆 Daily Sales Activity Dashboard":
        st.markdown(f"### 📆 Individual & Team Daily Sales Activity Dashboard ({selected_month})")
        st.caption("Tracking field execution, telephone calls, meetings, and lead generation.")

        where_logs = ""
        params_logs = []
        if selected_month != "All Time":
            where_logs = "WHERE TO_CHAR(dal.log_date, 'YYYY-MM') = %s"
            params_logs = [selected_month]

        query_logs = f"""
            SELECT 
                dal.log_date AS "Date",
                u.full_name AS "Sales_Exec",
                dal.new_companies_visited AS "Companies_Visited",
                dal.telephone_calls AS "Calls_Made",
                dal.emails_sent AS "Emails_Sent",
                dal.meetings_held AS "Meetings_Held",
                dal.new_leads_generated AS "New_Leads",
                dal.daily_challenges AS "Challenges",
                dal.management_support_needed AS "Mgmt_Support",
                dal.remarks AS "Remarks"
            FROM daily_activity_logs dal
            LEFT JOIN users u ON dal.sales_executive_id = u.user_id
            {where_logs}
            ORDER BY dal.log_date DESC
        """
        try:
            df_logs = run_query(query_logs, params_logs) if params_logs else run_query(query_logs)
        except Exception:
            df_logs = pd.DataFrame()

        if df_logs.empty:
            st.info(f"No daily activity log records found for '{selected_month}'.")
        else:
            log_cols = {c.lower(): c for c in df_logs.columns}
            c_visited = log_cols.get('companies_visited', 'Companies_Visited')
            c_calls = log_cols.get('calls_made', 'Calls_Made')
            c_emails = log_cols.get('emails_sent', 'Emails_Sent')
            c_meetings = log_cols.get('meetings_held', 'Meetings_Held')
            c_leads = log_cols.get('new_leads', 'New_Leads')
            c_exec = log_cols.get('sales_exec', 'Sales_Exec')

            c_a, c_b, c_c, c_d = st.columns(4)
            with c_a:
                render_metric_card("Telephone Calls", f"{df_logs[c_calls].sum():,.0f}", "Target: 20 / Exec / Day", "#2563EB", "📞")
            with c_b:
                render_metric_card("Companies Visited", f"{df_logs[c_visited].sum():,.0f}", "Target: 5 / Exec / Day", "#059669", "🏢")
            with c_c:
                render_metric_card("Meetings Held", f"{df_logs[c_meetings].sum():,.0f}", "Target: 3 / Exec / Day", "#7C3AED", "🤝")
            with c_d:
                render_metric_card("New Leads", f"{df_logs[c_leads].sum():,.0f}", "Target: 5 / Exec / Day", "#D97706", "⚡")

            st.divider()

            st.markdown("#### 👤 Daily Activity Totals by Sales Executive")
            exec_logs = df_logs.groupby(c_exec).agg({
                c_visited: 'sum',
                c_calls: 'sum',
                c_emails: 'sum',
                c_meetings: 'sum',
                c_leads: 'sum'
            }).reset_index()

            st.dataframe(exec_logs, use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("#### 📊 Activity Comparison across Team")
            st.bar_chart(exec_logs.set_index(c_exec)[[c_calls, c_visited, c_meetings, c_leads]])

            with st.expander("💬 View Daily Field Challenges & Management Support Notes"):
                st.dataframe(
                    df_logs, 
                    use_container_width=True,
                    hide_index=True
                )

    # ==========================================
    # VIEW 4: SALES EXECUTIVE LEADERBOARD
    # ==========================================
    elif menu == "🏆 Sales Executive Leaderboard":
        st.markdown(f"### 🏆 Executive Sales Performance Dashboard ({selected_month})")

        exec_summary = df.groupby(sales_exec_col).agg(
            Quotations=(column_mapping.get('opportunity_id', 'opportunity_id'), 'count'),
            Orders_Won=(status_col, lambda x: (x == 'Success (Order Won)').sum()),
            Total_Quoted=(quotation_col, 'sum'),
            Total_Collected=(paid_col, 'sum'),
            Outstanding_Balance=(balance_col, 'sum')
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
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.markdown("#### 💵 Revenue vs Outstanding Collections by Sales Executive")
        st.bar_chart(exec_summary.set_index(sales_exec_col)[['Total_Collected', 'Outstanding_Balance']])

    # ==========================================
    # VIEW 5: SALES FUNNEL & PIPELINE
    # ==========================================
    elif menu == "📉 Sales Funnel & Pipeline":
        st.markdown(f"### 📉 Monthly Sales Funnel & Deal Pipeline ({selected_month})")

        stage_summary = df.groupby(status_col).agg(
            Deal_Count=(column_mapping.get('opportunity_id', 'opportunity_id'), 'count'),
            Total_Value=(quotation_col, 'sum')
        ).reset_index()

        col_f1, col_f2 = st.columns(2)

        with col_f1:
            st.markdown("#### Deal Value by Stage")
            st.bar_chart(stage_summary.set_index(status_col)['Total_Value'])

        with col_f2:
            st.markdown("#### Stage Count Distribution")
            st.dataframe(stage_summary, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### ❌ Lost Deal Reason Analysis")
        lost_df = df[df[reason_col].notnull() & (df[reason_col] != 'N/A') & (df[reason_col] != '')]
        if not lost_df.empty:
            loss_counts = lost_df[reason_col].value_counts()
            st.bar_chart(loss_counts)
        else:
            st.info("No lost deal reasons recorded for this selection.")

    # ==========================================
    # VIEW 6: MARKET SEGMENT & PRODUCT SCOPE
    # ==========================================
    elif menu == "🏢 Market Segment & Product Scope":
        st.markdown(f"### 🏗️ Market Segment & Product Breakdown ({selected_month})")

        m1, m2 = st.columns(2)

        with m1:
            st.markdown("#### Performance by Market Sector")
            sector_df = df.groupby(project_type_col)[quotation_col].sum().reset_index()
            st.bar_chart(sector_df.set_index(project_type_col))

        with m2:
            st.markdown("#### Performance by Product Scope")
            product_df = df.groupby(scope_col)[quotation_col].sum().reset_index()
            st.bar_chart(product_df.set_index(scope_col))