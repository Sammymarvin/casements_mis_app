import os
import pandas as pd
import datetime
import psycopg2
import psycopg2.extras

# Supabase Shared Pooler Parameters
DB_HOST = "aws-1-eu-west-1.pooler.supabase.com"
DB_USER = "postgres.kmxaxdmoxpbfklhiiuqz"
DB_PASSWORD = "KU#7B6a.&McVg&P"
DB_NAME = "postgres"
DB_PORT = "5432"

def get_connection():
    """Establish and return a clean connection to the Supabase pooler for Pandas & standard operations."""
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

def run_query(query, params=None):
    """Executes a SELECT query using psycopg2 and returns a pandas DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()

def execute_commit(query, params=None):
    """Executes INSERT, UPDATE, or DELETE queries and commits changes."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def seed_master_configurations():
    """Seeds the initial team roster and master dropdown options into the database."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
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
                SELECT %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE full_name = %s)
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
                    SELECT %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM system_settings WHERE category = %s AND item_value = %s
                    )
                """, (category, item, category, item))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

def init_db():
    """Initializes all required database tables in PostgreSQL if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE,
            role VARCHAR(50) NOT NULL,
            is_active INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Clients Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id SERIAL PRIMARY KEY,
            company_name VARCHAR(150) NOT NULL,
            contact_person VARCHAR(100),
            phone VARCHAR(50),
            email VARCHAR(150),
            district VARCHAR(100),
            region VARCHAR(100),
            market_segment VARCHAR(100)
        );
        """)

        # 3. Dynamic System Settings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_id SERIAL PRIMARY KEY,
            category VARCHAR(100) NOT NULL,
            item_value VARCHAR(255) NOT NULL,
            is_active INT DEFAULT 1
        );
        """)

        # 4. Opportunities Master Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            opportunity_id SERIAL PRIMARY KEY,
            record_code VARCHAR(100) UNIQUE,
            date_entered DATE NOT NULL,
            sales_executive_id INT NOT NULL,
            client_id INT NOT NULL,
            project_type VARCHAR(100),
            scope_of_work VARCHAR(150) NOT NULL,
            site_location VARCHAR(150),
            site_status VARCHAR(50) DEFAULT 'Pending',
            measurement_status VARCHAR(50) DEFAULT 'Pending',
            quotation_amount DOUBLE PRECISION DEFAULT 0.0,
            amount_paid DOUBLE PRECISION DEFAULT 0.0,
            deal_status VARCHAR(50) DEFAULT 'Pipeline',
            reason_for_loss VARCHAR(100) DEFAULT 'N/A - Won/Active',
            next_followup_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sales_executive_id) REFERENCES users(user_id),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        );
        """)

        # 5. Daily Activity Logs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_activity_logs (
            log_id SERIAL PRIMARY KEY,
            log_date DATE NOT NULL,
            sales_executive_id INT NOT NULL,
            new_companies_visited INT DEFAULT 0,
            telephone_calls INT DEFAULT 0,
            emails_sent INT DEFAULT 0,
            meetings_held INT DEFAULT 0,
            new_leads_generated INT DEFAULT 0,
            daily_challenges TEXT,
            management_support_needed TEXT,
            remarks TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sales_executive_id) REFERENCES users(user_id),
            CONSTRAINT unique_daily_log UNIQUE (log_date, sales_executive_id)
        );
        """)

        # 6. Competitor Pricing Intelligence Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitor_intelligence (
            intel_id SERIAL PRIMARY KEY,
            competitor_name VARCHAR(150) NOT NULL,
            product_scope VARCHAR(150) NOT NULL,
            estimated_sqm_rate DOUBLE PRECISION DEFAULT 0.0,
            win_rate_impact VARCHAR(100),
            perced_quality VARCHAR(100),
            notes TEXT,
            recorded_date DATE DEFAULT CURRENT_DATE
        );
        """)

        # 7. Customer Sentiment & Feedback Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_feedback (
            feedback_id SERIAL PRIMARY KEY,
            client_id INT,
            satisfaction_score INT,
            pricing_perception VARCHAR(100),
            quality_rating VARCHAR(100),
            feedback_comments TEXT,
            feedback_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        );
        """)

        # 8. PRO Monthly KPI Tracking Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pro_kpi_logs (
            log_id SERIAL PRIMARY KEY,
            log_month VARCHAR(50) NOT NULL,
            pr_campaigns INT DEFAULT 0,
            press_releases INT DEFAULT 0,
            project_showcases INT DEFAULT 0,
            testimonials_obtained INT DEFAULT 0,
            brand_compliance_pct DOUBLE PRECISION DEFAULT 100.0,
            reputation_issues_resolved_pct DOUBLE PRECISION DEFAULT 100.0,
            tiktok_posts INT DEFAULT 0,
            tiktok_views INT DEFAULT 0,
            facebook_posts INT DEFAULT 0,
            facebook_engagement INT DEFAULT 0,
            instagram_posts INT DEFAULT 0,
            instagram_follower_growth INT DEFAULT 0,
            linkedin_posts INT DEFAULT 0,
            x_posts INT DEFAULT 0,
            x_impressions INT DEFAULT 0,
            x_engagement_rate DOUBLE PRECISION DEFAULT 0.0,
            x_followers_growth INT DEFAULT 0,
            website_updates INT DEFAULT 0,
            website_visitors INT DEFAULT 0,
            whatsapp_enquiries INT DEFAULT 0,
            csat_rating DOUBLE PRECISION DEFAULT 95.0,
            complaints_resolved_pct DOUBLE PRECISION DEFAULT 100.0,
            recorded_date DATE DEFAULT CURRENT_DATE
        );
        """)

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    # Automatically populate master options and team roster
    seed_master_configurations()

