import streamlit as st
import pandas as pd
import datetime
from database.db import run_query, execute_commit
from ui.theme import render_header

def render_kpi_card(title, value, target, status_color="#2563EB", icon="📢"):
    """Helper for PRO dashboard KPI cards."""
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(229, 231, 235, 0.2);
        border-left: 5px solid {status_color};
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #6B7280;">
            {icon} {title}
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; margin: 4px 0; color: #1F2937;">
            {value}
        </div>
        <div style="font-size: 0.75rem; font-weight: 500; color: #4B5563;">
            Monthly Target: <b>{target}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_pro_dashboard():
    render_header(
        title="📣 Public Relations Officer (PRO) Performance Dashboard", 
        subtitle="Brand Visibility, Digital Marketing Reach & Lead Revenue Attribution"
    )

    pro_menu = st.sidebar.radio(
        "PRO Dashboard Views",
        [
            "🏆 Overall Scorecard & Executive View",
            "📱 Digital Marketing & Reach",
            "💰 Lead Source & Revenue Attribution",
            "📝 Input & Update PRO Metrics",
            "📜 Historical Logs & Performance Audit"
        ]
    )

    # Fetch Base Sales/Opportunities Data
    try:
        df_opps = run_query("""
            SELECT 
                opportunity_id, lead_source, quotation_amount, amount_paid, 
                deal_status, site_status, date_entered
            FROM opportunities
        """)
    except Exception:
        df_opps = pd.DataFrame()

    # Fetch Latest PRO Log Data
    try:
        df_pro_logs = run_query("SELECT * FROM pro_kpi_logs ORDER BY log_id DESC LIMIT 1")
    except Exception:
        df_pro_logs = pd.DataFrame()

    latest_log = df_pro_logs.iloc[0] if not df_pro_logs.empty else {}

    # Extract dynamic figures from sales database
    total_enquiries = len(df_opps) if not df_opps.empty else 0
    orders_won = len(df_opps[df_opps['deal_status'] == 'Success (Order Won)']) if not df_opps.empty else 0
    total_revenue = df_opps['amount_paid'].sum() if not df_opps.empty else 0.0

    # ==========================================
    # VIEW 1: OVERALL SCORECARD & EXECUTIVE VIEW
    # ==========================================
    if pro_menu == "🏆 Overall Scorecard & Executive View":
        st.markdown("### 🏆 Overall Monthly PRO Scorecard (Weighted)")
        st.caption("Quantifiable score calculated across the key performance pillars.")

        # Calculated Scores against Targets
        corp_image_score = min(100.0, ((latest_log.get('pr_campaigns', 0) / 4) + (latest_log.get('press_releases', 0) / 2)) / 2 * 100)
        digital_score = min(100.0, ((latest_log.get('tiktok_posts', 0) / 40) + (latest_log.get('facebook_posts', 0) / 30) + (latest_log.get('instagram_posts', 0) / 30)) / 3 * 100)
        lead_gen_score = min(100.0, (total_enquiries / 200) * 100)
        sales_conv_score = min(100.0, (orders_won / 24) * 100)
        revenue_score = min(100.0, (total_revenue / 200000000) * 100)
        csat_score = min(100.0, (latest_log.get('csat_rating', 95.0) / 95.0) * 100)

        # Weighted calculation
        total_weighted_score = (
            (corp_image_score * 0.20) +
            (digital_score * 0.25) +
            (lead_gen_score * 0.20) +
            (sales_conv_score * 0.15) +
            (revenue_score * 0.15) +
            (csat_score * 0.05)
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Total PRO Score", f"{total_weighted_score:.1f}%", "100%", "#059669" if total_weighted_score >= 80 else "#D97706", "🏅")
        with c2:
            render_kpi_card("Marketing Revenue", f"UGX {total_revenue:,.0f}", "UGX 200M", "#2563EB", "💵")
        with c3:
            render_kpi_card("Total Enquiries", f"{total_enquiries}", "200 Leads", "#7C3AED", "📥")
        with c4:
            render_kpi_card("Orders Closed", f"{orders_won}", "24 Orders", "#059669", "📦")

        st.divider()

        st.markdown("#### 📊 Scorecard Pillar Breakdown")
        scorecard_data = pd.DataFrame([
            {"Pillar": "Corporate Image & Brand Visibility", "Weight": "20%", "Target": "100%", "Achieved Score": f"{corp_image_score:.1f}%", "Weighted Contribution": f"{corp_image_score * 0.20:.1f}%"},
            {"Pillar": "Digital Marketing Performance", "Weight": "25%", "Target": "100%", "Achieved Score": f"{digital_score:.1f}%", "Weighted Contribution": f"{digital_score * 0.25:.1f}%"},
            {"Pillar": "Lead Generation", "Weight": "20%", "Target": "200 Leads", "Achieved Score": f"{lead_gen_score:.1f}%", "Weighted Contribution": f"{lead_gen_score * 0.20:.1f}%"},
            {"Pillar": "Sales Conversion", "Weight": "15%", "Target": "24 Orders", "Achieved Score": f"{sales_conv_score:.1f}%", "Weighted Contribution": f"{sales_conv_score * 0.15:.1f}%"},
            {"Pillar": "Revenue Generated", "Weight": "15%", "Target": "UGX 200M", "Achieved Score": f"{revenue_score:.1f}%", "Weighted Contribution": f"{revenue_score * 0.15:.1f}%"},
            {"Pillar": "Customer Satisfaction", "Weight": "5%", "Target": "≥95%", "Achieved Score": f"{csat_score:.1f}%", "Weighted Contribution": f"{csat_score * 0.05:.1f}%"},
        ])
        st.table(scorecard_data)

    # ==========================================
    # VIEW 2: DIGITAL MARKETING & REACH
    # ==========================================
    elif pro_menu == "📱 Digital Marketing & Reach":
        st.markdown("### 📱 Social Media & Digital Marketing Tracking")
        st.caption("Monitoring publication volume, impressions, engagement, and traffic across all platforms.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 🎵 TikTok & Facebook")
            st.metric("TikTok Videos", f"{latest_log.get('tiktok_posts', 0)} / 40 Target")
            st.metric("Avg TikTok Views", f"{latest_log.get('tiktok_views', 0):,}", delta="Target: 5,000")
            st.metric("FB Engagement", f"{latest_log.get('facebook_engagement', 0):,}", delta="Target: 8,000")

        with col2:
            st.markdown("#### 📸 Instagram & X (Twitter)")
            st.metric("IG Followers Growth", f"+{latest_log.get('instagram_follower_growth', 0)}", delta="Target: +500")
            st.metric("X Impressions", f"{latest_log.get('x_impressions', 0):,}", delta="Target: 60,000")
            st.metric("X Engagement Rate", f"{latest_log.get('x_engagement_rate', 0.0):.1f}%", delta="Target: 5.0%")

        with col3:
            st.markdown("#### 🌐 Web & WhatsApp")
            st.metric("Website Visitors", f"{latest_log.get('website_visitors', 0):,}", delta="Target: 5,000")
            st.metric("Website Updates", f"{latest_log.get('website_updates', 0)} / 8 Target")
            st.metric("WhatsApp Enquiries", f"{latest_log.get('whatsapp_enquiries', 0)}", delta="Target: 250")

    # ==========================================
    # VIEW 3: LEAD SOURCE & REVENUE ATTRIBUTION
    # ==========================================
    elif pro_menu == "💰 Lead Source & Revenue Attribution":
        st.markdown("### 💰 Lead Source Revenue Attribution")
        st.caption("Directly linking marketing and PR channels to generated revenue.")

        # --- Section 1: Lead Source Analytics Display ---
        if not df_opps.empty and 'lead_source' in df_opps.columns:
            source_summary = df_opps.groupby('lead_source').agg(
                Enquiries=('opportunity_id', 'count'),
                Revenue_UGX=('amount_paid', 'sum')
            ).reset_index()

            source_summary['% Revenue Contribution'] = (
                source_summary['Revenue_UGX'] / (total_revenue if total_revenue > 0 else 1)
            ) * 100
            source_summary = source_summary.sort_values(by='Revenue_UGX', ascending=False)

            st.dataframe(
                source_summary.style.format({
                    "Revenue_UGX": "UGX {:,.0f}",
                    "% Revenue Contribution": "{:.1f}%"
                }),
                use_container_width=True
            )

            st.divider()
            st.markdown("#### 💵 Generated Revenue by Channel")
            st.bar_chart(source_summary.set_index('lead_source')['Revenue_UGX'])
        else:
            st.info("No lead attribution data logged yet. Use the entry form below to log a new lead/order.")

        st.divider()

        # --- Section 2: Direct Entry Form for Lead Source Data ---
        st.markdown("### ➕ Add New Lead & Revenue Attribution Entry")
        st.caption("Record a new customer enquiry or deal with its originating marketing channel.")

        with st.form("lead_attribution_entry_form"):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.text_input("Client / Project Name", placeholder="e.g. Acme Towers Aluminum Work")
                lead_source = st.selectbox(
                    "Marketing Channel (Lead Source)",
                    [
                        "TikTok Video",
                        "Facebook Campaign",
                        "Instagram",
                        "X (Twitter)",
                        "Website Inquiry Form",
                        "WhatsApp Business",
                        "Press Release / PR",
                        "Direct Walk-in / Showroom",
                        "Referral / Word of Mouth"
                    ]
                )
                quotation_amount = st.number_input("Quotation Amount (UGX)", min_value=0.0, step=100000.0)

            with c2:
                deal_status = st.selectbox(
                    "Deal Status",
                    [
                        "New Enquiry",
                        "Under Negotiation",
                        "Quotation Issued",
                        "Success (Order Won)",
                        "Closed / Lost"
                    ]
                )
                amount_paid = st.number_input("Amount Paid / Collected (UGX)", min_value=0.0, step=100000.0)
                date_entered = st.date_input("Entry Date", datetime.date.today())

            submit_lead = st.form_submit_button("💾 Save Lead Attribution Record")

            if submit_lead:
                if not client_name.strip():
                    st.error("Please enter a Client / Project Name.")
                else:
                    sql_insert_opp = """
                        INSERT INTO opportunities 
                        (client_name, lead_source, quotation_amount, amount_paid, deal_status, date_entered)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    execute_commit(sql_insert_opp, (
                        client_name, lead_source, quotation_amount, amount_paid, deal_status, str(date_entered)
                    ))
                    st.success(f"Successfully recorded lead for '{client_name}' via {lead_source}!")
                    st.rerun()

    # ==========================================
    # VIEW 4: INPUT & UPDATE PRO METRICS
    # ==========================================
    elif pro_menu == "📝 Input & Update PRO Metrics":
        st.markdown("### 📝 Enter PRO Monthly Analytics & Performance Data")
        st.caption("Fill out the monthly metrics across corporate image, digital platforms, and customer SLAs.")

        with st.form("pro_kpi_full_form"):
            log_month = st.text_input("Log Period (YYYY-MM)", datetime.date.today().strftime("%Y-%m"))

            st.markdown("---")
            st.subheader("A. Corporate Image & Brand Visibility")
            c1, c2 = st.columns(2)
            with c1:
                pr_campaigns = st.number_input("PR Campaigns Executed (Target: 4)", min_value=0, value=int(latest_log.get('pr_campaigns', 4)))
                press_releases = st.number_input("Press Releases Published (Target: 2)", min_value=0, value=int(latest_log.get('press_releases', 2)))
                project_showcases = st.number_input("Project Showcases Posted (Target: 8)", min_value=0, value=int(latest_log.get('project_showcases', 8)))
            with c2:
                testimonials = st.number_input("Testimonials Obtained (Target: 10)", min_value=0, value=int(latest_log.get('testimonials_obtained', 10)))
                brand_compliance = st.number_input("Brand Compliance % (Target: 100%)", min_value=0.0, max_value=100.0, value=float(latest_log.get('brand_compliance_pct', 100.0)))
                reputation_resolved = st.number_input("Reputation Issues Resolved %", min_value=0.0, max_value=100.0, value=float(latest_log.get('reputation_issues_resolved_pct', 100.0)))

            st.markdown("---")
            st.subheader("B. Digital Marketing Performance")
            d1, d2, d3 = st.columns(3)
            with d1:
                tiktok_posts = st.number_input("TikTok Videos (Target: 40)", min_value=0, value=int(latest_log.get('tiktok_posts', 40)))
                tiktok_views = st.number_input("Avg TikTok Views (Target: 5000)", min_value=0, value=int(latest_log.get('tiktok_views', 5000)))
                fb_posts = st.number_input("Facebook Posts (Target: 30)", min_value=0, value=int(latest_log.get('facebook_posts', 30)))
                fb_engagement = st.number_input("FB Engagement (Target: 8000)", min_value=0, value=int(latest_log.get('facebook_engagement', 8000)))

            with d2:
                ig_posts = st.number_input("Instagram Posts (Target: 30)", min_value=0, value=int(latest_log.get('instagram_posts', 30)))
                ig_growth = st.number_input("IG Follower Growth (Target: 500)", min_value=0, value=int(latest_log.get('instagram_follower_growth', 500)))
                linkedin_posts = st.number_input("LinkedIn Posts (Target: 12)", min_value=0, value=int(latest_log.get('linkedin_posts', 12)))
                x_posts = st.number_input("X (Twitter) Posts (Target: 40)", min_value=0, value=int(latest_log.get('x_posts', 40)))

            with d3:
                x_impressions = st.number_input("X Impressions (Target: 60,000)", min_value=0, value=int(latest_log.get('x_impressions', 60000)))
                x_eng_rate = st.number_input("X Engagement Rate % (Target: 5%)", min_value=0.0, max_value=100.0, value=float(latest_log.get('x_engagement_rate', 5.0)))
                x_growth = st.number_input("X Follower Growth (Target: 300)", min_value=0, value=int(latest_log.get('x_followers_growth', 300)))
                web_updates = st.number_input("Website Updates (Target: 8)", min_value=0, value=int(latest_log.get('website_updates', 8)))
                web_visitors = st.number_input("Website Visitors (Target: 5000)", min_value=0, value=int(latest_log.get('website_visitors', 5000)))
                wa_enquiries = st.number_input("WhatsApp Enquiries (Target: 250)", min_value=0, value=int(latest_log.get('whatsapp_enquiries', 250)))

            st.markdown("---")
            st.subheader("C. Customer Satisfaction & SLAs")
            s1, s2 = st.columns(2)
            with s1:
                csat_rating = st.number_input("CSAT Rating % (Target: ≥95%)", min_value=0.0, max_value=100.0, value=float(latest_log.get('csat_rating', 95.0)))
            with s2:
                complaints_resolved = st.number_input("Complaints Resolved in 48h %", min_value=0.0, max_value=100.0, value=float(latest_log.get('complaints_resolved_pct', 100.0)))

            submit_pro = st.form_submit_button("💾 Save & Commit PRO Performance Log")

            if submit_pro:
                sql_insert = """
                    INSERT INTO pro_kpi_logs 
                    (log_month, pr_campaigns, press_releases, project_showcases, testimonials_obtained,
                     brand_compliance_pct, reputation_issues_resolved_pct, tiktok_posts, tiktok_views,
                     facebook_posts, facebook_engagement, instagram_posts, instagram_follower_growth,
                     linkedin_posts, x_posts, x_impressions, x_engagement_rate, x_followers_growth,
                     website_updates, website_visitors, whatsapp_enquiries, csat_rating, complaints_resolved_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                execute_commit(sql_insert, (
                    log_month, pr_campaigns, press_releases, project_showcases, testimonials,
                    brand_compliance, reputation_resolved, tiktok_posts, tiktok_views,
                    fb_posts, fb_engagement, ig_posts, ig_growth,
                    linkedin_posts, x_posts, x_impressions, x_eng_rate, x_growth,
                    web_updates, web_visitors, wa_enquiries, csat_rating, complaints_resolved
                ))
                st.success(f"PRO Performance metrics for {log_month} saved successfully!")
                st.rerun()

    # ==========================================
    # VIEW 5: HISTORICAL LOGS & PERFORMANCE AUDIT
    # ==========================================
    elif pro_menu == "📜 Historical Logs & Performance Audit":
        st.markdown("### 📜 Historical PRO KPI Logs & Trends")
        st.caption("Review past monthly entries, perform audits, and track long-term growth across all channels.")

        try:
            df_all_logs = run_query("SELECT * FROM pro_kpi_logs ORDER BY log_id DESC")
        except Exception:
            df_all_logs = pd.DataFrame()

        if not df_all_logs.empty:
            st.dataframe(df_all_logs, use_container_width=True)

            st.divider()
            st.markdown("#### 📈 Multi-Month Channel Reach Trends")
            
            # Simple Trend Chart Selection
            if 'log_month' in df_all_logs.columns:
                df_chart = df_all_logs.sort_values(by='log_id', ascending=True)
                metric_to_chart = st.selectbox(
                    "Select Metric to Visualize Trend",
                    ["tiktok_views", "facebook_engagement", "x_impressions", "website_visitors", "whatsapp_enquiries", "csat_rating"]
                )
                st.line_chart(df_chart.set_index('log_month')[metric_to_chart])

            st.divider()

            # Export Capability
            csv_data = df_all_logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export All PRO KPI Logs (CSV)",
                data=csv_data,
                file_name="pro_kpi_logs_export.csv",
                mime="text/csv"
            )
        else:
            st.info("No historical logs found in database.")