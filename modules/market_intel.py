import streamlit as st
import pandas as pd
import datetime
from database.db import run_query, execute_commit
from ui.theme import render_header

def render_metric_card(title, value, subtitle="", status_color="#2563EB", icon="🧠"):
    """Helper to render modern styled KPI cards."""
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(229, 231, 235, 0.2);
        border-left: 5px solid {status_color};
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <div style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; color: #6B7280; letter-spacing: 0.5px;">
            {icon} {title}
        </div>
        <div style="font-size: 1.6rem; font-weight: 700; margin: 6px 0; color: #1F2937;">
            {value}
        </div>
        <div style="font-size: 0.8rem; font-weight: 500; color: {status_color};">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_market_intelligence():
    render_header(
        title="🧠 Market Intelligence Hub", 
        subtitle="Competitor Benchmarking, Pricing Analysis & Customer Sentiment Tracking"
    )

    # Sidebar Sub-Navigation
    menu = st.sidebar.radio(
        "Intelligence Views",
        [
            "📊 Executive Market Insights",
            "🏷️ Competitor Benchmarking",
            "💬 Client Sentiment & Feedback",
            "➕ Record Intelligence Data"
        ]
    )

    # Fetch Competitor Data
    try:
        df_comp = run_query("SELECT * FROM competitor_intelligence ORDER BY intel_id DESC")
    except Exception:
        df_comp = pd.DataFrame()

    # Fetch Feedback Data
    try:
        query_feedback = """
            SELECT 
                cf.feedback_id,
                c.company_name AS [Client],
                cf.satisfaction_score AS [CSAT Score],
                cf.pricing_perception AS [Price Perception],
                cf.quality_rating AS [Quality Rating],
                cf.feedback_comments AS [Comments],
                cf.feedback_date AS [Date]
            FROM customer_feedback cf
            LEFT JOIN clients c ON cf.client_id = c.client_id
            ORDER BY cf.feedback_id DESC
        """
        df_feedback = run_query(query_feedback)
    except Exception:
        df_feedback = pd.DataFrame()

    # ==========================================
    # VIEW 1: EXECUTIVE MARKET INSIGHTS
    # ==========================================
    if menu == "📊 Executive Market Insights":
        st.markdown("### 📊 Market Intelligence Summary")
        st.caption("Strategic positioning overview against competitors in the Uganda building materials sector.")

        avg_csat = df_feedback['CSAT Score'].mean() if not df_feedback.empty else 0.0
        comp_count = len(df_comp['competitor_name'].unique()) if not df_comp.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Monitored Competitors", f"{comp_count}", "Active Market Competitors", "#2563EB", "🏢")
        with c2:
            render_metric_card("Avg Customer CSAT", f"{avg_csat:.1f} / 5.0", "Client Satisfaction Score", "#059669" if avg_csat >= 4.0 else "#D97706", "⭐")
        with c3:
            render_metric_card("Competitor Entries", f"{len(df_comp)}", "Benchmark Logs Recorded", "#7C3AED", "📑")
        with c4:
            render_metric_card("Feedback Logs", f"{len(df_feedback)}", "Client Reviews Collected", "#D97706", "💬")

        st.divider()

        st.markdown("#### 🎯 Strategic Price Perception Breakdown")
        if not df_feedback.empty and 'Price Perception' in df_feedback.columns:
            st.bar_chart(df_feedback['Price Perception'].value_counts())
        else:
            st.info("No customer pricing sentiment data recorded yet.")

    # ==========================================
    # VIEW 2: COMPETITOR BENCHMARKING
    # ==========================================
    elif menu == "🏷️ Competitor Benchmarking":
        st.markdown("### 🏷️ Competitor Pricing & Rate Benchmarking")
        st.caption("Comparing estimated market rates per SQM across Aluminium, Steel & Glass.")

        if df_comp.empty:
            st.info("No competitor pricing data logged yet. Add logs using the 'Record Intelligence Data' tab.")
        else:
            st.dataframe(
                df_comp[['competitor_name', 'product_scope', 'estimated_sqm_rate', 'win_rate_impact', 'perceived_quality', 'notes']],
                use_container_width=True
            )

            st.divider()
            st.markdown("#### 💵 Estimated SQM Rate Comparison by Product Scope")
            chart_df = df_comp.groupby(['competitor_name', 'product_scope'])['estimated_sqm_rate'].mean().unstack().fillna(0)
            st.bar_chart(chart_df)

    # ==========================================
    # VIEW 3: CLIENT SENTIMENT & FEEDBACK
    # ==========================================
    elif menu == "💬 Client Sentiment & Feedback":
        st.markdown("### 💬 Client Experience & Sentiment Logs")
        st.caption("Tracking client satisfaction, quality ratings, and raw feedback notes.")

        if df_feedback.empty:
            st.info("No customer feedback records found.")
        else:
            st.dataframe(df_feedback, use_container_width=True)

    # ==========================================
    # VIEW 4: RECORD INTELLIGENCE DATA
    # ==========================================
    elif menu == "➕ Record Intelligence Data":
        st.markdown("### ➕ Add Market Intelligence or Client Feedback")

        tab1, tab2 = st.tabs(["🏷️ Add Competitor Rate", "💬 Add Customer Feedback"])

        with tab1:
            st.markdown("#### Record Competitor Pricing / Intel")
            with st.form("add_comp_form"):
                comp_name = st.text_input("Competitor Name (e.g., Roofings, Uganda Baati, Local Fabricators)")
                scope = st.selectbox("Product Scope", ["Aluminium Windows & Doors", "Curtain Walls", "Toughened Glass", "Steel Fabrication", "Office Partitions"])
                sqm_rate = st.number_input("Estimated SQM Rate (UGX)", min_value=0.0, step=5000.0)
                impact = st.selectbox("Market Threat / Impact", ["High Threat", "Medium Threat", "Low Threat"])
                quality = st.selectbox("Perceived Quality Level", ["Premium Quality", "Standard Quality", "Low Budget / Inferior"])
                notes = st.text_area("Market Insights / Notes")

                submit_comp = st.form_submit_button("💾 Save Competitor Entry")
                if submit_comp:
                    if comp_name:
                        sql = """
                            INSERT INTO competitor_intelligence 
                            (competitor_name, product_scope, estimated_sqm_rate, win_rate_impact, perceived_quality, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """
                        execute_commit(sql, (comp_name, scope, sqm_rate, impact, quality, notes))
                        st.success(f"Competitor intelligence logged for {comp_name}!")
                        st.rerun()
                    else:
                        st.error("Please provide a competitor name.")

        with tab2:
            st.markdown("#### Record Customer Feedback")
            clients_df = run_query("SELECT client_id, company_name FROM clients")
            
            with st.form("add_feedback_form"):
                if not clients_df.empty:
                    client_map = dict(zip(clients_df['company_name'], clients_df['client_id']))
                    selected_client_name = st.selectbox("Select Client", list(client_map.keys()))
                else:
                    selected_client_name = None
                    st.warning("No clients registered in system. Add clients via Master Entry first.")

                csat = st.slider("Satisfaction Rating (1 = Poor, 5 = Excellent)", 1, 5, 4)
                price_perception = st.selectbox("Pricing Perception", ["Very Expensive", "Slightly High", "Fair / Competitive", "Very Affordable"])
                quality_rating = st.selectbox("Product & Fitting Quality", ["Exceeds Expectations", "Meets Expectations", "Below Expectations"])
                comments = st.text_area("Client Feedback Remarks")

                submit_fb = st.form_submit_button("💾 Save Customer Feedback")
                if submit_fb and selected_client_name:
                    c_id = client_map[selected_client_name]
                    sql_fb = """
                        INSERT INTO customer_feedback 
                        (client_id, satisfaction_score, pricing_perception, quality_rating, feedback_comments)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    execute_commit(sql_fb, (c_id, csat, price_perception, quality_rating, comments))
                    st.success("Customer feedback saved successfully!")
                    st.rerun()