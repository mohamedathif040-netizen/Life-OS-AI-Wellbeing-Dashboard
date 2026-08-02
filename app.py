import streamlit as st
import pandas as pd
import requests
import base64
from urllib.parse import quote
from ai_coach import get_ai_coaching, get_avatar_prompt


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Life-OS",
    page_icon="📱",
    layout="wide"
)
def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()
    
bg = get_base64_image("assets/background.png")

st.markdown(
    f"""
    <style>
    
    .stApp {{
        background:
            linear-gradient(rgba(5,8,20,0.75), rgba(5,8,20,0.75)),
            url("data:image/png;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        
    }}
    
    </style>
    
    """,
    unsafe_allow_html=True
    
    
)
# -----------------------------
# Upload Screen Time CSV
# -----------------------------
uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Screen Time CSV",
    type=["csv"],
    help="Upload your own screen time data or use the sample dataset."
)

# Load uploaded file if available
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ Using uploaded data")
else:
    df = pd.read_csv("screentime.csv")
    st.sidebar.info("📄 Using sample dataset")
    
required_columns = {
    "Date",
    "App_Name",
    "Category",
    "Minutes_Used"
}

if not required_columns.issubset(df.columns):
    st.error(
        "Invalid CSV format.\n\n"
        "Required columns:\n"
        "Date, App_Name, Category, Minutes_Used"
    )
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date")

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("📱 Life-OS Wellbeing Dashboard")
st.markdown("### Your AI-powered Digital Wellbeing Companion")

st.divider()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.success("🟢 Life-OS is Running")

st.sidebar.info(
    """
Track your digital habits.

Analyze your productivity.

Receive AI coaching.
"""
)
st.sidebar.header("⚙ Dashboard Controls")

dates = df["Date"].dt.strftime("%Y-%m-%d").unique()
selected_date = st.sidebar.selectbox(
    "Select a Day",
    dates
)

daily_goal = st.sidebar.slider(
    "Daily Goal (Minutes)",
    min_value=60,
    max_value=600,
    value=300,
    step=30
)

show_data = st.sidebar.checkbox("Show Raw Dataset")

# -----------------------------
# Filter Data
# -----------------------------
selected_datetime = pd.to_datetime(selected_date)

day_df = df[df["Date"] == selected_datetime]
# -----------------------------
# KPI Calculations
# -----------------------------
total_minutes = day_df["Minutes_Used"].sum()

top_app = day_df.loc[
    day_df["Minutes_Used"].idxmax(),
    "App_Name"
]

goal_difference = total_minutes - daily_goal

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Today's Screen Time",
        f"{total_minutes} min"
    )

with col2:
    st.metric(
        "Most Used App",
        top_app
    )

with col3:
    st.metric(
        "Goal Status",
        f"{goal_difference:+} min",
        delta=f"{goal_difference:+} min",
        delta_color="inverse"
    )

st.divider()

# Productivity Score
productivity_score = max(0, min(100, 100 - int((total_minutes / daily_goal) * 50)))

st.subheader("🏆 Productivity Score")

st.progress(productivity_score / 100)

st.write(f"### {productivity_score}/100")

st.subheader("🎯 Daily Goal Progress")

progress = min(total_minutes / daily_goal, 1.0)

st.progress(progress)

st.write(f"{total_minutes} / {daily_goal} minutes")

# -----------------------------
# Charts
# -----------------------------

# Daily Trend
daily_total = (
    df.groupby("Date")["Minutes_Used"]
    .sum()
)

st.subheader("📈 Daily Screen Time Trend")

st.line_chart(daily_total)

# Category Usage
category_total = (
    day_df.groupby("Category")["Minutes_Used"]
    .sum()
)

st.subheader("📊 Today's Category Usage")

st.bar_chart(category_total)

st.divider()

st.subheader("🤖 AI Lifestyle Coach")

summary = (
    day_df.groupby("Category")["Minutes_Used"]
    .sum()
    .to_string()
)

if st.button("🧠 Analyze My Day"):

    with st.spinner("Life-OS is analyzing your habits..."):

        advice = get_ai_coaching(summary)

    if total_minutes > daily_goal + 60:
        st.warning(advice)

    elif total_minutes > daily_goal:
        st.info(advice)

    else:
        st.success(advice)
        
st.divider()

st.subheader("📅 Weekly Insights")

daily_summary = (
    df.groupby("Date")["Minutes_Used"]
    .sum()
)

st.write(f"📊 Average Daily Screen Time: **{int(daily_summary.mean())} minutes**")

st.write(f"🔥 Highest Usage Day: **{daily_summary.idxmax()} ({daily_summary.max()} min)**")

st.write(f"✅ Lowest Usage Day: **{daily_summary.idxmin()} ({daily_summary.min()} min)**")

st.subheader("📂 Category Breakdown")

category_percentage = (
    day_df.groupby("Category")["Minutes_Used"]
    .sum()
)

st.dataframe(category_percentage)

st.divider()
st.subheader("🎭 Today's Productivity Avatar")

if st.button("Generate Avatar"):

    with st.spinner("Creating your avatar..."):

        avatar_prompt = get_avatar_prompt(summary)

        image_url = (
            "https://image.pollinations.ai/prompt/"
            + quote(avatar_prompt)
        )

        st.image(
            image_url,
            caption=avatar_prompt,
            use_container_width=True
        )

# -----------------------------
# Raw Data
# -----------------------------
if show_data:
    st.subheader("Dataset")
    st.dataframe(day_df, use_container_width=True)