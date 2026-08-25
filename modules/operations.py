import streamlit as st
import pandas as pd
import datetime
from database.db import run_query, execute_commit
from ui.theme import render_header

def render_metric_card(title, value, subtitle="", status_color="#2563EB", icon="⚙️"):
    """Helper to render modern styled KPI cards."""
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


def render_pipeline_operations():
    render_header(
        title="⚙️ Pipeline & Operations Hub", 
        subtitle="Factory Production, Site Readiness & Project Execution Management"
    )

    # Sidebar Sub-Navigation
    op_menu = st.sidebar.radio(
        "Operations Navigation",
        [
            "📋 Operations Overview",
            "📐 Site Readiness & Measurements",
            "🏭 Production & Execution Pipeline",
            "🔄 Update Project Status"
        ]
    )

    # Fetch Base Project Data (PostgreSQL Compatible Double-Quote Aliases)
    query_opps = """
        SELECT 
            o.opportunity_id,
            o.record_code AS "Code",
            o.date_entered AS "Date",
            u.full_name AS "Sales Exec",
            c.company_name AS "Client",
            o.project_type AS "Project Type",
            o.scope_of_work AS "Scope",
            o.site_location AS "Location",
            o.site_status AS "Site Status",
            o.measurement_status AS "Measurement Status",
            o.quotation_amount AS "Quotation",
            o.amount_paid AS "Paid",
            o.deal_status AS "Deal Stage",
            o.next_followup_date AS "Next Follow-up"
        FROM opportunities o
        LEFT JOIN users u ON o.sales_executive_id = u.user_id
        LEFT JOIN clients c ON o.client_id = c.client_id
        ORDER BY o.opportunity_id DESC
    """
    df = run_query(query_opps)

    if df.empty:
        st.info("No active operational records found. Add entries in the Master Entry module to populate this hub.")
        return

    # Clean numerical values
    df['Quotation'] = df['Quotation'].fillna(0.0).astype(float)
    df['Paid'] = df['Paid'].fillna(0.0).astype(float)

    # Key Aggregated Operational Metrics
    total_projects = len(df)
    pending_measurements = len(df[df['Measurement Status'] == 'Pending'])
    site_ready_count = len(df[df['Site Status'] == 'Site Ready'])
    active_in_progress = len(df[df['Site Status'] == 'In Progress'])

    # ==========================================
    # VIEW 1: OPERATIONS OVERVIEW
    # ==========================================
    if op_menu == "📋 Operations Overview":
        st.markdown("### 📊 Operational Overview")
        st.caption("Live status of site readiness, measurement workflows, and project execution.")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Total Logged Projects", f"{total_projects}", "Active Work Orders", "#2563EB", "📁")
        with c2:
            render_metric_card("Pending Measurements", f"{pending_measurements}", "Requires Site Surveyor", "#D97706", "📐")
        with c3:
            render_metric_card("Sites Ready for Work", f"{site_ready_count}", "Cleared for Installation", "#059669", "🏗️")
        with c4:
            render_metric_card("In-Progress Works", f"{active_in_progress}", "Active Site/Factory Tasks", "#7C3AED", "⚡")

        st.divider()

        st.markdown("#### 📋 Operational Master Table")
        st.dataframe(
            df[['Code', 'Client', 'Scope', 'Location', 'Site Status', 'Measurement Status', 'Deal Stage', 'Next Follow-up']],
            use_container_width=True
        )

    # ==========================================
    # VIEW 2: SITE READINESS & MEASUREMENTS
    # ==========================================
    elif op_menu == "📐 Site Readiness & Measurements":
        st.markdown("### 📐 Site Readiness & Dimension Measurements")
        st.caption("Monitor site preparation, survey requests, and architectural dimension approvals.")

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown("#### Site Readiness Distribution")
            site_summary = df['Site Status'].value_counts().reset_index()
            site_summary.columns = ['Site Status', 'Count']
            st.bar_chart(site_summary.set_index('Site Status'))

        with col_m2:
            st.markdown("#### Dimension Measurement Approval")
            meas_summary = df['Measurement Status'].value_counts().reset_index()
            meas_summary.columns = ['Measurement Status', 'Count']
            st.bar_chart(meas_summary.set_index('Measurement Status'))

        st.divider()

        st.markdown("#### ⚠️ Projects Requiring Site Visits / Measurements")
        action_required = df[(df['Measurement Status'] == 'Pending') | (df['Site Status'] == 'Not Ready')]
        if not action_required.empty:
            st.dataframe(
                action_required[['Code', 'Client', 'Sales Exec', 'Scope', 'Location', 'Site Status', 'Measurement Status', 'Next Follow-up']],
                use_container_width=True
            )
        else:
            st.success("All site visits and measurements are currently up to date!")

    # ==========================================
    # VIEW 3: PRODUCTION & EXECUTION PIPELINE
    # ==========================================
    elif op_menu == "🏭 Production & Execution Pipeline":
        st.markdown("### 🏭 Factory Production & Scope Breakdown")
        st.caption("Track scope distribution across Aluminium, Toughened Glass, Steel Fabrication, and Partitions.")

        # Breakdown by Scope of Work
        scope_counts = df.groupby('Scope').agg(
            Project_Count=('opportunity_id', 'count'),
            Total_Value=('Quotation', 'sum')
        ).reset_index().sort_values(by='Project_Count', ascending=False)

        st.dataframe(
            scope_counts.style.format({"Total_Value": "UGX {:,.0f}"}),
            use_container_width=True
        )

        st.divider()

        st.markdown("#### 📊 Project Volume by Material/Scope")
        st.bar_chart(scope_counts.set_index('Scope')['Project_Count'])

    # ==========================================
    # VIEW 4: UPDATE PROJECT STATUS
    # ==========================================
    elif op_menu == "🔄 Update Project Status":
        st.markdown("### 🔄 Quick Update Operations Status")
        st.caption("Update site readiness, dimension survey progress, or site follow-up dates.")

        project_list = df['Code'] + " - " + df['Client'] + " (" + df['Scope'] + ")"
        selected_project = st.selectbox("Select Project Code to Update:", project_list)

        if selected_project:
            record_code = selected_project.split(" - ")[0]
            current_row = df[df['Code'] == record_code].iloc[0]

            with st.form("update_ops_form"):
                st.write(f"**Updating Project:** {record_code} ({current_row['Client']})")
                
                c_u1, c_u2 = st.columns(2)
                with c_u1:
                    new_site_status = st.selectbox(
                        "Site Status", 
                        ["Not Ready", "Site Ready", "In Progress", "Completed"],
                        index=["Not Ready", "Site Ready", "In Progress", "Completed"].index(current_row['Site Status']) if current_row['Site Status'] in ["Not Ready", "Site Ready", "In Progress", "Completed"] else 0
                    )
                    new_meas_status = st.selectbox(
                        "Measurement Status", 
                        ["Pending", "Taken", "Approved"],
                        index=["Pending", "Taken", "Approved"].index(current_row['Measurement Status']) if current_row['Measurement Status'] in ["Pending", "Taken", "Approved"] else 0
                    )

                with c_u2:
                    new_deal_status = st.selectbox(
                        "Deal / Execution Stage", 
                        ["Prospect", "Qualified Lead", "Site Visit", "Quotation Issued", "Negotiation", "Success (Order Won)", "Closed Lost"],
                        index=["Prospect", "Qualified Lead", "Site Visit", "Quotation Issued", "Negotiation", "Success (Order Won)", "Closed Lost"].index(current_row['Deal Stage']) if current_row['Deal Stage'] in ["Prospect", "Qualified Lead", "Site Visit", "Quotation Issued", "Negotiation", "Success (Order Won)", "Closed Lost"] else 0
                    )
                    new_followup = st.date_input("Next Site/Follow-up Date", datetime.date.today())

                submit_btn = st.form_submit_button("💾 Save Operational Status")

                if submit_btn:
                    # PostgreSQL uses %s placeholders instead of ?
                    update_sql = """
                        UPDATE opportunities
                        SET site_status = %s, measurement_status = %s, deal_status = %s, next_followup_date = %s
                        WHERE record_code = %s
                    """
                    execute_commit(update_sql, (new_site_status, new_meas_status, new_deal_status, str(new_followup), record_code))
                    st.success(f"Successfully updated status for project {record_code}!")
                    st.rerun()