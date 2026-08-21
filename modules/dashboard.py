from pathlib import Path

code = r'''import streamlit as st
import pandas as pd
from database.db import run_query


def render_dashboard():
    """Render the Executive Management Dashboard."""

    st.header("📈 Executive Management Dashboard")

    # ============================================================
    # DYNAMIC MONTH SELECTION
    # ============================================================

    months_query = """
        SELECT DISTINCT
            TO_CHAR(date_entered, 'YYYY-MM') AS month_val
        FROM opportunities
        WHERE date_entered IS NOT NULL
        ORDER BY month_val DESC;
    """

    try:
        df_months = run_query(months_query)

        if (
            not df_months.empty
            and "month_val" in df_months.columns
        ):
            available_months = (
                df_months["month_val"]
                .dropna()
                .astype(str)
                .tolist()
            )
        else:
            available_months = []

    except Exception as e:
        st.warning(f"Unable to load available months: {e}")
        available_months = []

    month_options = ["All Time"] + available_months

    selected_month = st.selectbox(
        "📅 Filter Performance by Month",
        month_options,
        index=0,
    )

    # ============================================================
    # EXECUTIVE SUMMARY METRICS
    # ============================================================

    if selected_month == "All Time":
        metrics_query = """
            SELECT
                COUNT(opportunity_id) AS total_deals,
                COALESCE(SUM(quotation_amount), 0) AS total_quoted,
                COALESCE(SUM(amount_paid), 0) AS total_collected,
                COALESCE(
                    SUM(
                        CASE
                            WHEN deal_status = 'Success (Order Won)'
                            THEN quotation_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_revenue_won,
                COALESCE(
                    SUM(quotation_amount - amount_paid),
                    0
                ) AS total_outstanding
            FROM opportunities;
        """

        metrics_params = ()

    else:
        metrics_query = """
            SELECT
                COUNT(opportunity_id) AS total_deals,
                COALESCE(SUM(quotation_amount), 0) AS total_quoted,
                COALESCE(SUM(amount_paid), 0) AS total_collected,
                COALESCE(
                    SUM(
                        CASE
                            WHEN deal_status = 'Success (Order Won)'
                            THEN quotation_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_revenue_won,
                COALESCE(
                    SUM(quotation_amount - amount_paid),
                    0
                ) AS total_outstanding
            FROM opportunities
            WHERE TO_CHAR(date_entered, 'YYYY-MM') = %s;
        """

        metrics_params = (selected_month,)

    df_metrics = run_query(
        metrics_query,
        metrics_params,
    )

    # Safely extract metric values
    if df_metrics.empty:
        total_deals = 0
        total_quoted = 0.0
        total_collected = 0.0
        total_revenue_won = 0.0
        total_outstanding = 0.0
    else:
        row = df_metrics.iloc[0]

        total_deals = int(
            row.get("total_deals", 0) or 0
        )
        total_quoted = float(
            row.get("total_quoted", 0) or 0
        )
        total_collected = float(
            row.get("total_collected", 0) or 0
        )
        total_revenue_won = float(
            row.get("total_revenue_won", 0) or 0
        )
        total_outstanding = float(
            row.get("total_outstanding", 0) or 0
        )

    # ============================================================
    # EXECUTIVE SUMMARY DISPLAY
    # ============================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Deals Logged",
        f"{total_deals:,}",
    )

    col2.metric(
        "Total Quoted (UGX)",
        f"{total_quoted:,.0f}",
    )

    col3.metric(
        "Total Revenue Won (UGX)",
        f"{total_revenue_won:,.0f}",
    )

    col4.metric(
        "Outstanding Collection (UGX)",
        f"{total_outstanding:,.0f}",
    )

    st.markdown("---")

    # ============================================================
    # SALES EXECUTIVE LEADERBOARD
    # ============================================================

    st.subheader(
        f"🏆 Sales Executive Leaderboard ({selected_month})"
    )

    if selected_month == "All Time":
        leaderboard_query = """
            SELECT
                u.full_name AS "Sales Executive",
                COUNT(o.opportunity_id) AS "Total Deals",
                COALESCE(
                    SUM(o.quotation_amount),
                    0
                ) AS "Quoted Value (UGX)",
                COALESCE(
                    SUM(
                        CASE
                            WHEN o.deal_status = 'Success (Order Won)'
                            THEN o.quotation_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS "Revenue Won (UGX)",
                COALESCE(
                    SUM(o.amount_paid),
                    0
                ) AS "Collections (UGX)"
            FROM users u
            LEFT JOIN opportunities o
                ON u.user_id = o.sales_executive_id
            WHERE u.role IN (
                'Sales Executive',
                'General Manager'
            )
            GROUP BY
                u.user_id,
                u.full_name
            ORDER BY
                COALESCE(
                    SUM(
                        CASE
                            WHEN o.deal_status = 'Success (Order Won)'
                            THEN o.quotation_amount
                            ELSE 0
                        END
                    ),
                    0
                ) DESC,
                COUNT(o.opportunity_id) DESC;
        """

        leaderboard_params = ()

    else:
        leaderboard_query = """
            SELECT
                u.full_name AS "Sales Executive",
                COUNT(o.opportunity_id) AS "Total Deals",
                COALESCE(
                    SUM(o.quotation_amount),
                    0
                ) AS "Quoted Value (UGX)",
                COALESCE(
                    SUM(
                        CASE
                            WHEN o.deal_status = 'Success (Order Won)'
                            THEN o.quotation_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS "Revenue Won (UGX)",
                COALESCE(
                    SUM(o.amount_paid),
                    0
                ) AS "Collections (UGX)"
            FROM users u
            LEFT JOIN opportunities o
                ON u.user_id = o.sales_executive_id
                AND TO_CHAR(
                    o.date_entered,
                    'YYYY-MM'
                ) = %s
            WHERE u.role IN (
                'Sales Executive',
                'General Manager'
            )
            GROUP BY
                u.user_id,
                u.full_name
            ORDER BY
                COALESCE(
                    SUM(
                        CASE
                            WHEN o.deal_status = 'Success (Order Won)'
                            THEN o.quotation_amount
                            ELSE 0
                        END
                    ),
                    0
                ) DESC,
                COUNT(o.opportunity_id) DESC;
        """

        leaderboard_params = (selected_month,)

    df_leaderboard = run_query(
        leaderboard_query,
        leaderboard_params,
    )

    # ============================================================
    # LEADERBOARD DISPLAY
    # ============================================================

    if df_leaderboard.empty:
        st.info(
            f"No sales performance data available for {selected_month}."
        )
        return

    # Format numeric columns for presentation
    currency_columns = [
        "Quoted Value (UGX)",
        "Revenue Won (UGX)",
        "Collections (UGX)",
    ]

    for column in currency_columns:
        if column in df_leaderboard.columns:
            df_leaderboard[column] = (
                pd.to_numeric(
                    df_leaderboard[column],
                    errors="coerce",
                )
                .fillna(0)
                .map(lambda value: f"{value:,.0f}")
            )

    if "Total Deals" in df_leaderboard.columns:
        df_leaderboard["Total Deals"] = (
            pd.to_numeric(
                df_leaderboard["Total Deals"],
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
        )

    st.dataframe(
        df_leaderboard,
        use_container_width=True,
        hide_index=True,
    )
'''

path = Path("/mnt/data/dashboard.py")
path.write_text(code, encoding="utf-8")

print(f"Created: {path}")