def import_daily_activities_excel(file_path):
    """Imports daily activity entries from an uploaded Excel file using PostgreSQL UPSERT logic."""
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    
    imported_count = 0
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        for idx, row in df.iterrows():
            raw_date = row.get('Date')
            sales_person = str(row.get('Sales Person', '')).strip()

            if pd.isna(raw_date) or not sales_person or sales_person.lower() == 'nan':
                continue  

            try:
                log_date = pd.to_datetime(raw_date, dayfirst=True).strftime('%Y-%m-%d')
            except Exception:
                log_date = datetime.date.today().strftime('%Y-%m-%d')

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

            daily_challenges = str(row.get('Daily Challenges', '')).replace('nan', '').strip()
            mgmt_support = str(row.get('Management Support Needed', '')).replace('nan', '').strip()
            remarks = str(row.get('Remarks', '')).replace('nan', '').strip()

            # 1. Get or Create User ID for the Sales Person
            cursor.execute("SELECT user_id FROM users WHERE LOWER(full_name) = LOWER(%s)", (sales_person,))
            user_res = cursor.fetchone()
            
            if not user_res:
                cursor.execute("INSERT INTO users (full_name, role) VALUES (%s, 'Sales Executive')", (sales_person,))
                conn.commit()
                cursor.execute("SELECT user_id FROM users WHERE LOWER(full_name) = LOWER(%s)", (sales_person,))
                user_res = cursor.fetchone()
                user_id = user_res['user_id']
            else:
                user_id = user_res['user_id']

            # 2. Insert or Update record using PostgreSQL ON CONFLICT DO UPDATE
            query = """
                INSERT INTO daily_activity_logs 
                (log_date, sales_executive_id, new_companies_visited, telephone_calls, 
                 emails_sent, meetings_held, new_leads_generated, daily_challenges, 
                 management_support_needed, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (log_date, sales_executive_id)
                DO UPDATE SET
                    new_companies_visited = EXCLUDED.new_companies_visited,
                    telephone_calls = EXCLUDED.telephone_calls,
                    emails_sent = EXCLUDED.emails_sent,
                    meetings_held = EXCLUDED.meetings_held,
                    new_leads_generated = EXCLUDED.new_leads_generated,
                    daily_challenges = EXCLUDED.daily_challenges,
                    management_support_needed = EXCLUDED.management_support_needed,
                    remarks = EXCLUDED.remarks;
            """
            params = (
                log_date, user_id, new_companies_visited, telephone_calls,
                emails_sent, meetings_held, new_leads_generated, daily_challenges,
                mgmt_support, remarks
            )
            cursor.execute(query, params)
            imported_count += 1

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return imported_count