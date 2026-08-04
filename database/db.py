import sqlite3
import pandas as pd
import datetime

DB_NAME = "casements_mis.db"

def get_connection():
    """Returns a connection object to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def run_query(query, params=()):
    """Executes a SELECT query and returns a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_commit(query, params=()):
    """Executes INSERT, UPDATE, or DELETE queries and commits changes."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def seed_master_configurations():
    """Seeds the initial team roster and master dropdown options into the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Team Members & Roles
    team_members = [
        ("Sandra", "Sales Executive"),
        ("Doreen", "Sales Executive"),
        ("General Manager", "General Manager"),
        ("Anna", "General Manager")
    ]
    for name, role in team_members:
        cursor.execute("""
            INSERT INTO users (full_name, role) 
            SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM users WHERE full_name = ?)
        """, (name, role, name))

    # 2. Category Values Mapping
    settings_data = {
        "project_type": ["Residential", "Commercial", "Industrial", "Institutional"],
        "scope_of_work": [
            "Aluminium Windows & Doors", "Sliding Doors", "Curtain Walls", 
            "Toughened Glass", "Office Partitions", "Steel Fabrication", "Unipot"
        ],
        "site_status": ["Not Ready", "Site Ready", "In Progress", "Completed"],
        "measurement_status": ["Pending", "Taken", "Approved"],
        "deal_status": [
            "Prospect", "Qualified Lead", "Site Visit", 
            "Quotation Issued", "Negotiation", "Success (Order Won)", "Closed Lost"
        ],
        "reason_for_loss": [
            "N/A - Won/Active", "Quotation Expensive", 
            "Bad Reputation", "Taken by Competitor", "On Hold"
        ],
        "market_segment": [
            "Individual Clients", "Contractors", "Architects", 
            "Engineers", "Developers", "Consultants", "Institutions"
        ]
    }

    # 3. Insert configurations if they don't already exist
    for category, items in settings_data.items():
        for item in items:
            cursor.execute("""
                INSERT INTO system_settings (category, item_value)
                SELECT ?, ? WHERE NOT EXISTS (
                    SELECT 1 FROM system_settings WHERE category = ? AND item_value = ?
                )
            """, (category, item, category, item))

    conn.commit()
    conn.close()

def init_db():
    """Initializes all required database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        role TEXT NOT NULL CHECK(role IN ('Sales Executive', 'Sales Manager', 'General Manager', 'Managing Director', 'Admin')),
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Clients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        district TEXT,
        region TEXT,
        market_segment TEXT
    );
    """)

    # 3. Dynamic System Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        item_value TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    );
    """)

    # 4. Opportunities Master Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        opportunity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_code TEXT UNIQUE,
        date_entered DATE NOT NULL,
        sales_executive_id INTEGER NOT NULL,
        client_id INTEGER NOT NULL,
        project_type TEXT,
        scope_of_work TEXT NOT NULL,
        site_location TEXT,
        site_status TEXT DEFAULT 'Pending',
        measurement_status TEXT DEFAULT 'Pending',
        quotation_amount REAL DEFAULT 0.0,
        amount_paid REAL DEFAULT 0.0,
        deal_status TEXT DEFAULT 'Pipeline',
        reason_for_loss TEXT DEFAULT 'N/A - Won/Active',
        next_followup_date DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sales_executive_id) REFERENCES users(user_id),
        FOREIGN KEY (client_id) REFERENCES clients(client_id)
    );
    """)

    # 5. Daily Activity Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_activity_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date DATE NOT NULL,
        sales_executive_id INTEGER NOT NULL,
        new_companies_visited INTEGER DEFAULT 0,
        telephone_calls INTEGER DEFAULT 0,
        emails_sent INTEGER DEFAULT 0,
        meetings_held INTEGER DEFAULT 0,
        new_leads_generated INTEGER DEFAULT 0,
        daily_challenges TEXT,
        management_support_needed TEXT,
        remarks TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sales_executive_id) REFERENCES users(user_id)
    );
    """)
    # 6. Competitor Pricing Intelligence Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_intelligence (
        intel_id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor_name TEXT NOT NULL,
        product_scope TEXT NOT NULL,
        estimated_sqm_rate REAL DEFAULT 0.0,
        win_rate_impact TEXT,
        perceived_quality TEXT,
        notes TEXT,
        recorded_date DATE DEFAULT CURRENT_DATE
    );
    """)

    # 7. Customer Sentiment & Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        satisfaction_score INTEGER CHECK(satisfaction_score BETWEEN 1 AND 5),
        pricing_perception TEXT,
        quality_rating TEXT,
        feedback_comments TEXT,
        feedback_date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (client_id) REFERENCES clients(client_id)
    );
    """)
    # 8. PRO Monthly KPI Tracking Table
  
    cursor.execute("""
