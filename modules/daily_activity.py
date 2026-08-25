import streamlit as st
import datetime
import pandas as pd
from database.db import run_query, execute_commit

st.header("📝 Daily Activity Log Entry")

with st.expander("📤 Bulk Import Daily Activities from Excel"):
    uploaded_activity_file = st.file_uploader("Upload Daily Activity Log Excel File (.xlsx)", type=["xlsx", "xls"], key="daily_act_uploader")
    
    if uploaded_activity_file is not None:
        if st.button("🚀 Import Daily Activity Rows"):
            import tempfile
            from database.db import import_daily_activities_excel
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                tmp_file.write(uploaded_activity_file.getvalue())
                tmp_path = tmp_file.name

            with st.spinner("Processing activity records and linking sales executives..."):
                count = import_daily_activities_excel(tmp_path)
                st.success(f"🎉 Successfully imported {count} daily activity logs!")
                st.rerun()

def render_daily_activity():
    st.header("📝 Daily Activity Log Entry")
    st.caption("Track daily effort, client touchpoints, challenges, and support requirements.")

    # Fetch Sales Executives dynamically
    users_df = run_query("SELECT user_id, full_name FROM users WHERE role = 'Sales Executive' AND is_active = 1")
    user_dict = dict(zip(users_df['full_name'], users_df['user_id'])) if not users_df.empty else {}

    # --- 1. ENTRY FORM ---
    with st.form("daily_activity_form", clear_on_submit=True):
        st.subheader("Log Today's Activities")

        col1, col2, col3 = st.columns(3)

        # Column 1: Date & Sales Person
        with col1:
            log_date = st.date_input("Date", datetime.date.today())
            sales_exec = st.selectbox(
                "Sales Person", 
                options=list(user_dict.keys()) if user_dict else ["Sandra", "John Bukenya", "Doreen"]
            )
            new_companies_visited = st.number_input("New Companies Visited", min_value=0, step=1, value=0)
            telephone_calls = st.number_input("Telephone Calls", min_value=0, step=1, value=0)

        # Column 2: Digital & Physical Activity Metrics
        with col2:
            emails_sent = st.number_input("Emails Sent", min_value=0, step=1, value=0)
            meetings_held = st.number_input("Meetings Held", min_value=0, step=1, value=0)
            new_leads_generated = st.number_input("New Leads Generated", min_value=0, step=1, value=0)

        # Column 3: Qualitative Insights & Requests
        with col3:
            daily_challenges = st.text_area("Daily Challenges", placeholder="e.g. Traffic delays, client pricing pushback...")
            management_support = st.text_area("Management Support Needed", placeholder="e.g. Approval for special discount on Speke project...")
            remarks = st.text_area("Remarks", placeholder="General observations or key takeaways...")

        submitted = st.form_submit_button("💾 Submit Daily Activity Log", use_container_width=True)

        if submitted:
            # Fallback user ID lookup
            exec_id = user_dict.get(sales_exec, 1)

            query = """
                INSERT INTO daily_activity_logs 
                (log_date, sales_executive_id, new_companies_visited, telephone_calls, 
                 emails_sent, meetings_held, new_leads_generated, daily_challenges, 
                 management_support_needed, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                log_date, exec_id, new_companies_visited, telephone_calls,
                emails_sent, meetings_held, new_leads_generated, daily_challenges.strip(),
                management_support.strip(), remarks.strip()
            )
            execute_commit(query, params)
            st.success(f"✅ Daily activity log for {sales_exec} on {log_date} successfully saved!")
            st.rerun()

    # --- 2. RECENT ACTIVITY LOGS TABLE ---
    st.markdown("---")
    st.subheader("📋 Recent Daily Activity Logs")

    recent_logs = run_query("""
        SELECT 
            d.log_date AS "Date",
            u.full_name AS "Sales Person",
            d.new_companies_visited AS "New Companies Visited",
            d.telephone_calls AS "Telephone Calls",
            d.emails_sent AS "Emails Sent",
            d.meetings_held AS "Meetings Held",
            d.new_leads_generated AS "New Leads Generated",
            d.daily_challenges AS "Daily Challenges",
            d.management_support_needed AS "Management Support Needed",
            d.remarks AS "Remarks"
        FROM daily_activity_logs d
        JOIN users u ON d.sales_executive_id = u.user_id
        ORDER BY d.log_id DESC
    """)

    st.dataframe(recent_logs, use_container_width=True, hide_index=True)