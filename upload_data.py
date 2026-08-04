import sqlite3
import pandas as pd
import datetime
from datetime import datetime as dt
import os

DB_NAME = "casements_mis.db"

def get_connection():
    """Returns a connection object to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def seed_master_configurations():
    """Seeds the initial team roster and master dropdown options into the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Team Members & Roles
    team_members = [
        ("Sandra", "Sales Executive"),
        ("Doreen", "Sales Executive"),
        ("General Manager", "Sales Executive"),
        ("Anna", "Sales Executive")
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

    # Seed team roster and settings
    seed_master_configurations()

def parse_date(date_str):
    if not date_str or str(date_str).strip() == "":
        return None
    date_str = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return dt.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None

def clean_num(val):
    if not val:
        return 0
    val_str = str(val).lower().replace("ugx", "").replace("usd", "").replace(",", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return 0

def upload_raw_dataset():
    raw_records = [
        ("7/21/2026", "Sandra", "Mirondo Fred", "750142995", "Institutional", "Office Partitions", "JINJA", "Not Ready", "Pending", "58546260", "58546260", "0", "Success (Order Won)", "N/A - Won/Active", "2026-08-08"),
        ("7/22/2026", "Sandra", "Zephyr Balunywa", "256776610176", "Commercial", "Aluminium Windows & Doors", "BUSEMBATIA", "", "Taken", "2550000", "0", "2550000", "Prospect", "", ""),
        ("7/23/2026", "Sandra", "Arch Forum", "256776690915", "Commercial", "Aluminium Windows & Doors", "NTINDA", "", "", "141000000", "0", "141000000", "Prospect", "", ""),
        ("7/24/2026", "Sandra", "Arch Forum", "256776690915", "Commercial", "Aluminium Windows & Doors", "NTINDA", "", "", "311437363", "0", "311437363", "Prospect", "", ""),
        ("7/25/2026", "Sandra", "Madam Yudaya", "256772650938", "Residential", "Aluminium Windows & Doors", "KIRA-NSASA", "", "", "132032328", "0", "132032328", "Prospect", "", ""),
        ("7/26/2026", "Sandra", "Andrew Amara", "256752282505", "Commercial", "Aluminium Windows & Doors", "LUWEERO", "", "", "42909976", "0", "42909976", "Prospect", "", ""),
        ("7/27/2026", "Sandra", "Dr. Ndawula David", "256772409023", "Residential", "Steel Fabrication", "GAYAZA", "", "", "4511351", "0", "4511351", "Prospect", "", ""),
        ("7/28/2026", "Sandra", "Mr. Edgar", "256706078772", "Residential", "Aluminium Windows & Doors", "NAGURU", "", "", "8500000", "0", "8500000", "Prospect", "", ""),
        ("7/29/2026", "Sandra", "Mr. Esami", "256702720808", "Commercial", "Toughened Glass", "WANDEGAYA", "", "", "2585000", "0", "2585000", "Prospect", "", ""),
        ("7/30/2026", "Sandra", "Opus Design", "256706690312", "Industrial", "Steel Fabrication", "BULENGA", "", "", "21586600", "0", "21586600", "Prospect", "", ""),
        ("7/31/2026", "Sandra", "Mr. Oguttu Wilber", "256784261089", "Residential", "Aluminium Windows & Doors", "BUSIA", "", "", "130000000", "0", "130000000", "Prospect", "", ""),
        ("8/1/2026", "Sandra", "Ibero Coffee", "27836673818", "Industrial", "Aluminium Windows & Doors", "NAMANVE", "Not Ready", "", "135947576", "0", "135947576", "Prospect", "", ""),
        ("8/2/2026", "Sandra", "Ibero Coffee", "27836673818", "Industrial", "Aluminium Windows & Doors", "NAMANVE", "Not Ready", "", "166095651", "0", "166095651", "Prospect", "", ""),
        ("8/3/2026", "Sandra", "Ibero Coffee", "27836673818", "Industrial", "Curtain Walls", "NAMANVE", "Not Ready", "", "556393600", "0", "556393600", "Prospect", "", ""),
        ("8/4/2026", "Sandra", "Ibero Coffee", "27836673818", "Industrial", "Aluminium Windows & Doors", "NAMANVE", "Not Ready", "", "55518467", "0", "55518467", "Prospect", "", ""),
        ("8/5/2026", "Sandra", "Ibero Coffee", "27836673818", "Industrial", "Steel Fabrication", "NAMANVE", "Not Ready", "", "46020000", "0", "46020000", "Prospect", "", ""),
        ("8/6/2026", "Sandra", "Ibero Coffee", "27836673818", "Industrial", "Steel Fabrication", "NAMANVE", "Not Ready", "", "44657808", "0", "44657808", "Prospect", "", ""),
        ("20/7/2026", "Anna", "Mr.Mugisha Amujjade", "256787476267", "Residential", "Aluminium Windows & Doors", "KISOZI", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("20/7/2026", "Anna", "Madam Mutoni", "256786791714", "Residential", "Aluminium Windows & Doors", "Wakiso", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("21/7/2026", "Anna", "Mr.frank", "256749795811", "Commercial", "Aluminium Windows & Doors", "MBARARA", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("21/7/2026", "Anna", "Mr.Smith", "2567750000875", "Residential", "Aluminium Windows & Doors", "WAKISO", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("22/7/2026", "Anna", "Madam winnie", "256771915697", "Residential", "Aluminium Windows & Doors", "WAKISO", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("23/7/2026", "Anna", "Mr joel", "256705713353", "Residential", "Steel Fabrication", "WAKISO", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("23/7/2026", "Anna", "QUISA Constructions", "256751458275", "Residential", "Aluminium Windows & Doors", "MBARARA", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("23/7/2026", "Anna", "Mr.Erisa", "256752888424", "Residential", "Aluminium Windows & Doors", "MBARARA", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("23/7/2026", "Anna", "Mr.ODOI", "256782612306", "Residential", "Aluminium Windows & Doors", "JINJA", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("23/7/2026", "Anna", "Mr.Edward", "256772381212", "Residential", "Aluminium Windows & Doors", "NASANA", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("23/7/2026", "Anna", "Mr.Caleb", "2567778880985", "Residential", "Aluminium Windows & Doors", "JINJA", "Not Ready", "", "0", "0", "0", "Prospect", "", ""),
        ("29/7/2026", "Doreen", "SBC UGANDA", "", "Industrial", "STAINLESS MIRROR", "AIRPORT", "Site Ready", "Taken", "19488585", "11561025", "7927560", "Success (Order Won)", "N/A - Won/Active", ""),
        ("29/7/2026", "Doreen", "PONNI SAFARI CAMPS", "", "Institutional", "Unipot", "KARAMOJA", "In Progress", "Taken", "18354000", "18354000", "0", "Success (Order Won)", "N/A - Won/Active", ""),
        ("29/7/2026", "Doreen", "VIROGO", "", "Residential", "Aluminium Windows & Doors", "MITYANA", "Site Ready", "Taken", "3160891", "3160891", "0", "Success (Order Won)", "N/A - Won/Active", ""),
        ("29/7/2026", "Doreen", "3D SERVICE", "", "Residential", "Sliding Doors", "BUNGA", "Site Ready", "Taken", "12140999", "9800000", "2340999", "Success (Order Won)", "N/A - Won/Active", ""),
        ("29/7/2026", "Doreen", "ASILI AGRICULTURAL", "766101562", "Institutional", "UNIPORTS", "In Progress", "Taken", "31813600", "0", "31813600", "Prospect", "", "29/7/2027"),
        ("29/7/2026", "Doreen", "MR ISA", "702436427", "Residential", "Aluminium Windows & Doors", "NAKIGALALA", "Site Ready", "Taken", "22925374", "0", "22925374", "Prospect", "", ""),
        ("29/7/2026", "Doreen", "MR DAVID", "704731766", "Residential", "Steel Fabrication", "KAJJANSI", "In Progress", "Taken", "5520000", "0", "5520000", "Quotation Issued", "", ""),
        ("28/7/2026", "Doreen", "MY KAYUMBA", "", "Residential", "Steel Fabrication", "KIGALI", "In Progress", "Taken", "7363200", "0", "7363200", "Quotation Issued", "", ""),
        ("23/7/2026", "Doreen", "MR CHARLES", "782517278", "Residential", "Aluminium Windows & Doors", "LUZIRA", "In Progress", "Taken", "20494430", "0", "20494430", "Prospect", "", ""),
        ("24/7/2026", "Doreen", "MS CAROLYNE", "772313112", "Residential", "Aluminium Windows & Doors", "MUTUNDWE", "Not Ready", "Taken", "44041723", "0", "44041723", "Quotation Issued", "", ""),
        ("2026-08-03", "Doreen", "ssimbwa", "757135031", "Residential", "Steel Fabrication", "kakiri", "Not Ready", "Taken", "9230845", "0", "9230845", "Quotation Issued", "", ""),
        ("2026-08-03", "Doreen", "SARJAN", "700612924", "Commercial", "Aluminium Windows & Doors", "KOLOLO", "In Progress", "Pending", "124700000", "0", "124700000", "Quotation Issued", "", ""),
        ("2026-08-01", "Doreen", "EXCEL CONSTRUCTION", "emma@excelconstruction.org", "Commercial", "Aluminium Windows & Doors", "KOLOLO", "In Progress", "Pending", "2980582289", "0", "2980582289", "Quotation Issued", "", ""),
        ("2026-08-03", "Doreen", "L.A LIVING SPACE", "", "Residential", "Aluminium Windows & Doors", "KUNGU", "Site Ready", "Approved", "83000000", "35000000", "48000000", "Success (Order Won)", "N/A - Won/Active", ""),
        ("2026-08-01", "Doreen", "BRENDAH", "772477200", "Residential", "SHOWER CABINS", "KIGO", "Site Ready", "Taken", "15847400", "0", "15847400", "Quotation Issued", "", "")
    ]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Clear existing opportunities to avoid duplication on re-run
    cursor.execute("DELETE FROM opportunities;")

    inserted_count = 0
    for idx, rec in enumerate(raw_records, start=1):
        rec_list = list(rec) + [""] * (15 - len(rec))
        d_entered, sales_person, client_name, contact, proj_type, scope, location, site_stat, meas_stat, q_amt, paid_amt, out_bal, deal_stat, loss_reason, followup_date = rec_list[:15]

        cursor.execute("SELECT user_id FROM users WHERE full_name = ?", (sales_person,))
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute("INSERT INTO users (full_name, role) VALUES (?, 'Sales Executive')", (sales_person,))
            sales_id = cursor.lastrowid
        else:
            sales_id = user_row[0]

        cursor.execute("SELECT client_id FROM clients WHERE company_name = ?", (client_name,))
        client_row = cursor.fetchone()
        if not client_row:
            cursor.execute("INSERT INTO clients (company_name, phone) VALUES (?, ?)", (client_name, str(contact)))
            client_id = cursor.lastrowid
        else:
            client_id = client_row[0]

        formatted_date = parse_date(d_entered) or "2026-08-01"
        formatted_followup = parse_date(followup_date)
        quotation_val = clean_num(q_amt)
        paid_val = clean_num(paid_amt)
        code = f"REC-{idx:04d}"

        cursor.execute("""
            INSERT INTO opportunities (
                record_code, date_entered, sales_executive_id, client_id,
                project_type, scope_of_work, site_location, site_status,
                measurement_status, quotation_amount, amount_paid,
                deal_status, reason_for_loss, next_followup_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code, formatted_date, sales_id, client_id,
            proj_type, scope, location, site_stat or "Pending",
            meas_stat or "Pending", quotation_val, paid_val,
            deal_stat or "Prospect", loss_reason or "N/A - Won/Active", formatted_followup
        ))
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"Successfully uploaded {inserted_count} opportunity records!")

def upload_daily_activity_logs():
    daily_logs = [
        ("27/07/2026", "Sandra", 0, 10, 1, 1, 3, "Clients complain about casements delaying their orders", "N/A", "Meeting set for tomorrow at Ibero Namanve"),
        ("21/07/2026", "Anna", 1, 15, 0, 1, 1, "N/A", "N/A", "They asked to contact Mr. Abid directly"),
        ("21/07/2026", "Doreen", 1, 4, 0, 2, 0, "N/A", "N/A", "Routine client follow-ups"),
        ("23/07/2026", "Anna", 0, 2, 0, 5, 2, "Complaint about delay on delivery from clients", "N/A", "Will give me feedback before end of August"),
        ("23/07/2026", "Sandra", 1, 2, 0, 2, 1, "N/A", "N/A", "Followed up on pipeline items"),
        ("2026-08-03", "Doreen", 0, 1, 2, 1, 0, "N/A", "N/A", "Site visit completed")
    ]

    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing logs to avoid duplication on re-run
    cursor.execute("DELETE FROM daily_activity_logs;")

    inserted_logs = 0
    for log in daily_logs:
        log_date_raw, sales_person, visited, calls, emails, meetings, leads, challenges, support, remarks = log

        cursor.execute("SELECT user_id FROM users WHERE full_name = ?", (sales_person,))
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute("INSERT INTO users (full_name, role) VALUES (?, 'Sales Executive')", (sales_person,))
            sales_id = cursor.lastrowid
        else:
            sales_id = user_row[0]

        formatted_date = parse_date(log_date_raw) or "2026-08-01"

        cursor.execute("""
            INSERT INTO daily_activity_logs (
                log_date, sales_executive_id, new_companies_visited,
                telephone_calls, emails_sent, meetings_held,
                new_leads_generated, daily_challenges,
                management_support_needed, remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            formatted_date, sales_id, clean_num(visited),
            clean_num(calls), clean_num(emails), clean_num(meetings),
            clean_num(leads), challenges, support, remarks
        ))
        inserted_logs += 1

    conn.commit()
    conn.close()
    print(f"Successfully uploaded {inserted_logs} daily activity log records!")

if __name__ == "__main__":
    init_db()
    upload_raw_dataset()
    upload_daily_activity_logs()