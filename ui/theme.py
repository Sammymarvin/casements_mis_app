# ui/theme.py
import streamlit as st

def apply_custom_ui():
    """Injects custom CSS styling into the Streamlit app for a sleek, modern UI."""
    st.set_page_config(
        page_title="Casements Africa | MIS Portal",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    custom_css = """
    <style>
        /* Import Clean Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Top Header Styling */
        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 24px;
            border-radius: 12px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 {
            color: #FFFFFF !important;
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }
        .main-header p {
            color: #E0E7FF;
            margin: 5px 0 0 0;
            font-size: 14px;
        }

        /* Executive Metric Cards */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        .metric-label {
            font-size: 13px;
            font-weight: 600;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 22px;
            font-weight: 700;
            color: #111827;
            margin-top: 6px;
        }

        /* Enhanced Form Container */
        div[data-testid="stForm"] {
            background-color: #FAFAFA;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 24px;
        }

        /* Primary Button Styling */
        .stButton>button[kind="primary"] {
            background-color: #2563EB;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            border: none;
            box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #1D4ED8;
        }

        /* Table Styling Overrides */
        div[data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #E5E7EB;
        }
    </style>
    """
    # Fixed syntax below:
    st.markdown(custom_css, unsafe_allow_html=True)

def render_header(title, subtitle=""):
    """Displays a custom top banner header across modules."""
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )