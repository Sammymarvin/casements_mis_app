import io
import pandas as pd
import psycopg2

# Raw dataset
csv_data = """opportunity_id\tCode\tDate\tSales Exec\tClient Name\tContact Number\tProject\tScope\tLocation\tSite Status\tMeas. Status\tQuotation (UGX)\tPaid (UGX)\tBalance (UGX)\tDeal Status\tReason for Loss\tNext Follow-Up
153\tCAL-2026-4925\t8/21/2026\tAnna\tMADAM XUMEL ALIANA\t766977777\tResidential\tAluminium Windows & Doors\tKampala\tNot Ready\tApproved\t16756491\t0\t16756491\tProspect\tN/A - Won/Active\t8/31/2026
130\tCAL-2026-4056\t8/12/2026\tSandra\tMRS. MITI BARBARA\t+256 701 569063\tCommercial\tAluminium Windows & Doors\tKampala\tNot Ready\tTaken\t28006896.17\t0\t28006896.17\tProspect\tN/A - Won/Active\t8/19/2026
142\tCAL-2026-1054\t8/11/2026\tjoseph\tMs Docus\t773449718\tResidential\tAluminium Windows & Doors\tseguku\tNot Ready\tTaken\t62522220\t0\t62522220\tProspect\tN/A - Won/Active\t8/18/2026
141\tCAL-2026-1252\t8/11/2026\tjoseph\tMIKE\t772493452\tResidential\tAluminium Windows & Doors\tKYEBANDO\tNot Ready\tPending\t242126424\t0\t242126424\tProspect\tN/A - Won/Active\t8/18/2026
140\tCAL-2026-1433\t8/11/2026\tjoseph\tMR STEPHEN\t\tResidential\tAluminium Windows & Doors\tNTUNGAMO\tNot Ready\tPending\t79180469.2\t0\t79180469.2\tProspect\tN/A - Won/Active\t8/18/2026
139\tCAL-2026-4033\t8/11/2026\tSandra\tMR. STEVEN MWES\t9133402195\tResidential\tAluminium Windows & Doors\tNtungamo\tSite Ready\tTaken\t79180469.2\t0\t79180469.2\tProspect\tN/A - Won/Active\t8/18/2026
138\tCAL-2026-4054\t8/11/2026\tAnna\tAFOM CONTRUCTIONS\t783917965\tResidential\tAluminium Windows & Doors\t\tPending\tPending\t18504227\t0\t\tN/A - Won/Active\tN/A - Won/Active\t8/18/2026
137\tCAL-2026-4109\t8/11/2026\tAnna\tMADAM LYDIA\tUNIPORTS\tCommercial\tAluminium Windows & Doors\t\tPending\tPending\t22254800\t0\t\tProspect\tN/A - Won/Active\t8/18/2026
136\tCAL-2026-4826\t8/11/2026\tAnna\tMr.David Entebbe\t785290578\tResidential\tAluminium Windows & Doors\tEntebbe\tIn Progress\tTaken\t126574062\t0\t126574062\tNegotiation\tN/A - Won/Active\t8/31/2026
135\tCAL-2026-5745\t8/11/2026\tAnna\tMr. Tom Rujjumba\t753366955\tCommercial\tAluminium Windows & Doors\tfort portal\tSite Ready\tTaken\t14154548\t12954459\t1200089\tQualified Lead\tN/A - Won/Active\t8/31/2026
134\tCAL-2026-4628\t8/11/2026\tAnna\tMr.Rashid\t772843382\tCommercial\tAluminium Windows & Doors\tBakuri\tIn Progress\tPending\t1465560\t0\t1465560\tNegotiation\tN/A - Won/Active\t8/31/2026
133\tCAL-2026-0632\t8/11/2026\tAnna\tMr. Micheal\t772527622\tResidential\tAluminium Windows & Doors\tNtinda\tNot Ready\tTaken\t339334\t339334\t0\tSuccess (Order Won)\tN/A - Won/Active\t8/18/2026
132\tCAL-2026-4813\t8/11/2026\tAnna\tMr.Esami\t702720808\tResidential\tAluminium Windows & Doors\tKampala\tSite Ready\tTaken\t2585000\t1809500\t775500\tProspect\tN/A - Won/Active\t8/31/2026
131\tCAL-2026-0637\t8/11/2026\tSandra\tDr. David Ndawula\t2.57E+11\tResidential\tSteel Fabrication\tNakakololo- Gayaza\tSite Ready\tTaken\t4500000\t0\t4500000\tProspect\tN/A - Won/Active\t8/18/2026
145\tCAL-2026-4017\t8/10/2026\tDoreen\tMR AKENA ERIC\t2.57E+11\tResidential\tAluminium Windows & Doors\tKampala\tSite Ready\tApproved\t24000000\t10000000\t14000000\tSuccess (Order Won)\tN/A - Won/Active\t8/17/2026
144\tCAL-2026-4152\t8/10/2026\tDoreen\tCHARLES OUMA\t\tResidential\tAluminium Windows & Doors\tKampala\tSite Ready\tApproved\t9538000\t9538000\t0\tSuccess (Order Won)\tN/A - Won/Active\t8/17/2026
143\tCAL-2026-4422\t8/10/2026\tDoreen\tISA KAJUBI\t0702436427 \\ +256785578484\tResidential\tAluminium Windows & Doors\tKampala\tSite Ready\tApproved\t1803153960\t9040000\t1794113960\tProspect\tN/A - Won/Active\t8/17/2026
103\tREC-0017\t8/6/2026\tSandra\tIbero Coffee\t27836673818\tIndustrial\tSteel Fabrication\tNAMANVE\tNot Ready\tPending\t44657808\t0\t44657808\tProspect\tN/A - Won/Active\t
102\tREC-0016\t8/5/2026\tSandra\tIbero Coffee\t27836673818\tIndustrial\tSteel Fabrication\tNAMANVE\tNot Ready\tPending\t46020000\t0\t46020000\tProspect\tN/A - Won/Active\t
101\tREC-0015\t8/4/2026\tSandra\tIbero Coffee\t27836673818\tIndustrial\tAluminium Windows & Doors\tNAMANVE\tNot Ready\tPending\t55518467\t0\t55518467\tProspect\tN/A - Won/Active\t
128\tREC-0042\t8/3/2026\tDoreen\tL.A LIVING SPACE\t\tResidential\tAluminium Windows & Doors\tKUNGU\tSite Ready\tApproved\t83000000\t35000000\t48000000\tSuccess (Order Won)\tN/A - Won/Active\t
126\tREC-0040\t8/3/2026\tDoreen\tSARJAN\t700612924\tCommercial\tAluminium Windows & Doors\tKOLOLO\tIn Progress\tPending\t124700000\t0\t124700000\tQuotation Issued\tN/A - Won/Active\t
125\tREC-0039\t8/3/2026\tDoreen\tssimbwa\t757135031\tResidential\tSteel Fabrication\tkakiri\tNot Ready\tTaken\t9230845\t0\t9230845\tQuotation Issued\tN/A - Won/Active\t
100\tREC-0014\t8/3/2026\tSandra\tIbero Coffee\t27836673818\tIndustrial\tCurtain Walls\tNAMANVE\tNot Ready\tPending\t556393600\t0\t556393600\tProspect\tN/A - Won/Active\t
99\tREC-0013\t8/2/2026\tSandra\tIbero Coffee\t27836673818\tIndustrial\tAluminium Windows & Doors\tNAMANVE\tNot Ready\tPending\t166095651\t0\t166095651\tProspect\tN/A - Won/Active\t
129\tREC-0043\t8/1/2026\tDoreen\tBRENDAH\t772477200\tResidential\tSHOWER CABINS\tKIGO\tSite Ready\tTaken\t15847400\t0\t15847400\tQuotation Issued\tN/A - Won/Active\t
127\tREC-0041\t8/1/2026\tDoreen\tEXCEL CONSTRUCTION\temma@excelconstruction.org\tCommercial\tAluminium Windows & Doors\tKOLOLO\tIn Progress\tPending\t2980582289\t0\t2980582289\tQuotation Issued\tN/A - Won/Active\t
98\tREC-0012\t8/1/2026\tSandra\tIbero Coffee\t27836673818\tIndustrial\tAluminium Windows & Doors\tNAMANVE\tNot Ready\tPending\t135947576\t0\t135947576\tProspect\tN/A - Won/Active\t
97\tREC-0011\t7/31/2026\tSandra\tMr. Oguttu Wilber\t2.57E+11\tResidential\tAluminium Windows & Doors\tBUSIA\tPending\tPending\t130000000\t0\t130000000\tProspect\tN/A - Won/Active\t
96\tREC-0010\t7/30/2026\tSandra\tOpus Design\t2.57E+11\tIndustrial\tSteel Fabrication\tBULENGA\tPending\tPending\t21586600\t0\t21586600\tProspect\tN/A - Won/Active\t
121\tREC-0035\t7/29/2026\tDoreen\tMR DAVID\t704731766\tResidential\tSteel Fabrication\tKAJJANSI\tIn Progress\tTaken\t5520000\t0\t5520000\tQuotation Issued\tN/A - Won/Active\t
120\tREC-0034\t7/29/2026\tDoreen\tMR ISA\t702436427\tResidential\tAluminium Windows & Doors\tNAKIGALALA\tSite Ready\tTaken\t22925374\t0\t22925374\tProspect\tN/A - Won/Active\t
119\tREC-0033\t7/29/2026\tDoreen\tASILI AGRICULTURAL\t766101562\tInstitutional\tUNIPORTS\t\tIn Progress\tTaken\t31813600\t0\t-31813600\tProspect\t29/7/2027\t
118\tREC-0032\t7/29/2026\tDoreen\t3D SERVICE\t\tResidential\tSliding Doors\tBUNGA\tSite Ready\tTaken\t12140999\t9800000\t2340999\tSuccess (Order Won)\tN/A - Won/Active\t
117\tREC-0031\t7/29/2026\tDoreen\tVIROGO\t\tResidential\tAluminium Windows & Doors\tMITYANA\tSite Ready\tTaken\t3160891\t3160891\t0\tSuccess (Order Won)\tN/A - Won/Active\t
116\tREC-0030\t7/29/2026\tDoreen\tPONNI SAFARI CAMPS\t\tInstitutional\tUnipot\tKARAMOJA\tIn Progress\tTaken\t18354000\t18354000\t0\tSuccess (Order Won)\tN/A - Won/Active\t
115\tREC-0029\t7/29/2026\tDoreen\tSBC UGANDA\t\tIndustrial\tSTAINLESS MIRROR\tAIRPORT\tSite Ready\tTaken\t19488585\t11561025\t7927560\tSuccess (Order Won)\tN/A - Won/Active\t
95\tREC-0009\t7/29/2026\tSandra\tMr. Esami\t2.57E+11\tCommercial\tToughened Glass\tWANDEGAYA\tPending\tPending\t2585000\t0\t2585000\tProspect\tN/A - Won/Active\t
122\tREC-0036\t7/28/2026\tDoreen\tMY KAYUMBA\t\tResidential\tSteel Fabrication\tKIGALI\tIn Progress\tTaken\t7363200\t0\t7363200\tQuotation Issued\tN/A - Won/Active\t
94\tREC-0008\t7/28/2026\tSandra\tMr. Edgar\t2.57E+11\tResidential\tAluminium Windows & Doors\tNAGURU\tPending\tPending\t8500000\t0\t8500000\tProspect\tN/A - Won/Active\t
93\tREC-0007\t7/27/2026\tSandra\tDr. Ndawula David\t2.57E+11\tResidential\tSteel Fabrication\tGAYAZA\tPending\tPending\t4511351\t0\t4511351\tProspect\tN/A - Won/Active\t
92\tREC-0006\t7/26/2026\tSandra\tAndrew Amara\t2.57E+11\tCommercial\tAluminium Windows & Doors\tLUWEERO\tPending\tPending\t42909976\t0\t42909976\tProspect\tN/A - Won/Active\t
91\tREC-0005\t7/25/2026\tSandra\tMadam Yudaya\t2.57E+11\tResidential\tAluminium Windows & Doors\tKIRA-NSASA\tPending\tPending\t132032328\t0\t132032328\tProspect\tN/A - Won/Active\t
124\tREC-0038\t7/24/2026\tDoreen\tMS CAROLYNE\t772313112\tResidential\tAluminium Windows & Doors\tMUTUNDWE\tNot Ready\tTaken\t44041723\t0\t44041723\tQuotation Issued\tN/A - Won/Active\t
90\tREC-0004\t7/24/2026\tSandra\tArch Forum\t2.57E+11\tCommercial\tAluminium Windows & Doors\tNTINDA\tPending\tPending\t311437363\t0\t311437363\tProspect\tN/A - Won/Active\t
123\tREC-0037\t7/23/2026\tDoreen\tMR CHARLES\t782517278\tResidential\tAluminium Windows & Doors\tLUZIRA\tIn Progress\tTaken\t20494430\t0\t20494430\tProspect\tN/A - Won/Active\t
114\tREC-0028\t7/23/2026\tAnna\tMr.Caleb\t2.57E+12\tResidential\tAluminium Windows & Doors\tJINJA\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
113\tREC-0027\t7/23/2026\tAnna\tMr.Edward\t2.57E+11\tResidential\tAluminium Windows & Doors\tNASANA\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
112\tREC-0026\t7/23/2026\tAnna\tMr.ODOI\t2.57E+11\tResidential\tAluminium Windows & Doors\tJINJA\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
111\tREC-0025\t7/23/2026\tAnna\tMr.Erisa\t2.57E+11\tResidential\tAluminium Windows & Doors\tMBARARA\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
110\tREC-0024\t7/23/2026\tAnna\tQUISA Constructions\t2.57E+11\tResidential\tAluminium Windows & Doors\tMBARARA\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
109\tREC-0023\t7/23/2026\tAnna\tMr joel\t2.57E+11\tResidential\tSteel Fabrication\tWAKISO\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
89\tREC-0003\t7/23/2026\tSandra\tArch Forum\t2.57E+11\tCommercial\tAluminium Windows & Doors\tNTINDA\tPending\tPending\t141000000\t0\t141000000\tProspect\tN/A - Won/Active\t
108\tREC-0022\t7/22/2026\tAnna\tMadam winnie\t2.57E+11\tResidential\tAluminium Windows & Doors\tWAKISO\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
88\tREC-0002\t7/22/2026\tSandra\tZephyr Balunywa\t2.57E+11\tCommercial\tAluminium Windows & Doors\tBUSEMBATIA\tNot Ready\tTaken\t2830000\t2830000\t0\tSuccess (Order Won)\tN/A - Won/Active\t8/14/2026
107\tREC-0021\t7/21/2026\tAnna\tMr.Smith\t2.57E+12\tResidential\tAluminium Windows & Doors\tWAKISO\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
106\tREC-0020\t7/21/2026\tAnna\tMr.frank\t2.57E+11\tCommercial\tAluminium Windows & Doors\tMBARARA\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
87\tREC-0001\t7/21/2026\tSandra\tMirondo Fred\t750142995\tInstitutional\tOffice Partitions\tJINJA\tNot Ready\tPending\t58546260\t58546260\t0\tSuccess (Order Won)\tN/A - Won/Active\t8/8/2026
105\tREC-0019\t7/20/2026\tAnna\tMadam Mutoni\t2.57E+11\tResidential\tAluminium Windows & Doors\tWakiso\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
104\tREC-0018\t7/20/2026\tAnna\tMr.Mugisha Amujjade\t2.57E+11\tResidential\tAluminium Windows & Doors\tKISOZI\tNot Ready\tPending\t0\t0\t0\tProspect\tN/A - Won/Active\t
147\tCAL-2026-5430\t7/17/2026\tSandra\tMr. Fred Mirondo\t2.57E+11\tInstitutional\tAluminium Windows & Doors\tJINJA\tSite Ready\tPending\t79126350.31\t0\t79126350.31\tProspect\tN/A - Won/Active\t8/18/2026
146\tCAL-2026-5421\t7/17/2026\tSandra\tMr. Mirondo fred\t2.57E+11\tInstitutional\tOffice Partitions\tJinja\tNot Ready\tPending\t79126350.31\t0\t79126350.31\tProspect\tN/A - Won/Active\t8/18/2026
148\tCAL-2026-2925\t7/16/2026\tSandra\tMrs. Zephyr Balunywa\t2.57E+11\tCommercial\tAluminium Windows & Doors\tBusembatia\tNot Ready\tTaken\t2500000\t0\t2500000\tProspect\tN/A - Won/Active\t8/18/2026
150\tCAL-2026-0953\t7/13/2026\tSandra\tMr. Andrew Mara\t2.57E+11\tResidential\tAluminium Windows & Doors\tLuweero\tNot Ready\tPending\t42909976.2\t0\t42909976.2\tProspect\tN/A - Won/Active\t8/18/2026
149\tCAL-2026-2029\t7/13/2026\tSandra\tMr. Kiiza Nelson\t2.57E+11\tResidential\tAluminium Windows & Doors\tAkright\tSite Ready\tTaken\t46488050\t0\t46488050\tProspect\tN/A - Won/Active\t8/12/2026
151\tCAL-2026-4355\t7/4/2026\tSandra\tMR.KASUMBA\t2.57E+11\tResidential\tAluminium Windows & Doors\tMawokota\tNot Ready\tPending\t16027521.27\t0\t16027521.27\tProspect\tN/A - Won/Active\t8/18/2026
152\tCAL-2026-2336\t6/30/2026\tSandra\tOpus Design\t2.57E+11\tCommercial\tSteel Fabrication\tBulenga\tNot Ready\tPending\t21584600\t0\t21584600\tProspect\tN/A - Won/Active\t8/18/2026"""

# Load dataset into pandas and remove duplicate rows based on Code
df = pd.read_csv(io.StringIO(csv_data), sep='\t')
df = df.drop_duplicates(subset=['Code'])

# Connect to Supabase PostgreSQL using your settings
conn = psycopg2.connect(
    host="aws-1-eu-west-1.pooler.supabase.com",
    database="postgres",
    user="postgres.kmxaxdmoxpbfklhiiuqz",
    password="KU#7B6a.&McVg&P",
    port="5432"
)
cursor = conn.cursor()

# 1. Seed Users
users = [
    ('Anna', 'anna@casements.co.ug', 'Sales Executive'),
    ('Sandra', 'sandra@casements.co.ug', 'Sales Executive'),
    ('Joseph', 'joseph@casements.co.ug', 'Sales Executive'),
    ('Doreen', 'doreen@casements.co.ug', 'Sales Executive')
]
for u in users:
    cursor.execute("""
        INSERT INTO users (full_name, email, role) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (email) DO NOTHING;
    """, u)
conn.commit()

# 2. Insert Unique Clients
df['Clean_Client'] = df['Client Name'].astype(str).str.strip().str.upper()
clients_df = df.drop_duplicates(subset=['Clean_Client'])

for _, row in clients_df.iterrows():
    name = row['Clean_Client']
    phone = str(row['Contact Number']) if pd.notna(row['Contact Number']) else None
    district = str(row['Location']) if pd.notna(row['Location']) else None
    
    cursor.execute("""
        INSERT INTO clients (company_name, phone, district) 
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (name, phone, district))
conn.commit()

# 3. Fetch mappings cleanly
cursor.execute("SELECT user_id, full_name FROM users;")
user_map = {row[1].lower(): row[0] for row in cursor.fetchall()}

cursor.execute("SELECT client_id, company_name FROM clients;")
client_map = {row[1]: row[0] for row in cursor.fetchall()}

# 4. Insert Opportunities
for _, row in df.iterrows():
    sales_exec = str(row['Sales Exec']).strip().lower()
    client_name = str(row['Client Name']).strip().upper()
    
    user_id = user_map.get(sales_exec, 1)
    client_id = client_map.get(client_name)
    
    if not client_id:
        continue

    def clean_float(val):
        try:
            return float(val)
        except:
            return 0.0

    cursor.execute("""
        INSERT INTO opportunities (
            record_code, date_entered, sales_executive_id, client_id, 
            project_type, scope_of_work, site_location, site_status, 
            measurement_status, quotation_amount, amount_paid, 
            deal_status, reason_for_loss, next_followup_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (record_code) DO NOTHING;
    """, (
        str(row['Code']),
        str(row['Date']),
        user_id,
        client_id,
        str(row['Project']),
        str(row['Scope']),
        str(row['Location']) if pd.notna(row['Location']) else None,
        str(row['Site Status']) if pd.notna(row['Site Status']) else 'Pending',
        str(row['Meas. Status']) if pd.notna(row['Meas. Status']) else 'Pending',
        clean_float(row['Quotation (UGX)']),
        clean_float(row['Paid (UGX)']),
        str(row['Deal Status']),
        str(row['Reason for Loss']) if pd.notna(row['Reason for Loss']) else 'N/A - Won/Active',
        str(row['Next Follow-Up']) if pd.notna(row['Next Follow-Up']) and str(row['Next Follow-Up']).strip() != '' else None
    ))

conn.commit()
cursor.close()
conn.close()

print("Data successfully cleaned, duplicates removed, and loaded into Supabase PostgreSQL!")