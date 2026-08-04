PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('Sales Executive', 'Sales Manager', 'General Manager', 'Managing Director', 'Admin')),
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_code TEXT UNIQUE,
    date_entered DATE NOT NULL,
    sales_executive_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    project_type TEXT CHECK(project_type IN ('Commercial', 'Residential', 'Industrial', 'Government', 'Institutions')),
    scope_of_work TEXT NOT NULL,
    site_location TEXT,
    site_status TEXT DEFAULT 'Pending',
    measurement_status TEXT DEFAULT 'Pending',
    quotation_amount REAL DEFAULT 0.0,
    amount_paid REAL DEFAULT 0.0,
    deal_status TEXT DEFAULT 'Pipeline' CHECK(deal_status IN ('Pipeline', 'Success (Order Won)', 'Lost', 'Cancelled')),
    reason_for_loss TEXT DEFAULT 'N/A - Won/Active',
    next_followup_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sales_executive_id) REFERENCES users(user_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE IF NOT EXISTS daily_activities (
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_executive_id INTEGER NOT NULL,
    opportunity_id INTEGER,
    activity_type TEXT CHECK(activity_type IN ('Call', 'Email', 'Meeting', 'Site Visit', 'Presentation', 'Follow-up')),
    activity_date DATE NOT NULL,
    notes TEXT,
    FOREIGN KEY (sales_executive_id) REFERENCES users(user_id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id)
);
-- 1. COMPETITOR INTELLIGENCE
CREATE TABLE IF NOT EXISTS competitor_insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER,
    competitor_name TEXT NOT NULL,
    competitor_price REAL,
    win_loss_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id)
);

-- 2. CUSTOMER SATISFACTION (CSAT) LOGS
CREATE TABLE IF NOT EXISTS customer_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    opportunity_id INTEGER,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5), -- 1 to 5 Star Rating
    feedback_comments TEXT,
    survey_date DATE,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

-- 3. SALES TARGETS & SETTINGS
CREATE TABLE IF NOT EXISTS sales_targets (
    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_executive_id INTEGER NOT NULL,
    target_month INTEGER CHECK(target_month BETWEEN 1 AND 12),
    target_year INTEGER DEFAULT 2026,
    target_revenue REAL NOT NULL,
    target_activities INTEGER DEFAULT 20,
    FOREIGN KEY (sales_executive_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS system_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'project_type', 'scope_of_work', 'site_status', 'measurement_status', 'deal_status', 'reason_for_loss', 'market_segment'
    item_value TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);
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