import streamlit as st


def apply_custom_style():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0b1220 0%, #111827 100%);
        color: #f9fafb;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .hero-box {
        background: linear-gradient(135deg, #1d4ed8 0%, #7c3aed 100%);
        border-radius: 22px;
        padding: 28px 32px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        margin-bottom: 24px;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        color: white;
        line-height: 1.15;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: rgba(255,255,255,0.92);
        margin-bottom: 0;
    }

    .section-title {
        font-size: 30px;
        font-weight: 800;
        color: #f9fafb;
        margin-top: 8px;
        margin-bottom: 16px;
        padding-left: 14px;
        border-left: 6px solid #60a5fa;
    }

    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18);
        min-height: 125px;
    }

    .metric-label {
        font-size: 14px;
        color: #cbd5e1;
        margin-bottom: 10px;
        font-weight: 600;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .metric-note {
        font-size: 13px;
        color: #94a3b8;
    }

    .metric-high {
        border-left: 5px solid #ef4444;
    }

    .metric-medium {
        border-left: 5px solid #f59e0b;
    }

    .metric-low {
        border-left: 5px solid #22c55e;
    }

    .metric-main {
        border-left: 5px solid #60a5fa;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        overflow: hidden;
    }

    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin-top: 24px;
        margin-bottom: 24px;
    }

.chart-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 18px 20px 10px 20px;
    margin-top: 10px;
    margin-bottom: 10px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.16);
}

.chart-title {
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 6px;
}

.chart-subtitle {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 6px;
}

    </style>
    """, unsafe_allow_html=True)
