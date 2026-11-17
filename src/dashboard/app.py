from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_predictions
from ui_style import apply_custom_style


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Traffic Congestion Dashboard",
    page_icon="🚦",
    layout="wide"
)

apply_custom_style()


# =========================================================
# HERO HEADER
# =========================================================

hero_html = (
    '<div class="hero-box">'
    '<div class="hero-badge">🚦 Traffic Analytics • Random Forest</div>'
    '<div class="hero-title">DỰ ĐOÁN ÙN TẮC GIAO THÔNG</div>'
    '<div style="color:rgba(255,255,255,0.96);font-size:20px;'
    'font-weight:650;margin-top:6px;margin-bottom:12px;">'
    'Traffic Congestion Prediction Dashboard'
    '</div>'
    '<div class="hero-subtitle">'
    'Phân tích dữ liệu giao thông METR-LA và dự đoán '
    'mức độ ùn tắc trước 15 phút bằng mô hình Random Forest.'
    '</div>'
    '</div>'
)

st.markdown(
    hero_html,
    unsafe_allow_html=True
)

# =========================================================
# LOAD DATA
# =========================================================

df = load_predictions()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## 🎛️ Bộ lọc")
st.sidebar.caption(
    "Tùy chỉnh dữ liệu hiển thị trên dashboard."
)

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "📅 Khoảng thời gian",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

sensor_list = sorted(
    df["sensor_id"].astype(str).unique()
)

selected_sensor = st.sidebar.selectbox(
    "📡 Sensor",
    ["Tất cả"] + sensor_list
)

congestion_filter = st.sidebar.multiselect(
    "🚦 Mức ùn tắc dự đoán",
    ["HIGH", "MEDIUM", "LOW"],
    default=["HIGH", "MEDIUM", "LOW"]
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["timestamp"].dt.date >= start_date)
        &
        (filtered_df["timestamp"].dt.date <= end_date)
    ]

if selected_sensor != "Tất cả":
    filtered_df = filtered_df[
        filtered_df["sensor_id"].astype(str)
        == selected_sensor
    ]

filtered_df = filtered_df[
    filtered_df["predicted_congestion_15m"]
    .isin(congestion_filter)
]


# =========================================================
# SUMMARY CONTEXT
# =========================================================

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = min_date
    end_date = max_date

sensor_display = (
    "Tất cả sensor"
    if selected_sensor == "Tất cả"
    else f"Sensor {selected_sensor}"
)

info_col1, info_col2 = st.columns([1, 2])

with info_col1:
    st.info(
        f"📡 **Sensor đang xem:** {sensor_display}"
    )

with info_col2:
    st.info(
        "📅 **Khoảng thời gian:** "
        f"{start_date.strftime('%d/%m/%Y')} "
        f"→ {end_date.strftime('%d/%m/%Y')}"
    )


# =========================================================
# KPI
# =========================================================

st.markdown(
    '<div class="section-title">Tổng quan</div>',
    unsafe_allow_html=True
)

accuracy = (
    filtered_df["is_correct"].mean()
    if len(filtered_df) > 0
    else 0
)

high_count = (
    filtered_df[
        filtered_df["predicted_congestion_15m"] == "HIGH"
    ].shape[0]
)

medium_count = (
    filtered_df[
        filtered_df["predicted_congestion_15m"] == "MEDIUM"
    ].shape[0]
)

low_count = (
    filtered_df[
        filtered_df["predicted_congestion_15m"] == "LOW"
    ].shape[0]
)

