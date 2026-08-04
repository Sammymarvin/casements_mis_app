import streamlit as st
import pandas as pd
from database.db import run_query, execute_commit

def seed_default_settings():
    """Populates default configuration values if setting table is empty."""
    check = run_query("SELECT COUNT(*) as count FROM system_settings")
    if check.iloc[0]['count'] == 0:
        defaults = [
            ("project_type", "Residential"), ("project_type", "Commercial"), 
            ("project_type", "Industrial"), ("project_type", "Institutional"),
            
            ("scope_of_work", "Aluminium Windows & Doors"), ("scope_of_work", "Sliding Doors"),
            ("scope_of_work", "Curtain Walls"), ("scope_of_work", "Toughened Glass"),
            ("scope_of_work", "Office Partitions"), ("scope_of_work", "Steel Fabrication"),
            ("scope_of_work", "Unipot"),
            
            ("site_status", "Not Ready"), ("site_status", "Site Ready"), 
            ("site_status", "In Progress"), ("site_status", "Completed"),
            
            ("measurement_status", "Pending"), ("measurement_status", "Taken"), 
            ("measurement_status", "Approved"),
            
            ("deal_status", "Prospect"), ("deal_status", "Qualified Lead"),
            ("deal_status", "Site Visit"), ("deal_status", "Quotation Issued"),
            ("deal_status", "Negotiation"), ("deal_status", "Success (Order Won)"),
            ("deal_status", "Closed Lost"),
            
            ("reason_for_loss", "N/A - Won/Active"), ("reason_for_loss", "Quotation Expensive"),
            ("reason_for_loss", "Bad Reputation"), ("reason_for_loss", "Taken by Competitor"),
            ("reason_for_loss", "On Hold"),
            
            ("market_segment", "Individual Clients"), ("market_segment", "Contractors"),
            ("market_segment", "Architects"), ("market_segment", "Engineers"),
            ("market_segment", "Developers"), ("market_segment", "Consultants"),
            ("market_segment", "Institutions")
        ]
        for category, value in defaults:
            execute_commit("INSERT INTO system_settings (category, item_value) VALUES (?, ?)", (category, value))

def render_settings():
    st.header("⚙️ Settings & Master Configuration Lists")
    seed_default_settings()

    categories = {
        "👥 Sales Executives & Team Members": "users",
        "Project Types": "project_type",
        "Products / Scope": "scope_of_work",
        "Site Status Options": "site_status",
        "Measurement Status Options": "measurement_status",
        "Deal Status Options": "deal_status",
        "Reasons for Loss": "reason_for_loss",
        "Customer Segments": "market_segment"
    }

    selected_cat_label = st.selectbox("Select Setting Category to Manage", list(categories.keys()))
    selected_cat_key = categories[selected_cat_label]

    st.divider()

    # --- 1. SPECIAL MANAGEMENT FOR SALES EXECUTIVES & USERS ---
    if selected_cat_key == "users":
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("➕ Register New Team Member")
            with st.form("add_user_form", clear_on_submit=True):
                full_name = st.text_input("Full Name", placeholder="e.g. Sandra, Doreen, or Anna")
                email = st.text_input("Email Address", placeholder="name@casements.co.ug")
                role = st.selectbox("Organizational Role", [
                    "Sales Executive", 
                    "Sales Manager", 
                    "General Manager", 
                    "Managing Director", 
                    "Admin"
                ])
                
                submitted = st.form_submit_button("💾 Save Team Member", use_container_width=True)

                if submitted:
                    if full_name.strip():
                        # Check if user already exists
                        existing = run_query("SELECT user_id FROM users WHERE full_name = ?", (full_name.strip(),))
                        if existing.empty:
                            execute_commit(
                                "INSERT INTO users (full_name, email, role) VALUES (?, ?, ?)",
                                (full_name.strip(), email.strip(), role)
                            )
                            st.success(f"✅ Added '{full_name}' as {role}!")
                            st.rerun()
                        else:
                            st.warning(f"User '{full_name}' already exists in the system.")
                    else:
                        st.error("Please enter a valid full name.")

        with col2:
            st.subheader("📋 Active Team Roster")
            users_df = run_query("""
                SELECT 
                    user_id AS 'ID',
                    full_name AS 'Full Name',
                    email AS 'Email',
                    role AS 'Role',
                    CASE WHEN is_active = 1 THEN '🟢 Active' ELSE '🔴 Inactive' END AS 'Status',
                    created_at AS 'Date Added'
                FROM users 
                ORDER BY user_id DESC
            """)
            st.dataframe(users_df, use_container_width=True, hide_index=True)

    # --- 2. MANAGEMENT FOR GENERAL DROPDOWN LISTS ---
    else:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("➕ Add New Value")
            with st.form("add_setting_form", clear_on_submit=True):
                new_item = st.text_input(f"New {selected_cat_label} Value")
                submitted = st.form_submit_button("➕ Add to System", use_container_width=True)

                if submitted:
                    if new_item.strip():
                        execute_commit(
                            "INSERT INTO system_settings (category, item_value) VALUES (?, ?)", 
                            (selected_cat_key, new_item.strip())
                        )
                        st.success(f"Added '{new_item}' to {selected_cat_label}!")
                        st.rerun()
                    else:
                        st.error("Please enter a valid value.")

        with col2:
            st.subheader(f"Current {selected_cat_label}")
            df = run_query(
                "SELECT setting_id AS 'ID', item_value AS 'Value', is_active AS 'Active Status' FROM system_settings WHERE category = ?", 
                (selected_cat_key,)
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

           