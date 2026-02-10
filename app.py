import streamlit as st

# =========================================================
# 1️⃣ PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="🏥 Hospital Risk Cockpit",
    layout="wide"
)

st.title("🏥 Smart Hospital Risk Monitoring Cockpit")
st.markdown(
    "Executive Dashboard for Department Visits, Revenue Exposure, Patient Risk & Emergency Alerts"
)

st.divider()

# =========================================================
# 2️⃣ SNOWFLAKE SESSION (Snowflake OR Local)
# =========================================================
try:
    # Works ONLY inside Snowflake Streamlit
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
    st.success("✅ Running inside Snowflake Streamlit Environment")

except:
    # Works Locally (Manual Connection)
    from snowflake.snowpark import Session
    st.warning("⚠️ Running Locally - Connecting Manually to Snowflake")

    connection_parameters = {
        "account": "DSNFICY-SR18760",
        "user": "ZAHERA001",
        "password": "22761A0551@asra",
        "role": "ACCOUNTADMIN",
        "warehouse": "COMPUTE_WH",
        "database": "HOSPITAL_ANALYTICS_DB",
        "schema": "GOLD"
    }

    session = Session.builder.configs(connection_parameters).create()

# =========================================================
# 3️⃣ LOAD GOLD VIEWS FROM SNOWFLAKE
# =========================================================
st.subheader("📥 Loading Gold Analytics Views...")

kpi_df = session.sql("SELECT * FROM GOLD.VW_HOSPITAL_KPI").to_pandas()
risk_df = session.sql("SELECT * FROM GOLD.VW_HIGH_RISK_PATIENTS").to_pandas()
alert_df = session.sql("SELECT * FROM GOLD.VW_ALERT_DRILLDOWN").to_pandas()
emergency_df = session.sql("SELECT * FROM GOLD.VW_DEPT_EMERGENCY_STATS").to_pandas()

# Optional Trend View
try:
    trend_df = session.sql("SELECT * FROM GOLD.VW_VISIT_TREND").to_pandas()
except:
    trend_df = None

st.success("✅ Data Loaded Successfully!")
st.divider()

# =========================================================
# 4️⃣ EXECUTIVE KPI METRICS
# =========================================================
st.subheader("📌 Executive KPIs")

total_visits = int(kpi_df["TOTAL_VISITS"].sum())
total_revenue = float(kpi_df["TOTAL_REVENUE"].sum())
avg_bill = float(kpi_df["AVG_BILL"].mean())

col1, col2, col3 = st.columns(3)

col1.metric("👨‍⚕️ Total Visits", total_visits)
col2.metric("💰 Total Revenue", f"₹ {round(total_revenue,2)}")
col3.metric("📊 Avg Bill Amount", f"₹ {round(avg_bill,2)}")

st.divider()

# =========================================================
# 5️⃣ FILTER SECTION
# =========================================================
st.subheader("🎛️ Department Filter")

dept_list = ["All"] + sorted(kpi_df["DEPT_NAME"].unique())
selected_dept = st.selectbox("Select Department", dept_list)

if selected_dept != "All":
    kpi_df = kpi_df[kpi_df["DEPT_NAME"] == selected_dept]
    emergency_df = emergency_df[emergency_df["DEPT_NAME"] == selected_dept]

st.divider()

# =========================================================
# 6️⃣ VISUAL 1: VISIT LOAD REPORT
# =========================================================
st.subheader("📊 Department-wise Visit Load")

visit_chart = kpi_df.set_index("DEPT_NAME")[["TOTAL_VISITS"]]
st.bar_chart(visit_chart)

st.divider()

# =========================================================
# 7️⃣ VISUAL 2: REVENUE COMPARISON REPORT
# =========================================================
st.subheader("💰 Revenue Comparison Across Departments")

revenue_chart = kpi_df.set_index("DEPT_NAME")[["TOTAL_REVENUE"]]
st.line_chart(revenue_chart)

st.divider()

# =========================================================
# 8️⃣ UNIQUE REPORT: TOP 5 REVENUE DEPARTMENTS
# =========================================================
st.subheader("🏆 Top 5 Revenue Departments (Executive Leaderboard)")

