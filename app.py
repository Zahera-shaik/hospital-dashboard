import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="🏥 Hospital Risk Cockpit", layout="wide")

st.title("🏥 Smart Hospital Risk Monitoring Cockpit")
st.markdown(
    "Executive Dashboard for Department Visits, Revenue Exposure, Patient Risk & Emergency Alerts"
)

# ---------------------------------------------------------
# LOAD CSV FILES (Your Real Data)
# ---------------------------------------------------------
patients_df = pd.read_csv("patients.csv")
departments_df = pd.read_csv("departments.csv")
visits_df = pd.read_csv("visits.csv")
alerts_df = pd.read_csv("alert.csv")

# ---------------------------------------------------------
# MERGE DATA FOR ANALYTICS
# ---------------------------------------------------------

# Merge Visits + Departments
visits_full = visits_df.merge(departments_df, on="DEPT_ID", how="left")

# Merge Visits + Patients
visits_full = visits_full.merge(patients_df, on="PATIENT_ID", how="left")

# Merge Alerts + Visits
alerts_full = alerts_df.merge(visits_full, on="VISIT_ID", how="left")

# ---------------------------------------------------------
# KPI METRICS SECTION
# ---------------------------------------------------------
st.subheader("📌 Executive KPIs")

total_visits = len(visits_df)
total_revenue = visits_df["BILL_AMOUNT"].sum()
avg_bill = visits_df["BILL_AMOUNT"].mean()
total_alerts = len(alerts_df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("👨‍⚕️ Total Visits", total_visits)
col2.metric("💰 Total Revenue", f"₹ {round(total_revenue,2)}")
col3.metric("📊 Avg Bill Amount", f"₹ {round(avg_bill,2)}")
col4.metric("🚨 Total Emergency Alerts", total_alerts)

st.divider()

# ---------------------------------------------------------
# FILTER SECTION
# ---------------------------------------------------------
st.subheader("🎛️ Department Filter")

dept_list = ["All"] + sorted(departments_df["DEPARTMENT_NAME"].unique())
selected_dept = st.selectbox("Select Department", dept_list)

filtered_visits = visits_full.copy()

if selected_dept != "All":
    filtered_visits = filtered_visits[
        filtered_visits["DEPARTMENT_NAME"] == selected_dept
    ]

st.divider()

# ---------------------------------------------------------
# VISUAL 1: Department-wise Visit Load
# ---------------------------------------------------------
st.subheader("📊 Department-wise Visit Load")

visit_summary = (
    filtered_visits.groupby("DEPARTMENT_NAME")["VISIT_ID"]
    .count()
    .reset_index()
)

visit_chart = visit_summary.set_index("DEPARTMENT_NAME")

st.bar_chart(visit_chart)

st.divider()

# ---------------------------------------------------------
# VISUAL 2: Revenue by Department
# ---------------------------------------------------------
st.subheader("💰 Revenue Comparison Across Departments")

revenue_summary = (
    filtered_visits.groupby("DEPARTMENT_NAME")["BILL_AMOUNT"]
    .sum()
    .reset_index()
)

revenue_chart = revenue_summary.set_index("DEPARTMENT_NAME")

st.line_chart(revenue_chart)

st.divider()

# ---------------------------------------------------------
# UNIQUE REPORT: Top 5 Revenue Departments
# ---------------------------------------------------------
st.subheader("🏆 Top 5 Revenue Departments")

top5 = revenue_summary.sort_values("BILL_AMOUNT", ascending=False).head(5)
st.dataframe(top5, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# HIGH RISK PATIENTS SECTION
# ---------------------------------------------------------
st.subheader("⚠️ High Risk Patients Monitoring")

high_risk = patients_df[patients_df["RISK_SCORE"] >= 80]

st.dataframe(high_risk, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# PATIENT SEARCH DRILLDOWN
# ---------------------------------------------------------
st.subheader("🔍 Patient Risk Drilldown Search")

patient_list = ["Select"] + sorted(patients_df["NAME"].unique())
selected_patient = st.selectbox("Choose Patient", patient_list)

if selected_patient != "Select":
    patient_data = patients_df[patients_df["NAME"] == selected_patient]
    st.dataframe(patient_data, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# RISK CATEGORY DISTRIBUTION
# ---------------------------------------------------------
st.subheader("🩺 Risk Category Distribution")

risk_levels = patients_df.copy()

risk_levels["RISK_LEVEL"] = risk_levels["RISK_SCORE"].apply(
    lambda x: "HIGH" if x >= 80 else "MEDIUM" if x >= 50 else "LOW"
)

risk_summary = risk_levels.groupby("RISK_LEVEL").size()

st.bar_chart(risk_summary)

st.divider()

# ---------------------------------------------------------
# ALERT FILTER SECTION
# ---------------------------------------------------------
st.subheader("🚨 Emergency Alerts Drilldown")

# FIX: Clean Alert Level Column
alerts_df["ALERT_LEVEL"] = alerts_df["ALERT_LEVEL"].fillna("UNKNOWN").astype(str)

alert_levels = ["All"] + sorted(alerts_df["ALERT_LEVEL"].unique())
selected_level = st.selectbox("Select Alert Level", alert_levels)

filtered_alerts = alerts_full.copy()

if selected_level != "All":
    filtered_alerts = filtered_alerts[
        filtered_alerts["ALERT_LEVEL"] == selected_level
    ]

# ---------------------------------------------------------
# ALERT TYPE DISTRIBUTION
# ---------------------------------------------------------
st.subheader("📌 Alert Type Distribution")

alert_type_summary = (
    filtered_alerts.groupby("ALERT_TYPE")
    .size()
    .to_frame("COUNT")
)

st.bar_chart(alert_type_summary)

st.divider()

# ---------------------------------------------------------
# ALERT TABLE WITH HIGHLIGHTING
# ---------------------------------------------------------
st.subheader("🚨 Live Emergency Alerts (Highlighted)")


def highlight_alert(row):
    if row["ALERT_LEVEL"] == "HIGH":
        return ["background-color: red"] * len(row)
    elif row["ALERT_LEVEL"] == "MEDIUM":
        return ["background-color: orange"] * len(row)
    else:
        return ["background-color: lightgreen"] * len(row)


st.dataframe(filtered_alerts.style.apply(highlight_alert, axis=1))

st.divider()

# ---------------------------------------------------------
# DOWNLOAD ALERT REPORT
# ---------------------------------------------------------
st.subheader("⬇️ Download Emergency Alert Report")

csv = filtered_alerts.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Alerts as CSV",
    data=csv,
    file_name="hospital_emergency_alerts.csv",
    mime="text/csv",
)

st.divider()

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.success("✅ Smart Hospital Risk Cockpit Loaded Successfully!")
st.caption("Built with Real Hospital Data + Streamlit Visual Analytics")
