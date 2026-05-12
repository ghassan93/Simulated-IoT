import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from patient_profile import load_patient_profile
from scenarios import generate_scenario, SCENARIO_OPTIONS, SCENARIO_LABELS
from decision_engine import analyze, reset_trend_history
from logger import FILE_NAME, init_logger, log_data

st.set_page_config(page_title="Elderly Monitoring Dashboard", layout="wide")

st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #3CFA58;
    margin-bottom: 10px;
}
.subtitle {
    color: #E3FFED;
    font-size: 16px;
    margin-bottom: 18px;
}
.card {
    padding: 18px;
    border-radius: 18px;
    background: #f8fafc;
    color:#111212;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    text-align: center;
    min-height: 135px;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
}
.pulse {
    font-size: 38px;
    animation: pulse 1.2s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.18); }
    100% { transform: scale(1); }
}
.normal { color: #16a34a; font-weight: 800; }
.warning { color: #ca8a04; font-weight: 800; }
.emergency { color: #dc2626; font-weight: 800; }
.profile-box {
    padding: 18px;
    border-radius: 18px;
    background: #eff6ff;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    color:#111212;
}
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 8px;
}
.analysis-box {
    padding: 18px;
    border-radius: 18px;
    background: #ecfeff;
    color:#111212;
    border-left: 6px solid #0891b2;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    line-height: 1.65;
}
.risk-low { color: #16a34a; font-weight: 800; }
.risk-moderate { color: #ca8a04; font-weight: 800; }
.risk-critical { color: #dc2626; font-weight: 800; }
.trend-small {
    font-size: 14px;
    margin-top: 8px;
    color: #334155;
    font-weight: 700;
}
.ai-box {
    padding: 20px;
    border-radius: 20px;
    background: linear-gradient(135deg, #eef2ff, #ecfeff);
    color:#111212;
    border-left: 7px solid #4f46e5;
    box-shadow: 0 8px 24px rgba(15,23,42,0.10);
    line-height: 1.7;
}
.ai-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: #e0e7ff;
    color: #3730a3;
    font-weight: 800;
    margin-right: 6px;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

profile = load_patient_profile()


def run_dashboard_simulation(selected_scenario, readings_count):
    init_logger()
    for _ in range(readings_count):
        scenario, data = generate_scenario(selected_scenario)
        result = analyze(data, profile)
        log_data(profile, scenario, data, result)


def reset_dashboard_log():
    reset_trend_history()
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
    init_logger()


st.sidebar.markdown("## Scenario Control")
selected_scenario = st.sidebar.selectbox(
    "Scenario Mode",
    SCENARIO_OPTIONS,
    format_func=lambda key: SCENARIO_LABELS.get(key, key),
    index=0,
)
readings_count = st.sidebar.slider("Readings to generate", min_value=1, max_value=30, value=5)

col_run_one, col_run_batch = st.sidebar.columns(2)
with col_run_one:
    if st.button("Generate 1", use_container_width=True):
        run_dashboard_simulation(selected_scenario, 1)
        st.rerun()
with col_run_batch:
    if st.button("Generate Batch", use_container_width=True):
        run_dashboard_simulation(selected_scenario, readings_count)
        st.rerun()

if st.sidebar.button("Reset Monitoring Log", use_container_width=True):
    reset_dashboard_log()
    st.rerun()

st.sidebar.caption(
    "Use this panel during the demo to switch between normal, fall, low oxygen, borderline SpO2, and gradual deterioration scenarios."
)

if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) == 0:
    reset_dashboard_log()
    run_dashboard_simulation("Random", 5)

df = pd.read_csv(FILE_NAME)
if df.empty:
    run_dashboard_simulation("Random", 5)
    df = pd.read_csv(FILE_NAME)
latest = df.iloc[-1]


def get_value(row, column, default="N/A"):
    return row[column] if column in row.index and pd.notna(row[column]) else default


def trend_icon(value):
    value = str(value).lower()
    if value == "rising":
        return "↑ Rising"
    if value == "falling":
        return "↓ Falling"
    if value == "collecting data":
        return "… Collecting"
    return "↔ Stable"


def risk_class(value):
    value = str(value).lower()
    if value == "critical":
        return "risk-critical"
    if value == "moderate":
        return "risk-moderate"
    return "risk-low"


hr_trend = get_value(latest, "hr_trend", "Stable")
spo2_trend = get_value(latest, "spo2_trend", "Stable")
temp_trend = get_value(latest, "temp_trend", "Stable")
stability_status = get_value(latest, "stability_status", "Stable")
early_warning = get_value(latest, "early_warning", "No early deterioration pattern detected")
smart_explanation = get_value(
    latest,
    "smart_explanation",
    "Trend interpretation is available after running the updated monitoring engine."
)
ai_explanation = get_value(
    latest,
    "ai_explanation",
    "Fuzzy-inspired AI explanation is available after generating new readings."
)
patient_state = get_value(latest, "patient_state", "Stable")
fuzzy_risk_score = get_value(latest, "fuzzy_risk_score", latest.get("score", 0))
confidence_score = get_value(latest, "confidence_score", 50)
stability_index = get_value(latest, "stability_index", 100)
fuzzy_breakdown = get_value(latest, "fuzzy_breakdown", "Not available yet")

st.markdown('<div class="main-title">Privacy-Aware Elderly Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Edge-based monitoring with fuzzy-inspired risk scoring, early warning, and explainable smart alerts</div>', unsafe_allow_html=True)

# Profile section
st.markdown('<div class="section-title">Patient Profile</div>', unsafe_allow_html=True)
p1, p2 = st.columns([2, 1])

with p1:
    st.markdown(f"""
    <div class="profile-box">
        <b>Name:</b> {profile['name']}<br>
        <b>Patient ID:</b> {profile['patient_id']}<br>
        <b>Age:</b> {profile['age']}<br>
        <b>Gender:</b> {profile['gender']}<br>
        <b>Blood Type:</b> {profile['blood_type']}<br>
        <b>Conditions:</b> {", ".join(profile['chronic_conditions'])}<br>
        <b>Allergies:</b> {", ".join(profile['allergies'])}<br>
        <b>Notes:</b> {profile['notes']}
    </div>
    """, unsafe_allow_html=True)

with p2:
    st.markdown(f"""
    <div class="profile-box">
        <b>Emergency Contact:</b><br>{profile['emergency_contact']}<br><br>
        <b>Current Risk Level:</b><br><span class="{risk_class(latest['risk_level'])}">{latest['risk_level']}</span><br><br>
        <b>Patient State:</b><br>{patient_state}<br><br>
        <b>Stability:</b><br>{stability_status}
    </div>
    """, unsafe_allow_html=True)

# Live metrics
st.markdown('<div class="section-title">Live Patient Status</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(
        f'<div class="card"><div class="pulse">❤️</div><h4>Heart Rate</h4>'
        f'<div class="metric-value">{latest["heart_rate"]} bpm</div>'
        f'<div class="trend-small">{trend_icon(hr_trend)}</div></div>',
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f'<div class="card"><h4>SpO2</h4><div class="metric-value">{latest["spo2"]}%</div>'
        f'<div class="trend-small">{trend_icon(spo2_trend)}</div></div>',
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f'<div class="card"><h4>Temperature</h4><div class="metric-value">{latest["temperature"]} °C</div>'
        f'<div class="trend-small">{trend_icon(temp_trend)}</div></div>',
        unsafe_allow_html=True
    )

with c4:
    risk_css = risk_class(latest["risk_level"])
    st.markdown(
        f'<div class="card"><h4>Fuzzy Risk</h4><div class="metric-value">{fuzzy_risk_score}%</div>'
        f'<div class="trend-small {risk_css}">{latest["risk_level"]}</div></div>',
        unsafe_allow_html=True
    )

with c5:
    css_class = latest["status"].lower()
    st.markdown(
        f'<div class="card"><h4>Patient State</h4><div class="metric-value {css_class}">{patient_state}</div>'
        f'<div class="trend-small">{latest["status"]}</div></div>',
        unsafe_allow_html=True
    )

with c6:
    st.markdown(
        f'<div class="card"><h4>Confidence</h4><div class="metric-value">{confidence_score}%</div>'
        f'<div class="trend-small">Stability Index: {stability_index}%</div></div>',
        unsafe_allow_html=True
    )

# Analysis section
st.markdown('<div class="section-title">Latest Analysis</div>', unsafe_allow_html=True)
a1, a2 = st.columns(2)

with a1:
    st.info(f"**Scenario:** {latest['scenario']}")
    st.info(f"**Trend Summary:** {latest['trend_flag']}")
    st.info(f"**Reason:** {latest['reason']}")

with a2:
    st.info(f"**Suggested Action:** {latest['action']}")
    st.info(f"**Risk Level:** {latest['risk_level']}")
    st.info(f"**Patient State:** {patient_state}")
    st.info(f"**Early Warning:** {early_warning}")

st.markdown(f"""
<div class="analysis-box">
    <b>Smart Analysis Panel</b><br>
    {smart_explanation}<br>
    <b>Clinical Interpretation:</b> {latest['reason']}
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="ai-box">
    <b>Explainable Fuzzy AI Panel</b><br>
    <span class="ai-pill">Patient State: {patient_state}</span>
    <span class="ai-pill">Fuzzy Risk: {fuzzy_risk_score}%</span>
    <span class="ai-pill">Confidence: {confidence_score}%</span>
    <span class="ai-pill">Stability Index: {stability_index}%</span><br>
    {ai_explanation}<br>
    <b>Fuzzy Breakdown:</b> {fuzzy_breakdown}
</div>
""", unsafe_allow_html=True)

if latest["status"] == "EMERGENCY":
    st.error("🚨 Emergency detected! Immediate response required.")
elif latest["status"] == "WARNING":
    st.warning("⚠ Warning condition detected. Monitor closely.")
else:
    st.success("✅ Patient condition is stable.")

# Daily snapshot
st.markdown('<div class="section-title">Daily Snapshot</div>', unsafe_allow_html=True)
s1, s2, s3, s4, s5, s6 = st.columns(6)

s1.metric("Avg Heart Rate", round(df["heart_rate"].mean(), 1))
s2.metric("Lowest SpO2", int(df["spo2"].min()))
s3.metric("Highest Temp", df["temperature"].max())
s4.metric("Warnings", int((df["status"] == "WARNING").sum()))
s5.metric("Emergencies", int((df["status"] == "EMERGENCY").sum()))
if "fuzzy_risk_score" in df.columns:
    s6.metric("Avg Fuzzy Risk", round(df["fuzzy_risk_score"].mean(), 1))
else:
    s6.metric("Avg Fuzzy Risk", "N/A")

# Trend interpretation snapshot
st.markdown('<div class="section-title">Trend Interpretation Snapshot</div>', unsafe_allow_html=True)
t1, t2, t3, t4, t5, t6 = st.columns(6)
t1.metric("Heart Rate Trend", trend_icon(hr_trend))
t2.metric("SpO2 Trend", trend_icon(spo2_trend))
t3.metric("Temperature Trend", trend_icon(temp_trend))
t4.metric("Stability", stability_status)
t5.metric("Patient State", patient_state)
t6.metric("Confidence", f"{confidence_score}%")

# Charts
st.markdown('<div class="section-title">Vital Sign Trends</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns(2)

with ch1:
    fig1, ax1 = plt.subplots()
    ax1.plot(df["heart_rate"], marker="o")
    ax1.set_title("Heart Rate Over Time")
    ax1.set_xlabel("Reading")
    ax1.set_ylabel("BPM")
    ax1.grid(True)
    st.pyplot(fig1)

with ch2:
    fig2, ax2 = plt.subplots()
    ax2.plot(df["spo2"], marker="o")
    ax2.set_title("SpO2 Over Time")
    ax2.set_xlabel("Reading")
    ax2.set_ylabel("%")
    ax2.grid(True)
    st.pyplot(fig2)

st.markdown('<div class="section-title">Risk Score Trend</div>', unsafe_allow_html=True)
fig3, ax3 = plt.subplots(figsize=(8, 2))
risk_series = df["fuzzy_risk_score"] if "fuzzy_risk_score" in df.columns else df["score"]
ax3.plot(risk_series, marker="o")
ax3.set_title("Fuzzy Risk Score Over Time")
ax3.set_xlabel("Reading")
ax3.set_ylabel("Risk %")
ax3.grid(True)
st.pyplot(fig3)

# Distribution
st.markdown('<div class="section-title">Distribution</div>', unsafe_allow_html=True)
d1, d2 = st.columns(2)

with d1:
    st.bar_chart(df["status"].value_counts())

with d2:
    st.bar_chart(df["scenario"].value_counts())

if "patient_state" in df.columns:
    st.markdown('<div class="section-title">AI Patient State Distribution</div>', unsafe_allow_html=True)
    st.bar_chart(df["patient_state"].value_counts())

# Alert history
st.markdown('<div class="section-title">Recent Alert History</div>', unsafe_allow_html=True)
alert_df = df[df["status"] != "NORMAL"].tail(10)
st.dataframe(alert_df, use_container_width=True)

# Full log
st.markdown('<div class="section-title">Recent Monitoring Log</div>', unsafe_allow_html=True)
st.dataframe(df.tail(15), use_container_width=True)
