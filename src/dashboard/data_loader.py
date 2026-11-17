from pathlib import Path
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "dashboard"
    / "final_predictions.csv"
)


@st.cache_data(show_spinner="Đang tải dữ liệu dự đoán...")
def load_predictions():
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["timestamp"]
    )

    df["sensor_id"] = df["sensor_id"].astype(str)

    return df