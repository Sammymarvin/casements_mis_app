import sqlite3
import re
from datetime import datetime

DB_NAME = "casements_mis.db"

RAW_SALES_DATA = [
    # Sandra's Records
    {"date": "21/07/2026", "sales_person": "Sandra", "client": "Mirondo Fred", "phone": "0750142995", "project": "Institutional", "scope": "Office Partitions", "location": "JINJA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 58546260, "paid": 58546260, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "2026-08-08", "remarks": "ns"},
    {"date": "22/07/2026", "sales_person": "Sandra", "client": "Zephyr Balunywa", "phone": "256776610176", "project": "Commercial", "scope": "Aluminium Windows & Doors", "location": "BUSEMBATIA", "site_status": "Pending", "meas_status": "Taken", "quote": 2550000, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Sandra", "client": "Arch Forum", "phone": "256776690915", "project": "Commercial", "scope": "Aluminium Windows & Doors", "location": "NTINDA", "site_status": "Pending", "meas_status": "Pending", "quote": 141000000, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "24/07/2026", "sales_person": "Sandra", "client": "Arch Forum", "phone": "256776690915", "project": "Commercial", "scope": "Aluminium Windows & Doors", "location": "NTINDA", "site_status": "Pending", "meas_status": "Pending", "quote": 311437363, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "25/07/2026", "sales_person": "Sandra", "client": "Madam Yudaya", "phone": "256772650938", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "KIRA-NSASA", "site_status": "Pending", "meas_status": "Pending", "quote": 132032328, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "26/07/2026", "sales_person": "Sandra", "client": "Andrew Amara", "phone": "256752282505", "project": "Commercial", "scope": "Aluminium Windows & Doors", "location": "LUWEERO", "site_status": "Pending", "meas_status": "Pending", "quote": 42909976, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "27/07/2026", "sales_person": "Sandra", "client": "Dr. Ndawula David", "phone": "256772409023", "project": "Residential", "scope": "Steel Fabrication", "location": "GAYAZA", "site_status": "Pending", "meas_status": "Pending", "quote": 4511351, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "28/07/2026", "sales_person": "Sandra", "client": "Mr. Edgar", "phone": "256706078772", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "NAGURU", "site_status": "Pending", "meas_status": "Pending", "quote": 8500000, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "29/07/2026", "sales_person": "Sandra", "client": "Mr. Esami", "phone": "256702720808", "project": "Commercial", "scope": "Toughened Glass", "location": "WANDEGAYA", "site_status": "Pending", "meas_status": "Pending", "quote": 2585000, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "30/07/2026", "sales_person": "Sandra", "client": "Opus Design", "phone": "256706690312", "project": "Industrial", "scope": "Steel Fabrication", "location": "BULENGA", "site_status": "Pending", "meas_status": "Pending", "quote": 21586600, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "31/07/2026", "sales_person": "Sandra", "client": "Mr. Oguttu Wilber", "phone": "256784261089", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "BUSIA", "site_status": "Pending", "meas_status": "Pending", "quote": 130000000, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "01/08/2026", "sales_person": "Sandra", "client": "Ibero Coffee", "phone": "27836673818", "project": "Industrial", "scope": "Aluminium Windows & Doors", "location": "NAMANVE", "site_status": "Not Ready", "meas_status": "Pending", "quote": 135947576, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "02/08/2026", "sales_person": "Sandra", "client": "Ibero Coffee", "phone": "27836673818", "project": "Industrial", "scope": "Aluminium Windows & Doors", "location": "NAMANVE", "site_status": "Not Ready", "meas_status": "Pending", "quote": 166095651, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "03/08/2026", "sales_person": "Sandra", "client": "Ibero Coffee", "phone": "27836673818", "project": "Industrial", "scope": "Curtain Walls", "location": "NAMANVE", "site_status": "Not Ready", "meas_status": "Pending", "quote": 556393600, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "04/08/2026", "sales_person": "Sandra", "client": "Ibero Coffee", "phone": "27836673818", "project": "Industrial", "scope": "Aluminium Windows & Doors", "location": "NAMANVE", "site_status": "Not Ready", "meas_status": "Pending", "quote": 55518467, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "05/08/2026", "sales_person": "Sandra", "client": "Ibero Coffee", "phone": "27836673818", "project": "Industrial", "scope": "Steel Fabrication", "location": "NAMANVE", "site_status": "Not Ready", "meas_status": "Pending", "quote": 46020000, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "06/08/2026", "sales_person": "Sandra", "client": "Ibero Coffee", "phone": "27836673818", "project": "Industrial", "scope": "Steel Fabrication", "location": "NAMANVE", "site_status": "Not Ready", "meas_status": "Pending", "quote": 44657808, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},

    # Anna's Records
    {"date": "20/07/2026", "sales_person": "Anna", "client": "Mr. Mugisha Amujjade", "phone": "256787476267", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "KISOZI", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "20/07/2026", "sales_person": "Anna", "client": "Madam Mutoni", "phone": "256786791714", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "Wakiso", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "21/07/2026", "sales_person": "Anna", "client": "Mr. Frank", "phone": "256749795811", "project": "Commercial", "scope": "Aluminium Windows & Doors", "location": "MBARARA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "21/07/2026", "sales_person": "Anna", "client": "Mr. Smith", "phone": "2567750000875", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "WAKISO", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "22/07/2026", "sales_person": "Anna", "client": "Madam Winnie", "phone": "256771915697", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "WAKISO", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Anna", "client": "Mr. Joel", "phone": "256705713353", "project": "Residential", "scope": "Steel Fabrication", "location": "WAKISO", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Anna", "client": "QUISA Constructions", "phone": "256751458275", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "MBARARA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Anna", "client": "Mr. Erisa", "phone": "256752888424", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "MBARARA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Anna", "client": "Mr. ODOI", "phone": "256782612306", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "JINJA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Anna", "client": "Mr. Edward", "phone": "256772381212", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "NASANA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Anna", "client": "Mr. Caleb", "phone": "2567778880985", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "JINJA", "site_status": "Not Ready", "meas_status": "Pending", "quote": 0, "paid": 0, "status": "Prospect", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},

    # Doreen's Records
    {"date": "20/07/2026", "sales_person": "Doreen", "client": "SBC UGANDA", "phone": "", "project": "Industrial", "scope": "STAINLESS MIRROR", "location": "AIRPORT", "site_status": "Site Ready", "meas_status": "Taken", "quote": 19488585, "paid": 11561025, "status": "In Progress", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "21/07/2026", "sales_person": "Doreen", "client": "PONNI SAFARI CAMPS", "phone": "", "project": "Institutional", "scope": "Unipot", "location": "KARAMOJA", "site_status": "In Progress", "meas_status": "Taken", "quote": 18354000, "paid": 18354000, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "22/07/2026", "sales_person": "Doreen", "client": "VIROGO", "phone": "", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "MITYANA", "site_status": "Site Ready", "meas_status": "Taken", "quote": 3160891, "paid": 3160891, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "22/07/2026", "sales_person": "Doreen", "client": "3D SERVICE", "phone": "", "project": "Residential", "scope": "Sliding Doors", "location": "BUNGA", "site_status": "Site Ready", "meas_status": "Taken", "quote": 12140999, "paid": 9800000, "status": "In Progress", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "29/07/2026", "sales_person": "Doreen", "client": "ASILI AGRICULTURAL", "phone": "", "project": "Institutional", "scope": "Unipot", "location": "UNIPORTS", "site_status": "In Progress", "meas_status": "Taken", "quote": 31813600, "paid": 31813600, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "29/07/2026", "sales_person": "Doreen", "client": "MR ISA", "phone": "0702436427", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "NAKIGALALA", "site_status": "Site Ready", "meas_status": "Taken", "quote": 22925374, "paid": 22925374, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "29/07/2026", "sales_person": "Doreen", "client": "MR DAVID", "phone": "0704731766", "project": "Residential", "scope": "Steel Fabrication", "location": "KAJJANSI", "site_status": "In Progress", "meas_status": "Taken", "quote": 5520000, "paid": 5520000, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "28/07/2026", "sales_person": "Doreen", "client": "MR KAYUMBA", "phone": "", "project": "Residential", "scope": "Steel Fabrication", "location": "KIGALI", "site_status": "In Progress", "meas_status": "Taken", "quote": 7363200, "paid": 7363200, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "23/07/2026", "sales_person": "Doreen", "client": "MR CHARLES", "phone": "0782517278", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "LUZIRA", "site_status": "In Progress", "meas_status": "Taken", "quote": 20494430, "paid": 20494430, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": ""},
    {"date": "24/07/2026", "sales_person": "Doreen", "client": "MS CAROLYNE", "phone": "0772313112", "project": "Residential", "scope": "Aluminium Windows & Doors", "location": "MUTUNDWE", "site_status": "Not Ready", "meas_status": "Taken", "quote": 44041723, "paid": 44041723, "status": "Success (Order Won)", "loss": "N/A - Won/Active", "followup": "", "remarks": "Mr. FREDRICK"}
]

def format_iso_date(date_str):
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        # Normalize years typed incorrectly in original logs (e.g., 2027/2028 -> 2026)
        clean_str = re.sub(r'202[789]', '2026', date_str.strip())
        return datetime.strptime(clean_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")

def seed_sales_opportunities():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    inserted_count = 0

    for idx, row in enumerate(RAW_SALES_DATA, start=1):
        record_code = f"CAL-2026-TXN{idx:03d}"
        iso_date = format_iso_date(row["date"])
        sales_person = row["sales_person"].strip()
        client_name = row["client"].strip()

        # 1. Get or Create User
        cursor.execute("SELECT user_id FROM users WHERE full_name = ?", (sales_person,))
        user_res = cursor.fetchone()
        if not user_res:
            cursor.execute("INSERT INTO users (full_name, role) VALUES (?, 'Sales Executive')", (sales_person,))
            user_id = cursor.lastrowid
        else:
            user_id = user_res[0]

        # 2. Get or Create Client
        cursor.execute("SELECT client_id FROM clients WHERE company_name = ?", (client_name,))
        client_res = cursor.fetchone()
        if not client_res:
            cursor.execute("INSERT INTO clients (company_name, phone) VALUES (?, ?)", (client_name, str(row["phone"])))
            client_id = cursor.lastrowid
        else:
            client_id = client_res[0]

        # 3. Insert Opportunity
        query_opp = """
            INSERT INTO opportunities (
                record_code, date_entered, sales_executive_id, client_id, 
                project_type, scope_of_work, site_location, site_status, 
                measurement_status, quotation_amount, amount_paid, deal_status, 
                reason_for_loss, next_followup_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            record_code,
            iso_date,
            user_id,
            client_id,
            row["project"],
            row["scope"],
            row["location"],
            row["site_status"],
            row["meas_status"],
            float(row["quote"]),
            float(row["paid"]),
            row["status"],
            row["loss"],
            row["followup"] if row["followup"] else None
        )

        cursor.execute(query_opp, params)
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"✅ Successfully inserted {inserted_count} sales transactions into '{DB_NAME}'!")

if __name__ == "__main__":
    seed_sales_opportunities()