top_depts = kpi_df.sort_values("TOTAL_REVENUE", ascending=False).head(5)
st.dataframe(top_depts, use_container_width=True)

st.divider()

# =========================================================
# 9️⃣ VISUAL 3: EMERGENCY VISITS REPORT
# =========================================================
st.subheader("🚨 Emergency Visits by Department")

emergency_chart = emergency_df.set_index("DEPT_NAME")[["EMERGENCY_VISITS"]]
st.bar_chart(emergency_chart)

st.divider()

# =========================================================
# 🔟 HIGH RISK PATIENTS TABLE
# =========================================================
st.subheader("⚠️ High Risk Patients Monitoring")

st.dataframe(risk_df, use_container_width=True)

st.divider()

# =========================================================
# 1️⃣1️⃣ UNIQUE REPORT: PATIENT SEARCH DRILLDOWN
# =========================================================
st.subheader("🔍 Patient Risk Drilldown Search")

patient_list = ["Select"] + sorted(risk_df["PATIENT_NAME"].unique())
selected_patient = st.selectbox("Choose Patient", patient_list)

if selected_patient != "Select":
    patient_data = risk_df[risk_df["PATIENT_NAME"] == selected_patient]
    st.write("📌 Selected Patient Details:")
    st.dataframe(patient_data, use_container_width=True)

st.divider()

# =========================================================
# 1️⃣2️⃣ RISK DISTRIBUTION REPORT (Fixed)
# =========================================================
st.subheader("🩺 Risk Score Distribution")

risk_counts = risk_df["RISK_SCORE"].value_counts().to_frame("COUNT")
st.bar_chart(risk_counts)

st.divider()

# =========================================================
# 1️⃣3️⃣ ALERT FILTER + ALERT ANALYTICS
# =========================================================
st.subheader("🚨 Emergency Alerts Drilldown")

if "ALERT_LEVEL" in alert_df.columns:
    alert_levels = ["All"] + sorted(alert_df["ALERT_LEVEL"].unique())
    selected_level = st.selectbox("Select Alert Level", alert_levels)

    if selected_level != "All":
        alert_df = alert_df[alert_df["ALERT_LEVEL"] == selected_level]

else:
    st.error("❌ ALERT_LEVEL column missing in VW_ALERT_DRILLDOWN")

# =========================================================
# 1️⃣4️⃣ VISUAL 4: ALERT TYPE DISTRIBUTION
# =========================================================
st.subheader("📌 Alert Type Distribution")

alert_chart = alert_df.groupby("ALERT_TYPE").size().to_frame("COUNT")
st.bar_chart(alert_chart)

st.divider()

# =========================================================
# 1️⃣5️⃣ ALERT TABLE WITH HIGHLIGHTING
# =========================================================
st.subheader("🚨 Live Emergency Alerts (Highlighted)")

def highlight_alert(row):
    if row["ALERT_LEVEL"] == "HIGH":
        return ["background-color: #ff4d4d"] * len(row)
    elif row["ALERT_LEVEL"] == "MEDIUM":
        return ["background-color: #ffa500"] * len(row)
    else:
        return ["background-color: #90ee90"] * len(row)

st.dataframe(alert_df.style.apply(highlight_alert, axis=1))

st.divider()

# =========================================================
# 1️⃣6️⃣ DOWNLOAD REPORT BUTTON
# =========================================================
st.subheader("⬇️ Download Emergency Alert Report")

csv = alert_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Alerts as CSV",
    data=csv,
    file_name="hospital_emergency_alerts.csv",
    mime="text/csv"
)

st.divider()

# =========================================================
# 1️⃣7️⃣ OPTIONAL TREND ANALYTICS REPORT
# =========================================================
if trend_df is not None:
    st.subheader("📈 Daily Visit Trend Analytics")

    trend_chart = trend_df.set_index("VISIT_DATE")[["DAILY_VISITS"]]
    st.line_chart(trend_chart)

    st.success("✅ Trend Analytics Loaded Successfully!")

st.divider()

# =========================================================
# 1️⃣8️⃣ FOOTER
# =========================================================
st.success("✅ Smart Hospital Risk Cockpit Loaded Successfully!")
st.caption("Built using Snowflake Gold Views + Streamlit Native Visual Analytics")
