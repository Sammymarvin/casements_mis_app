import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "casements_mis.db"

# Raw daily activity data from your sheet
DAILY_LOGS_DATA = [
    {
        "date": "27/07/2026",
        "sales_person": "Sandra",
        "visited": 0,
        "calls": 1,
        "emails": 0,
        "meetings": 1,
        "leads": 1,
        "challenges": "Clients complain about casements delaying their orders",
        "support": "N/A",
        "remarks": "Meeting set for tomorrow at Ibero Namanve"
    },
    {
        "date": "21/07/2026",
        "sales_person": "Anna",
        "visited": 1,
        "calls": 15,  # Parsed 1 15 0 1 1
        "emails": 0,
        "meetings": 1,
        "leads": 1,
        "challenges": "N/A",
        "support": "N/A",
        "remarks": "They asked to contact Mr. Abid directly"
    },
    {
        "date": "21/07/2026",
        "sales_person": "Doreen",
        "visited": 1,
        "calls": 4,
        "emails": 0,
        "meetings": 2,
        "leads": 0,
        "challenges": "",
        "support": "",
        "remarks": ""
    },
    {
        "date": "23/07/2026",
        "sales_person": "Anna",
        "visited": 0,
        "calls": 20, # Parsed 0 20 5 2 3
        "emails": 5,
        "meetings": 2,
        "leads": 3,
        "challenges": "Complaint about delay on delivery from clients",
        "support": "NA",
        "remarks": "Will give me feed before end of august"
    },
    {
        "date": "23/07/2026",
        "sales_person": "Sandra",
        "visited": 1,
        "calls": 20, # Parsed 1 20 2 1 3
        "emails": 2,
        "meetings": 1,
        "leads": 3,
        "challenges": "",
        "support": "",
        "remarks": ""
    }
]

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def seed_daily_activity_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    inserted_count = 0

    for entry in DAILY_LOGS_DATA:
        # Convert date to standard ISO format (YYYY-MM-DD)
        formatted_date = datetime.strptime(entry["date"], "%d/%m/%Y").strftime("%Y-%m-%d")
        sales_person = entry["sales_person"].strip()

        # 1. Ensure User exists in users table
        cursor.execute("SELECT user_id FROM users WHERE full_name = ?", (sales_person,))
        user_row = cursor.fetchone()
        
        if not user_row:
            cursor.execute("INSERT INTO users (full_name, role) VALUES (?, 'Sales Executive')", (sales_person,))
            user_id = cursor.lastrowid
        else:
            user_id = user_row["user_id"]

        # 2. Insert Daily Log into daily_activity_logs
        query = """
            INSERT INTO daily_activity_logs (
                log_date, sales_executive_id, new_companies_visited, 
                telephone_calls, emails_sent, meetings_held, 
                new_leads_generated, daily_challenges, 
                management_support_needed, remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            formatted_date,
            user_id,
            entry["visited"],
            entry["calls"],
            entry["emails"],
            entry["meetings"],
            entry["leads"],
            entry["challenges"],
            entry["support"],
            entry["remarks"]
        )
        
        cursor.execute(query, params)
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"✅ Successfully inserted {inserted_count} daily activity logs into '{DB_NAME}'!")

if __name__ == "__main__":
    seed_daily_activity_data()