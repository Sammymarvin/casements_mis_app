import streamlit as st
import datetime
import pandas as pd
from database.db import run_query, execute_commit
from ui.theme import render_header

def get_setting_options(category_key):
    """Utility to fetch active options from system_settings."""
    df = run_query("SELECT item_value FROM system_settings WHERE category = ? AND is_active = 1", (category_key,))
    return df['item_value'].tolist() if not df.empty else ["N/A"]

def render_master_entry():
    render_header(
        title="🏢 Master Sales Transactional Database", 
        subtitle="Manage sales pipelines, customer quotations, site statuses, and financial collections."
    )
    
    # Dynamic Navigation Tabs
    tab_overview, tab_new, tab_update = st.tabs([
        "📊 Pipeline Analytics", 
        "➕ Create Opportunity", 
        "🔄 View & Update Records"
    ])
    
    # Load Database Master Lists
    sales_execs_df = run_query("SELECT user_id, full_name FROM users WHERE role = 'Sales Executive' AND is_active = 1")
    sales_execs = sales_execs_df['full_name'].tolist() if not sales_execs_df.empty else ["Sandra", "Anna", "Doreen"]

    project_types = get_setting_options("project_type")
    products_scope = get_setting_options("scope_of_work")
    site_statuses = get_setting_options("site_status")
    measurement_statuses = get_setting_options("measurement_status")
    deal_statuses = get_setting_options("deal_status")
    reasons_for_loss = get_setting_options("reason_for_loss")

    # Raw Query for Opportunities (Includes Client Phone Number)
    query_all = """
        SELECT 
            o.opportunity_id,
            o.record_code AS [Code],
            o.date_entered AS [Date],
            u.full_name AS [Sales Exec],
            c.company_name AS [Client Name],
            c.phone AS [Contact Number],
            o.project_type AS [Project],
            o.scope_of_work AS [Scope],
            o.site_location AS [Location],
            o.site_status AS [Site Status],
            o.measurement_status AS [Meas. Status],
            o.quotation_amount AS [Quotation (UGX)],
            o.amount_paid AS [Paid (UGX)],
            (o.quotation_amount - o.amount_paid) AS [Balance (UGX)],
            o.deal_status AS [Deal Status],
            o.reason_for_loss AS [Reason for Loss],
            o.next_followup_date AS [Next Follow-Up]
        FROM opportunities o
        LEFT JOIN users u ON o.sales_executive_id = u.user_id
        LEFT JOIN clients c ON o.client_id = c.client_id
        ORDER BY o.date_entered DESC, o.opportunity_id DESC
    """
    df_opps = run_query(query_all)

    # ==========================================
    # TAB 1: EXECUTIVE KPI OVERVIEW
    # ==========================================
    with tab_overview:
        if df_opps.empty:
            st.info("No sales records available to generate pipeline metrics.")
        else:
            total_quoted = df_opps['Quotation (UGX)'].sum()
            total_collected = df_opps['Paid (UGX)'].sum()
            total_balance = df_opps['Balance (UGX)'].sum()
            total_deals = len(df_opps)
            won_deals = len(df_opps[df_opps['Deal Status'] == 'Success (Order Won)'])

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            with kpi1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Quotations</div>
                    <div class="metric-value">UGX {total_quoted:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with kpi2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Collections Received</div>
                    <div class="metric-value" style="color:#059669;">UGX {total_collected:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Outstanding Balance</div>
                    <div class="metric-value" style="color:#DC2626;">UGX {total_balance:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)

            with kpi4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Deals Closed (Won)</div>
                    <div class="metric-value" style="color:#2563EB;">{won_deals} / {total_deals}</div>
                </div>
                """, unsafe_allow_html=True)

            st.write(" ")
            st.write(" ")
            
            # Export Options for Dashboard Summary
            col_t1, col_t2 = st.columns([3, 1])
            with col_t1:
                st.subheader("📌 Recent Opportunities")
            with col_t2:
                csv_data = df_opps.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Full List (CSV)",
                    data=csv_data,
                    file_name=f"casements_sales_pipeline_{datetime.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.dataframe(
                df_opps.head(10).style.format({
                    "Quotation (UGX)": "{:,.0f}",
                    "Paid (UGX)": "{:,.0f}",
                    "Balance (UGX)": "{:,.0f}"
                }),
                use_container_width=True,
                height=300
            )

    # ==========================================
    # TAB 2: CREATE OPPORTUNITY FORM
    # ==========================================
    with tab_new:
        with st.form("new_opportunity_form", clear_on_submit=True):
            st.markdown("### 📝 Enter Opportunity Details")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                record_code = st.text_input("Record Code", value=f"CAL-2026-{datetime.datetime.now().strftime('%M%S')}")
                date_entered = st.date_input("Date Entered", datetime.date.today())
                sales_exec = st.selectbox("Sales Person / Executive", options=sales_execs)
                client_name = st.text_input("Client / Company Name", placeholder="e.g. Speke Apartments Ltd")
                contact_number = st.text_input("Contact Number", placeholder="e.g. +256 700 000000")
                project_type = st.selectbox("Project Type", options=project_types)

            with col2:
                scope_of_work = st.selectbox("Scope of Work / Product", options=products_scope)
                site_location = st.text_input("Site Location", "Kampala")
                site_status = st.selectbox("Site Status", options=site_statuses)
                measurement_status = st.selectbox("Measurement Status", options=measurement_statuses)
                deal_status = st.selectbox("Deal Status", options=deal_statuses)
                reason_for_loss = st.selectbox("Reason for Loss", options=reasons_for_loss)

            with col3:
                quotation_amount = st.number_input("Quotation Amount (UGX)", min_value=0.0, step=500000.0)
                amount_paid = st.number_input("Amount Paid / Deposit (UGX)", min_value=0.0, step=100000.0)
                balance = quotation_amount - amount_paid
                st.metric("Outstanding Balance (UGX)", f"UGX {balance:,.0f}")
                next_followup = st.date_input("Next Follow-Up Date", datetime.date.today() + datetime.timedelta(days=7))

            submitted = st.form_submit_button("💾 Save Opportunity to Database", type="primary", use_container_width=True)
            
            if submitted:
                if not client_name.strip():
                    st.error("Please enter a Client / Company Name before saving.")
                else:
                    # Get or Create Client
                    existing_client = run_query("SELECT client_id FROM clients WHERE company_name = ?", (client_name.strip(),))
                    if existing_client.empty:
                        execute_commit("INSERT INTO clients (company_name, phone) VALUES (?, ?)", (client_name.strip(), contact_number.strip()))
                        client_id = int(run_query("SELECT client_id FROM clients WHERE company_name = ?", (client_name.strip(),)).iloc[0]['client_id'])
                    else:
                        client_id = int(existing_client.iloc[0]['client_id'])
                        # Update phone if it was updated
                        if contact_number.strip():
                            execute_commit("UPDATE clients SET phone = ? WHERE client_id = ?", (contact_number.strip(), client_id))
                    
                    # Get Exec ID
                    user_res = run_query("SELECT user_id FROM users WHERE full_name = ?", (sales_exec,))
                    exec_id = int(user_res.iloc[0]['user_id']) if not user_res.empty else 1

                    # Save Opportunity
                    query_opp = """
                        INSERT INTO opportunities 
                        (record_code, date_entered, sales_executive_id, client_id, project_type, 
                         scope_of_work, site_location, site_status, measurement_status, 
                         quotation_amount, amount_paid, deal_status, reason_for_loss, next_followup_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    execute_commit(query_opp, (
                        record_code, date_entered, exec_id, client_id, project_type,
                        scope_of_work, site_location, site_status, measurement_status,
                        quotation_amount, amount_paid, deal_status, reason_for_loss, next_followup
                    ))

                    st.success(f"✅ Opportunity '{record_code}' successfully saved!")
                    st.rerun()

    # ==========================================
    # TAB 3: VIEW, FILTER, EXPORT & UPDATE RECORDS
    # ==========================================
    with tab_update:
        if df_opps.empty:
            st.info("No records to display.")
        else:
            col_f1, col_f2, col_f3 = st.columns([2, 2, 1.5])
            with col_f1:
                search_term = st.text_input("🔍 Search Client Name, Contact or Code", "").strip().lower()
            with col_f2:
                status_filter = st.selectbox("Filter by Deal Status", ["All"] + deal_statuses)
            with col_f3:
                st.write("") # Padding spacing
                st.write("") 
                filtered_csv = df_opps.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download List",
                    data=filtered_csv,
                    file_name=f"sales_records_{datetime.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            filtered_df = df_opps.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Client Name'].astype(str).str.lower().str.contains(search_term, na=False) | 
                    filtered_df['Code'].astype(str).str.lower().str.contains(search_term, na=False) |
                    filtered_df['Contact Number'].astype(str).str.lower().str.contains(search_term, na=False)
                ]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['Deal Status'] == status_filter]

            st.dataframe(
                filtered_df.style.format({
                    "Quotation (UGX)": "{:,.0f}",
                    "Paid (UGX)": "{:,.0f}",
                    "Balance (UGX)": "{:,.0f}"
                }),
                use_container_width=True,
                height=280
            )

            st.divider()

            # Record Update Tool
            st.markdown("### 🔄 Comprehensive Record & Status Modifier")
            record_options = {
                f"{row['Code']} | {row['Client Name']} ({row['Contact Number']})": row['opportunity_id']
                for _, row in filtered_df.iterrows()
            }
            
            if record_options:
                selected_label = st.selectbox("Select Record to Modify", list(record_options.keys()))
                selected_id = record_options[selected_label]
                current_rec = filtered_df[filtered_df['opportunity_id'] == selected_id].iloc[0]

                # Fetch Client ID and details for updating client contact info
                client_id_res = run_query("SELECT client_id FROM opportunities WHERE opportunity_id = ?", (selected_id,))
                current_client_id = int(client_id_res.iloc[0]['client_id']) if not client_id_res.empty else None

                with st.form("update_opportunity_form"):
                    ucol1, ucol2, ucol3 = st.columns(3)

                    with ucol1:
                        upd_client_name = st.text_input("Client / Company Name", value=str(current_rec['Client Name']))
                        upd_contact_num = st.text_input("Contact Number", value=str(current_rec['Contact Number'] or ''))
                        
                        upd_sales_exec = st.selectbox(
                            "Assigned Sales Executive",
                            options=sales_execs,
                            index=sales_execs.index(current_rec['Sales Exec']) if current_rec['Sales Exec'] in sales_execs else 0
                        )
                        
                        upd_deal_status = st.selectbox(
                            "Deal Status", 
                            options=deal_statuses, 
                            index=deal_statuses.index(current_rec['Deal Status']) if current_rec['Deal Status'] in deal_statuses else 0
                        )
                        upd_reason_loss = st.selectbox(
                            "Reason for Loss", 
                            options=reasons_for_loss,
                            index=reasons_for_loss.index(current_rec['Reason for Loss']) if current_rec['Reason for Loss'] in reasons_for_loss else 0
                        )

                    with ucol2:
                        upd_scope = st.selectbox(
                            "Scope of Work", 
                            options=products_scope,
                            index=products_scope.index(current_rec['Scope']) if current_rec['Scope'] in products_scope else 0
                        )
                        upd_location = st.text_input("Site Location", value=str(current_rec['Location'] or ''))
                        
                        upd_site_status = st.selectbox(
                            "Site Status", 
                            options=site_statuses,
                            index=site_statuses.index(current_rec['Site Status']) if current_rec['Site Status'] in site_statuses else 0
                        )
                        upd_meas_status = st.selectbox(
                            "Measurement Status", 
                            options=measurement_statuses,
                            index=measurement_statuses.index(current_rec['Meas. Status']) if current_rec['Meas. Status'] in measurement_statuses else 0
                        )

                    with ucol3:
                        upd_quotation_amt = st.number_input(
                            "Quotation Amount (UGX)", 
                            min_value=0.0, 
                            value=float(current_rec['Quotation (UGX)']), 
                            step=500000.0
                        )
                        upd_amount_paid = st.number_input(
                            "Amount Paid / Deposit (UGX)", 
                            min_value=0.0, 
                            value=float(current_rec['Paid (UGX)']), 
                            step=100000.0
                        )
                        upd_balance = upd_quotation_amt - upd_amount_paid
                        st.metric("Updated Outstanding Balance", f"UGX {upd_balance:,.0f}")
                        
                        # Handle Date parsing for follow-up date
                        try:
                            parsed_date = datetime.datetime.strptime(str(current_rec['Next Follow-Up']), "%Y-%m-%d").date()
                        except ValueError:
                            parsed_date = datetime.date.today()

                        upd_followup = st.date_input("Next Follow-Up Date", value=parsed_date)

                    update_submitted = st.form_submit_button("🚀 Post & Commit All Updates", type="primary", use_container_width=True)

                    if update_submitted:
                        # 1. Update Client Table Data
                        if current_client_id:
                            execute_commit(
                                "UPDATE clients SET company_name = ?, phone = ? WHERE client_id = ?",
                                (upd_client_name.strip(), upd_contact_num.strip(), current_client_id)
                            )

                        # 2. Map Sales Exec ID
                        exec_user_res = run_query("SELECT user_id FROM users WHERE full_name = ?", (upd_sales_exec,))
                        upd_exec_id = int(exec_user_res.iloc[0]['user_id']) if not exec_user_res.empty else 1

                        # 3. Post Updates to Opportunities Table
                        execute_commit("""
                            UPDATE opportunities
                            SET sales_executive_id = ?, scope_of_work = ?, site_location = ?,
                                deal_status = ?, reason_for_loss = ?, site_status = ?, 
                                measurement_status = ?, quotation_amount = ?, amount_paid = ?, 
                                next_followup_date = ?
                            WHERE opportunity_id = ?
                        """, (
                            upd_exec_id, upd_scope, upd_location,
                            upd_deal_status, upd_reason_loss, upd_site_status, 
                            upd_meas_status, upd_quotation_amt, upd_amount_paid, 
                            upd_followup, selected_id
                        ))
                        
                        st.success(f"🎉 Opportunity '{current_rec['Code']}' updated and posted successfully!")
                        st.rerun()