total_predictions = len(filtered_df)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(
        dedent(f"""
        <div class="metric-card metric-main">
            <div class="metric-label">
                📊 Tổng dự đoán
            </div>

            <div class="metric-value">
                {total_predictions:,}
            </div>

            <div class="metric-note">
                Bản ghi sau khi lọc
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        dedent(f"""
        <div class="metric-card metric-main">
            <div class="metric-label">
                🎯 Accuracy
            </div>

            <div class="metric-value">
                {accuracy * 100:.2f}%
            </div>

            <div class="metric-note">
                Độ chính xác trên dữ liệu đang xem
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        dedent(f"""
        <div class="metric-card metric-high">
            <div class="metric-label">
                🔴 HIGH
            </div>

            <div class="metric-value">
                {high_count:,}
            </div>

            <div class="metric-note">
                Ùn tắc cao
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        dedent(f"""
        <div class="metric-card metric-medium">
            <div class="metric-label">
                🟠 MEDIUM
            </div>

            <div class="metric-value">
                {medium_count:,}
            </div>

            <div class="metric-note">
                Ùn tắc trung bình
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        dedent(f"""
        <div class="metric-card metric-low">
            <div class="metric-label">
                🟢 LOW
            </div>

            <div class="metric-value">
                {low_count:,}
            </div>

            <div class="metric-note">
                Ùn tắc thấp
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# CHART AREA 1
# =========================================================

col1, col2 = st.columns(2)


# =========================================================
# CONGESTION DISTRIBUTION
# =========================================================

with col1:

    st.markdown(
        dedent("""
        <div class="chart-card">
            <div class="chart-title">
                🚦 Phân bố mức ùn tắc
            </div>

            <div class="chart-subtitle">
                Số lượng dự đoán theo từng mức HIGH / MEDIUM / LOW
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

    congestion_counts = (
        filtered_df[
            "predicted_congestion_15m"
        ]
        .value_counts()
        .reindex(
            ["HIGH", "MEDIUM", "LOW"],
            fill_value=0
        )
        .reset_index()
    )

    congestion_counts.columns = [
        "congestion",
        "count"
    ]

    fig = px.bar(
        congestion_counts,
        x="congestion",
        y="count",
        color="congestion",
        color_discrete_map={
            "HIGH": "#ef4444",
            "MEDIUM": "#f59e0b",
            "LOW": "#22c55e"
        }
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Mức ùn tắc",
        yaxis_title="Số lượng dự đoán",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        height=400
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# =========================================================
# SPEED BY HOUR
# =========================================================

with col2:

    st.markdown(
        dedent("""
        <div class="chart-card">
            <div class="chart-title">
                🕒 Tốc độ trung bình theo giờ
            </div>

            <div class="chart-subtitle">
                Biến động tốc độ giao thông trung bình trong ngày
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

    temp_df = filtered_df.copy()

    temp_df["hour"] = (
        temp_df["timestamp"].dt.hour
    )

    hourly_speed = (
        temp_df
        .groupby(
            "hour",
            as_index=False
        )["speed"]
        .mean()
    )

    fig2 = px.line(
        hourly_speed,
        x="hour",
        y="speed",
        markers=True
    )

    fig2.update_traces(
        line=dict(
            color="#60a5fa",
            width=3
        ),
        marker=dict(
            size=7
        )
    )

    fig2.update_layout(
        xaxis_title="Giờ",
        yaxis_title="Tốc độ trung bình",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        height=400
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )


st.divider()


# =========================================================
# MODEL COMPARISON
# =========================================================

st.markdown(
    '<div class="section-title">Đánh giá mô hình</div>',
    unsafe_allow_html=True
)

model_df = pd.DataFrame(
    {
        "Model": [
            "Persistence Baseline",
            "Random Forest"
        ],
        "Accuracy": [
            0.7361,
            0.7704
        ],
        "Weighted F1": [
            0.7361,
            0.7718
        ]
    }
)

fig3 = px.bar(
    model_df,
    x="Model",
    y=[
        "Accuracy",
        "Weighted F1"
    ],
    barmode="group",
    title="Baseline so với Random Forest"
)

fig3.update_layout(
    yaxis_tickformat=".0%",
    yaxis_title="Điểm đánh giá",
    xaxis_title="Mô hình",
    height=420
)

st.plotly_chart(
    fig3,
    width="stretch"
)


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

st.markdown(
    '<div class="section-title">Feature Importance</div>',
    unsafe_allow_html=True
)

importance_df = pd.DataFrame(
    {
        "Feature": [
            "lag_speed_5m",
            "speed",
            "lag_speed_10m",
            "lag_speed_15m",
            "hour",
            "day_of_week_num",
            "minute"
        ],
        "Importance": [
            0.356469,
            0.326441,
            0.195031,
            0.117526,
            0.002827,
            0.001705,
            0.000002
        ]
    }
)

importance_df = importance_df.sort_values(
    "Importance",
    ascending=True
)

fig4 = px.bar(
    importance_df,
    x="Importance",
    y="Feature",
    orientation="h"
)

fig4.update_traces(
    marker_color="#8b5cf6"
)

fig4.update_layout(
    title="Mức độ quan trọng của các đặc trưng",
    xaxis_title="Importance",
    yaxis_title="Feature",
    height=440
)

st.plotly_chart(
    fig4,
    width="stretch"
)


st.divider()


# =========================================================
# DATA TABLE
# =========================================================

st.markdown(
    '<div class="section-title">Dữ liệu dự đoán</div>',
    unsafe_allow_html=True
)

st.caption(
    "Hiển thị dữ liệu thực tế và kết quả dự đoán "
    "mức độ ùn tắc trước 15 phút."
)

display_columns = [
    "timestamp",
    "sensor_id",
    "speed",
    "target_congestion_15m",
    "predicted_congestion_15m",
    "is_correct"
]

st.dataframe(
    filtered_df[
        display_columns
    ].head(1000),
    width="stretch",
    hide_index=True
)

st.caption(
    f"Đang hiển thị tối đa 1.000 dòng "
    f"trên tổng {len(filtered_df):,} dòng sau khi lọc."
)