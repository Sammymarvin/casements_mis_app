import sqlite3
import pandas as pd
import os
from datetime import datetime as dt

DB_NAME = "casements_mis.db"

# Raw dataset supplied for insertion
RAW_TSV_DATA = """opportunity_id	Code	Date	Sales Exec	Client Name	Contact Number	Project	Scope	Location	Site Status	Meas. Status	Quotation (UGX)	Paid (UGX)	Balance (UGX)	Deal Status	Reason for Loss	Next Follow-Up
152	CAL-2026-4056	8/12/2026	Sandra	MRS. MITI BARBARA	+256 701 569063	Commercial	Aluminium Windows & Doors	Kampala	Not Ready	Taken	28006896.17	0	28006896.17	Prospect	N/A - Won/Active	8/19/2026
148	CAL-2026-0637	8/11/2026	Sandra	Dr. David Ndawula	2.56772E+11	Residential	Steel Fabrication	Nakakololo- Gayaza	Site Ready	Taken	4500000	0	4500000	Prospect	N/A - Won/Active	8/18/2026
147	CAL-2026-4813	8/11/2026	Anna	Mr.Esami	0702720808	Residential	Aluminium Windows & Doors	Kampala	Site Ready	Taken	2585000	1809500	775500	Prospect	N/A - Won/Active	8/31/2026
145	CAL-2026-0632	8/11/2026	Anna	Mr. Micheal	0772527622	Residential	Aluminium Windows & Doors	Ntinda	Not Ready	Taken	339334	339334	0	Success (Order Won)	N/A - Won/Active	8/18/2026
143	CAL-2026-4628	8/11/2026	Anna	Mr.Rashid	0772843382	Commercial	Aluminium Windows & Doors	Bakuri	In Progress	Pending	1465560	0	1465560	Negotiation	N/A - Won/Active	8/31/2026
142	CAL-2026-5745	8/11/2026	Anna	Mr. Tom Rujjumba	0753366955	Commercial	Aluminium Windows & Doors	fort portal	Site Ready	Taken	14154548	12954459	1200089	Qualified Lead	N/A - Won/Active	8/31/2026
140	CAL-2026-4826	8/11/2026	Anna	Mr.David Entebbe	0785290578	Residential	Aluminium Windows & Doors	Entebbe	In Progress	Taken	126574062	0	126574062	Negotiation	N/A - Won/Active	8/31/2026
138	CAL-2026-4109	8/11/2026	Anna	MR. STEVEN MWES	9133402195	Residential	Aluminium Windows & Doors	Kampala	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	8/18/2026
137	CAL-2026-4054	8/11/2026	Anna	MR. STEVEN MWES	9133402195	Residential	Aluminium Windows & Doors	Kampala	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	8/18/2026
136	CAL-2026-4033	8/11/2026	Sandra	MR. STEVEN MWES	9133402195	Residential	Aluminium Windows & Doors	Ntungamo	Site Ready	Taken	79180469.2	0	79180469.2	Prospect	N/A - Won/Active	8/18/2026
135	CAL-2026-1433	8/11/2026	joseph	MR STEPHEN		Residential	Aluminium Windows & Doors	NTUNGAMO	Not Ready	Pending	79180469.2	0	79180469.2	Prospect	N/A - Won/Active	8/18/2026
134	CAL-2026-1252	8/11/2026	joseph	MIKE	0772493452	Residential	Aluminium Windows & Doors	KYEBANDO 	Not Ready	Pending	242126424	0	242126424	Prospect	N/A - Won/Active	8/18/2026
133	CAL-2026-1054	8/11/2026	joseph	Ms Docus	0773449718	Residential	Aluminium Windows & Doors	seguku	Not Ready	Taken	62522220	0	62522220	Prospect	N/A - Won/Active	8/18/2026
132	CAL-2026-4422	8/10/2026	Doreen	ISA KAJUBI	0702436427 \ +256785578484	Residential	Aluminium Windows & Doors	Kampala	Site Ready	Approved	1803153960	9040000	1794113960	Prospect	N/A - Won/Active	8/17/2026
131	CAL-2026-4152	8/10/2026	Doreen	CHARLES OUMA		Residential	Aluminium Windows & Doors	Kampala	Site Ready	Approved	9538000	9538000	0	Success (Order Won)	N/A - Won/Active	8/17/2026
130	CAL-2026-4017	8/10/2026	Doreen	MR AKENA ERIC	2.56784E+11	Residential	Aluminium Windows & Doors	Kampala	Site Ready	Approved	24000000	10000000	14000000	Success (Order Won)	N/A - Won/Active	8/17/2026
103	REC-0017	8/6/2026	Sandra	Ibero Coffee	27836673818	Industrial	Steel Fabrication	NAMANVE	Not Ready	Pending	44657808	0	44657808	Prospect	N/A - Won/Active	
102	REC-0016	8/5/2026	Sandra	Ibero Coffee	27836673818	Industrial	Steel Fabrication	NAMANVE	Not Ready	Pending	46020000	0	46020000	Prospect	N/A - Won/Active	
101	REC-0015	8/4/2026	Sandra	Ibero Coffee	27836673818	Industrial	Aluminium Windows & Doors	NAMANVE	Not Ready	Pending	55518467	0	55518467	Prospect	N/A - Won/Active	
128	REC-0042	8/3/2026	Doreen	L.A LIVING SPACE		Residential	Aluminium Windows & Doors	KUNGU	Site Ready	Approved	83000000	35000000	48000000	Success (Order Won)	N/A - Won/Active	
126	REC-0040	8/3/2026	Doreen	SARJAN	700612924	Commercial	Aluminium Windows & Doors	KOLOLO	In Progress	Pending	124700000	0	124700000	Quotation Issued	N/A - Won/Active	
125	REC-0039	8/3/2026	Doreen	ssimbwa	757135031	Residential	Steel Fabrication	kakiri	Not Ready	Taken	9230845	0	9230845	Quotation Issued	N/A - Won/Active	
100	REC-0014	8/3/2026	Sandra	Ibero Coffee	27836673818	Industrial	Curtain Walls	NAMANVE	Not Ready	Pending	556393600	0	556393600	Prospect	N/A - Won/Active	
99	REC-0013	8/2/2026	Sandra	Ibero Coffee	27836673818	Industrial	Aluminium Windows & Doors	NAMANVE	Not Ready	Pending	166095651	0	166095651	Prospect	N/A - Won/Active	
129	REC-0043	8/1/2026	Doreen	BRENDAH	772477200	Residential	SHOWER CABINS	KIGO	Site Ready	Taken	15847400	0	15847400	Quotation Issued	N/A - Won/Active	
127	REC-0041	8/1/2026	Doreen	EXCEL CONSTRUCTION	emma@excelconstruction.org	Commercial	Aluminium Windows & Doors	KOLOLO	In Progress	Pending	2980582289	0	2980582289	Quotation Issued	N/A - Won/Active	
98	REC-0012	8/1/2026	Sandra	Ibero Coffee	27836673818	Industrial	Aluminium Windows & Doors	NAMANVE	Not Ready	Pending	135947576	0	135947576	Prospect	N/A - Won/Active	
97	REC-0011	7/31/2026	Sandra	Mr. Oguttu Wilber	2.56784E+11	Residential	Aluminium Windows & Doors	BUSIA	Pending	Pending	130000000	0	130000000	Prospect	N/A - Won/Active	
96	REC-0010	7/30/2026	Sandra	Opus Design	2.56707E+11	Industrial	Steel Fabrication	BULENGA	Pending	Pending	21586600	0	21586600	Prospect	N/A - Won/Active	
121	REC-0035	7/29/2026	Doreen	MR DAVID	704731766	Residential	Steel Fabrication	KAJJANSI	In Progress	Taken	5520000	0	5520000	Quotation Issued	N/A - Won/Active	
120	REC-0034	7/29/2026	Doreen	MR ISA	702436427	Residential	Aluminium Windows & Doors	NAKIGALALA	Site Ready	Taken	22925374	0	22925374	Prospect	N/A - Won/Active	
119	REC-0033	7/29/2026	Doreen	ASILI AGRICULTURAL	766101562	Institutional	UNIPORTS	In Progress	Taken	31813600	0	31813600	-31813600	Prospect	29/7/2027	
118	REC-0032	7/29/2026	Doreen	3D SERVICE		Residential	Sliding Doors	BUNGA	Site Ready	Taken	12140999	9800000	2340999	Success (Order Won)	N/A - Won/Active	
117	REC-0031	7/29/2026	Doreen	VIROGO		Residential	Aluminium Windows & Doors	MITYANA	Site Ready	Taken	3160891	3160891	0	Success (Order Won)	N/A - Won/Active	
116	REC-0030	7/29/2026	Doreen	PONNI SAFARI CAMPS		Institutional	Unipot	KARAMOJA	In Progress	Taken	18354000	18354000	0	Success (Order Won)	N/A - Won/Active	
115	REC-0029	7/29/2026	Doreen	SBC UGANDA		Industrial	STAINLESS MIRROR	AIRPORT	Site Ready	Taken	19488585	11561025	7927560	Success (Order Won)	N/A - Won/Active	
95	REC-0009	7/29/2026	Sandra	Mr. Esami	2.56703E+11	Commercial	Toughened Glass	WANDEGAYA	Pending	Pending	2585000	0	2585000	Prospect	N/A - Won/Active	
122	REC-0036	7/28/2026	Doreen	MY KAYUMBA		Residential	Steel Fabrication	KIGALI	In Progress	Taken	7363200	0	7363200	Quotation Issued	N/A - Won/Active	
94	REC-0008	7/28/2026	Sandra	Mr. Edgar	2.56706E+11	Residential	Aluminium Windows & Doors	NAGURU	Pending	Pending	8500000	0	8500000	Prospect	N/A - Won/Active	
93	REC-0007	7/27/2026	Sandra	Dr. Ndawula David	2.56772E+11	Residential	Steel Fabrication	GAYAZA	Pending	Pending	4511351	0	4511351	Prospect	N/A - Won/Active	
92	REC-0006	7/26/2026	Sandra	Andrew Amara	2.56752E+11	Commercial	Aluminium Windows & Doors	LUWEERO	Pending	Pending	42909976	0	42909976	Prospect	N/A - Won/Active	
91	REC-0005	7/25/2026	Sandra	Madam Yudaya	2.56773E+11	Residential	Aluminium Windows & Doors	KIRA-NSASA	Pending	Pending	132032328	0	132032328	Prospect	N/A - Won/Active	
124	REC-0038	7/24/2026	Doreen	MS CAROLYNE	772313112	Residential	Aluminium Windows & Doors	MUTUNDWE	Not Ready	Taken	44041723	0	44041723	Quotation Issued	N/A - Won/Active	
90	REC-0004	7/24/2026	Sandra	Arch Forum	2.56777E+11	Commercial	Aluminium Windows & Doors	NTINDA	Pending	Pending	311437363	0	311437363	Prospect	N/A - Won/Active	
123	REC-0037	7/23/2026	Doreen	MR CHARLES	782517278	Residential	Aluminium Windows & Doors	LUZIRA	In Progress	Taken	20494430	0	20494430	Prospect	N/A - Won/Active	
114	REC-0028	7/23/2026	Anna	Mr.Caleb	2.56778E+12	Residential	Aluminium Windows & Doors	JINJA	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
113	REC-0027	7/23/2026	Anna	Mr.Edward	2.56772E+11	Residential	Aluminium Windows & Doors	NASANA	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
112	REC-0026	7/23/2026	Anna	Mr.ODOI	2.56783E+11	Residential	Aluminium Windows & Doors	JINJA	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
111	REC-0025	7/23/2026	Anna	Mr.Erisa	2.56753E+11	Residential	Aluminium Windows & Doors	MBARARA	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
110	REC-0024	7/23/2026	Anna	QUISA Constructions	2.56751E+11	Residential	Aluminium Windows & Doors	MBARARA	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
109	REC-0023	7/23/2026	Anna	Mr joel	2.56706E+11	Residential	Steel Fabrication	WAKISO	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
89	REC-0003	7/23/2026	Sandra	Arch Forum	2.56777E+11	Commercial	Aluminium Windows & Doors	NTINDA	Pending	Pending	141000000	0	141000000	Prospect	N/A - Won/Active	
108	REC-0022	7/22/2026	Anna	Madam winnie	2.56772E+11	Residential	Aluminium Windows & Doors	WAKISO	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
88	REC-0002	7/22/2026	Sandra	Zephyr Balunywa	2.56777E+11	Commercial	Aluminium Windows & Doors	BUSEMBATIA	Not Ready	Taken	2830000	2830000	0	Success (Order Won)	N/A - Won/Active	8/14/2026
107	REC-0021	7/21/2026	Anna	Mr.Smith	2.56775E+12	Residential	Aluminium Windows & Doors	WAKISO	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
106	REC-0020	7/21/2026	Anna	Mr.frank	2.5675E+11	Commercial	Aluminium Windows & Doors	MBARARA	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
87	REC-0001	7/21/2026	Sandra	Mirondo Fred	750142995	Institutional	Office Partitions	JINJA	Not Ready	Pending	58546260	58546260	0	Success (Order Won)	N/A - Won/Active	8/8/2026
105	REC-0019	7/20/2026	Anna	Madam Mutoni	2.56787E+11	Residential	Aluminium Windows & Doors	Wakiso	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
104	REC-0018	7/20/2026	Anna	Mr.Mugisha Amujjade	2.56787E+11	Residential	Aluminium Windows & Doors	KISOZI	Not Ready	Pending	0	0	0	Prospect	N/A - Won/Active	
144	CAL-2026-5421	7/17/2026	Sandra	Mr. Mirondo fred	2.56783E+11	Institutional	Office Partitions	Jinja	Not Ready	Pending	79126350.31	0	79126350.31	Prospect	N/A - Won/Active	8/18/2026
141	CAL-2026-5430	7/17/2026	Sandra	Mr. Fred Mirondo	2.56783E+11	Institutional	Aluminium Windows & Doors	JINJA	Site Ready	Pending	79126350.31	0	79126350.31	Prospect	N/A - Won/Active	8/18/2026
151	CAL-2026-2925	7/16/2026	Sandra	Mrs. Zephyr Balunywa	2.56777E+11	Commercial	Aluminium Windows & Doors	Busembatia	Not Ready	Taken	2500000	0	2500000	Prospect	N/A - Won/Active	8/18/2026
149	CAL-2026-2029	7/13/2026	Sandra	Mr. Kiiza Nelson	2.56773E+11	Residential	Aluminium Windows & Doors	Akright	Site Ready	Taken	46488050	0	46488050	Prospect	N/A - Won/Active	8/12/2026
146	CAL-2026-0953	7/13/2026	Sandra	Mr. Andrew Mara	2.56752E+11	Residential	Aluminium Windows & Doors	Luweero	Not Ready	Pending	42909976.2	0	42909976.2	Prospect	N/A - Won/Active	8/18/2026
139	CAL-2026-4355	7/4/2026	Sandra	MR.KASUMBA	2.56781E+11	Residential	Aluminium Windows & Doors	Mawokota	Not Ready	Pending	16027521.27	0	16027521.27	Prospect	N/A - Won/Active	8/18/2026
150	CAL-2026-2336	6/30/2026	Sandra	Opus Design	2.56707E+11	Commercial	Steel Fabrication	Bulenga	Not Ready	Pending	21584600	0	21584600	Prospect	N/A - Won/Active	8/18/2026"""

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def parse_date(date_str):
    if not date_str or str(date_str).strip() in ("", "nan", "None"):
        return None
    date_str = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return dt.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None

