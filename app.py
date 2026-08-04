import sys
import os

# Force Python to recognize the project root directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from database.db import init_db

# Imports
from ui.theme import apply_custom_ui
from modules.dashboard import render_dashboard
from modules.analytics import render_analytics
from modules.master_entry import render_master_entry
from modules.traffic_lights import render_traffic_lights
from modules.settings import render_settings
from modules.daily_activity import render_daily_activity
from modules.operations import render_pipeline_operations
from modules.market_intel import render_market_intelligence
from modules.pro_dashboard import render_pro_dashboard

# 1. Initialize Database Tables & Seed Data
init_db()

# 2. Apply Custom Modern Executive Theme
apply_custom_ui()

# 3. Sidebar Navigation — Multi-Hub Architecture
st.sidebar.title("🏗️ Casements MIS 2026")
st.sidebar.markdown("---")

category = st.sidebar.selectbox(
    "Select Management Hub",
    [
        "1. Executive & Strategy",
        "2. Performance & Analytics",
        "3. Pipeline & Operations",
        "4. Market Intelligence",
        "5. Single-Point Data Entry"
    ]
)

# --- HUB 1: EXECUTIVE & STRATEGY ---
if category == "1. Executive & Strategy":
    menu = st.sidebar.radio(
        "View", 
        ["Executive Dashboard", "PRO Performance Dashboard", "Management Traffic Lights", "Sales Forecast Dashboard"]
    )
    
    if menu == "Executive Dashboard":
        render_dashboard()
    elif menu == "PRO Performance Dashboard":
        render_pro_dashboard()  # 👈 Added PRO Dashboard Route
    elif menu == "Management Traffic Lights":
        render_traffic_lights()
    elif menu == "Sales Forecast Dashboard":
        st.title("📈 Sales Forecast Dashboard")
        st.info("Sales pipeline projections and scenario forecasting module coming soon.")

# --- HUB 2: PERFORMANCE & ANALYTICS ---
elif category == "2. Performance & Analytics":
    render_analytics()

# --- HUB 3: PIPELINE & OPERATIONS ---
elif category == "3. Pipeline & Operations":  # 👈 Fixed variable name here!
    render_pipeline_operations()

# --- HUB 4: MARKET INTELLIGENCE ---
elif category == "4. Market Intelligence":
    render_market_intelligence()

# --- HUB 5: SINGLE-POINT DATA ENTRY ---
elif category == "5. Single-Point Data Entry":
    menu = st.sidebar.radio(
        "Entry Hub", 
        ["Master Sales Database Entry", "Daily Activity Log Entry", "Settings & Master Lists"]
    )
    
    if menu == "Master Sales Database Entry":
        render_master_entry()
    elif menu == "Daily Activity Log Entry":
        render_daily_activity()
    elif menu == "Settings & Master Lists":
        render_settings()