CREATE TABLE IF NOT EXISTS pro_kpi_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_month TEXT NOT NULL,
    pr_campaigns INTEGER DEFAULT 0,
    press_releases INTEGER DEFAULT 0,
    project_showcases INTEGER DEFAULT 0,
    testimonials_obtained INTEGER DEFAULT 0,
    brand_compliance_pct REAL DEFAULT 100.0,
    reputation_issues_resolved_pct REAL DEFAULT 100.0,
    tiktok_posts INTEGER DEFAULT 0,
    tiktok_views INTEGER DEFAULT 0,
    facebook_posts INTEGER DEFAULT 0,
    facebook_engagement INTEGER DEFAULT 0,
    instagram_posts INTEGER DEFAULT 0,
    instagram_follower_growth INTEGER DEFAULT 0,
    linkedin_posts INTEGER DEFAULT 0,
    x_posts INTEGER DEFAULT 0,
    x_impressions INTEGER DEFAULT 0,
    x_engagement_rate REAL DEFAULT 0.0,
    x_followers_growth INTEGER DEFAULT 0,
    website_updates INTEGER DEFAULT 0,
    website_visitors INTEGER DEFAULT 0,
    whatsapp_enquiries INTEGER DEFAULT 0,
    csat_rating REAL DEFAULT 95.0,
    complaints_resolved_pct REAL DEFAULT 100.0,
    recorded_date DATE DEFAULT CURRENT_DATE
);
""")

    conn.commit()
    conn.close()

    # Automatically populate master options and team roster
    seed_master_configurations()
def import_daily_activities_excel(file_path):
    """Imports daily activity entries from an uploaded Excel file."""
    df = pd.read_excel(file_path)
    
    # Clean column names by stripping trailing/leading whitespace
    df.columns = df.columns.str.strip()
    
    imported_count = 0

    for idx, row in df.iterrows():
        raw_date = row.get('Date')
        sales_person = str(row.get('Sales Person', '')).strip()

        if pd.isna(raw_date) or not sales_person or sales_person.lower() == 'nan':
            continue  # Skip header or empty rows

        # Format date safely
        try:
            log_date = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d')
        except Exception:
            log_date = datetime.date.today().strftime('%Y-%m-%d')

        # Safely parse numeric fields with defaults
        def safe_int(val):
            try:
                return int(val) if not pd.isna(val) else 0
            except (ValueError, TypeError):
                return 0

        new_companies_visited = safe_int(row.get('New Companies Visited'))
        telephone_calls = safe_int(row.get('Telephone Calls'))
        emails_sent = safe_int(row.get('Emails Sent'))
        meetings_held = safe_int(row.get('Meetings Held'))
        new_leads_generated = safe_int(row.get('New Leads Generated'))

        # Text fields
        daily_challenges = str(row.get('Daily Challenges', '')).replace('nan', '').strip()
        mgmt_support = str(row.get('Management Support Needed', '')).replace('nan', '').strip()
        remarks = str(row.get('Remarks', '')).replace('nan', '').strip()

        # 1. Get or Create User ID for the Sales Person
        user_res = run_query("SELECT user_id FROM users WHERE full_name = ?", (sales_person,))
        if user_res.empty:
            execute_commit("INSERT INTO users (full_name, role) VALUES (?, 'Sales Executive')", (sales_person,))
            user_id = int(run_query("SELECT user_id FROM users WHERE full_name = ?", (sales_person,)).iloc[0]['user_id'])
        else:
            user_id = int(user_res.iloc[0]['user_id'])

        # 2. Insert record into daily_activity_logs
        query = """
            INSERT INTO daily_activity_logs 
            (log_date, sales_executive_id, new_companies_visited, telephone_calls, 
             emails_sent, meetings_held, new_leads_generated, daily_challenges, 
             management_support_needed, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            log_date, user_id, new_companies_visited, telephone_calls,
            emails_sent, meetings_held, new_leads_generated, daily_challenges,
            mgmt_support, remarks
        )
        execute_commit(query, params)
        imported_count += 1

    return imported_count