def clean_num(val):
    if pd.isna(val) or val is None:
        return 0.0
    val_str = str(val).lower().replace("ugx", "").replace("usd", "").replace(",", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def update_database():
    import io
    df = pd.read_csv(io.StringIO(RAW_TSV_DATA), sep="\t")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    new_records = 0
    updated_records = 0

    for _, row in df.iterrows():
        sales_person = str(row['Sales Exec']).strip()
        client_name = str(row['Client Name']).strip()
        contact = str(row['Contact Number']).strip() if pd.notna(row['Contact Number']) else ""
        d_entered = str(row['Date']).strip()
        code = str(row['Code']).strip()
        proj_type = str(row['Project']).strip()
        scope = str(row['Scope']).strip()
        location = str(row['Location']).strip()
        site_stat = str(row['Site Status']).strip()
        meas_stat = str(row['Meas. Status']).strip()
        q_amt = row['Quotation (UGX)']
        paid_amt = row['Paid (UGX)']
        deal_stat = str(row['Deal Status']).strip()
        loss_reason = str(row['Reason for Loss']).strip()
        followup_date = str(row['Next Follow-Up']).strip() if pd.notna(row['Next Follow-Up']) else None

        # 1. Dynamic User Resolution
        cursor.execute("SELECT user_id FROM users WHERE LOWER(full_name) = LOWER(?)", (sales_person,))
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute("INSERT INTO users (full_name, role) VALUES (?, 'Sales Executive')", (sales_person,))
            sales_id = cursor.lastrowid
        else:
            sales_id = user_row['user_id']

        # 2. Dynamic Scope Registration in system_settings
        cursor.execute("SELECT setting_id FROM system_settings WHERE category = 'scope_of_work' AND LOWER(item_value) = LOWER(?)", (scope,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO system_settings (category, item_value) VALUES ('scope_of_work', ?)", (scope,))

        # 3. Dynamic Client Resolution
        cursor.execute("SELECT client_id FROM clients WHERE LOWER(company_name) = LOWER(?)", (client_name,))
        client_row = cursor.fetchone()
        if not client_row:
            cursor.execute("INSERT INTO clients (company_name, phone) VALUES (?, ?)", (client_name, contact))
            client_id = cursor.lastrowid
        else:
            client_id = client_row['client_id']

        formatted_date = parse_date(d_entered)
        formatted_followup = parse_date(followup_date)

        # 4. Check if record code exists
        cursor.execute("SELECT opportunity_id FROM opportunities WHERE record_code = ?", (code,))
        existing_opp = cursor.fetchone()

        if existing_opp:
            cursor.execute("""
                UPDATE opportunities SET
                    date_entered = ?, sales_executive_id = ?, client_id = ?,
                    project_type = ?, scope_of_work = ?, site_location = ?,
                    site_status = ?, measurement_status = ?, quotation_amount = ?,
                    amount_paid = ?, deal_status = ?, reason_for_loss = ?,
                    next_followup_date = ?
                WHERE record_code = ?
            """, (
                formatted_date, sales_id, client_id,
                proj_type, scope, location,
                site_stat or "Pending", meas_stat or "Pending",
                clean_num(q_amt), clean_num(paid_amt),
                deal_stat or "Prospect", loss_reason or "N/A - Won/Active",
                formatted_followup, code
            ))
            updated_records += 1
        else:
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
                meas_stat or "Pending", clean_num(q_amt), clean_num(paid_amt),
                deal_stat or "Prospect", loss_reason or "N/A - Won/Active", formatted_followup
            ))
            new_records += 1

    conn.commit()
    conn.close()
    print(f"Sync Complete! New records added: {new_records}, Updated records: {updated_records}")

if __name__ == "__main__":
    update_database()
