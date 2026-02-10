import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Hospital Risk Cockpit", layout="wide")

st.title("🏥 Smart Hospital Risk Monitoring Cockpit")
st.markdown("### Executive Dashboard for Patient Risk, Emergency Load & Revenue Exposure")

st.divider()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("🎛️ Hospital Monitoring Filters")

visit_count = st.sidebar.slider("Number of Patient Visits", 500, 5000, 1500)
risk_threshold = st.sidebar.slider("Minimum Patient Risk Score", 0, 100, 60)
bill_threshold = st.sidebar.slider("High Cost Visit Threshold (₹)", 10000, 100000, 30000)

# -------------------------------------------------
# GENERATE SYNTHETIC HOSPITAL DATA
# -------------------------------------------------
np.random.seed(42)

dates = pd.date_range(end=datetime.today(), periods=30)

departments = ["Cardiology", "Neurology", "Orthopedics", "Emergency", "Pediatrics"]
conditions = ["Diabetes", "Heart Disease", "Fracture", "Asthma", "Cancer"]

data = []

for _ in range(visit_count):
    date = random.choice(dates)
    dept = random.choice(departments)
    condition = random.choice(conditions)

    bill_amount = np.random.randint(500, 120000)
    risk_score = np.random.randint(5, 100)

    alert_reason = None

    if bill_amount > bill_threshold:
        alert_reason = "High Cost Treatment"
    elif risk_score > 85:
        alert_reason = "Critical Patient Risk"
    elif dept == "Emergency":
        alert_reason = "Emergency Visit Alert"

    data.append([
        random.randint(1000, 3000),   # Patient ID
        dept,
        condition,
        date,
        bill_amount,
        risk_score,
        alert_reason
    ])

df = pd.DataFrame(data, columns=[
    "PATIENT_ID",
    "DEPARTMENT",
    "CONDITION",
    "VISIT_DATE",
    "BILL_AMOUNT",
    "RISK_SCORE",
    "ALERT_REASON"
])

# -------------------------------------------------
# EXECUTIVE KPIs
# -------------------------------------------------
total_visits = len(df)
high_risk_cases = df["ALERT_REASON"].notna().sum()
total_revenue = df["BILL_AMOUNT"].sum()
risk_rate = round((high_risk_cases / total_visits) * 100, 2)

st.markdown("## 📌 Executive Hospital KPIs")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Patient Visits", f"{total_visits}")
c2.metric("Critical Alerts Raised", f"{high_risk_cases}")
c3.metric("Total Hospital Revenue", f"₹ {total_revenue:,}")
c4.metric("Risk Alert Rate (%)", f"{risk_rate}%")

st.divider()

# -------------------------------------------------
# VISIT TREND OVER TIME
# -------------------------------------------------
st.markdown("## 📈 Daily Visit Trend (Last 30 Days)")

trend_df = df.groupby("VISIT_DATE").size()

st.line_chart(trend_df)

st.divider()

# -------------------------------------------------
# EMERGENCY LOAD BY HOUR
# -------------------------------------------------
st.markdown("## ⏰ Emergency Load by Hour")

df["VISIT_HOUR"] = np.random.randint(0, 24, size=len(df))

hourly = df[df["DEPARTMENT"] == "Emergency"] \
    .groupby("VISIT_HOUR").size()

st.bar_chart(hourly)

st.divider()

# -------------------------------------------------
# ALERT ROOT CAUSE ANALYSIS
# -------------------------------------------------
st.markdown("## 🚨 Hospital Alert Root Cause Breakdown")

root_cause = df[df["ALERT_REASON"].notna()] \
    .groupby("ALERT_REASON").size()

st.bar_chart(root_cause)

st.divider()

# -------------------------------------------------
# PATIENT RISK SEGMENTATION
# -------------------------------------------------
st.markdown("## 🧠 Patient Risk Segmentation")

filtered = df[df["RISK_SCORE"] >= risk_threshold]

filtered["RISK_LEVEL"] = filtered["RISK_SCORE"].apply(
    lambda x: "HIGH" if x >= 80 else "MEDIUM" if x >= 50 else "LOW"
)

risk_summary = filtered.groupby("RISK_LEVEL").size()

st.bar_chart(risk_summary)

st.info(f"Showing {len(filtered)} visits with Risk Score ≥ {risk_threshold}")

st.divider()

# -------------------------------------------------
# TOP DEPARTMENTS BY REVENUE
# -------------------------------------------------
st.markdown("## 🏆 Top Revenue Generating Departments")

top_depts = df.groupby("DEPARTMENT")["BILL_AMOUNT"].sum() \
    .sort_values(ascending=False)

st.bar_chart(top_depts)

st.divider()

# -------------------------------------------------
# PATIENT DRILLDOWN SEARCH
# -------------------------------------------------
st.markdown("## 🔍 Patient Visit Investigation Panel")

patient_id = st.number_input(
    "Enter Patient ID to Investigate",
    min_value=1000,
    max_value=3000
)

patient_data = df[df["PATIENT_ID"] == patient_id]

st.dataframe(patient_data, use_container_width=True)

st.success("✅ Smart Hospital Cockpit Loaded Successfully!")
st.caption("Built for Hackathon: Real-Time Hospital Risk & Emergency Analytics")
