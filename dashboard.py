import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from patient_profile import load_patient_profile

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
</style>
""", unsafe_allow_html=True)

profile = load_patient_profile()
df = pd.read_csv("output.csv")
latest = df.iloc[-1]

st.markdown('<div class="main-title">Privacy-Aware Elderly Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Edge-based monitoring for fall detection and vital sign alerts</div>', unsafe_allow_html=True)

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
        <b>Current Risk Level:</b><br>{latest['risk_level']}
    </div>
    """, unsafe_allow_html=True)

# Live metrics
st.markdown('<div class="section-title">Live Patient Status</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f'<div class="card"><div class="pulse">❤️</div><h4>Heart Rate</h4><div class="metric-value">{latest["heart_rate"]} bpm</div></div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="card"><h4>SpO2</h4><div class="metric-value">{latest["spo2"]}%</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="card"><h4>Temperature</h4><div class="metric-value">{latest["temperature"]} °C</div></div>', unsafe_allow_html=True)

with c4:
    st.markdown(f'<div class="card"><h4>Risk Score</h4><div class="metric-value">{latest["score"]}</div></div>', unsafe_allow_html=True)

with c5:
    css_class = latest["status"].lower()
    st.markdown(f'<div class="card"><h4>Status</h4><div class="metric-value {css_class}">{latest["status"]}</div></div>', unsafe_allow_html=True)

# Analysis section
st.markdown('<div class="section-title">Latest Analysis</div>', unsafe_allow_html=True)
a1, a2 = st.columns(2)

with a1:
    st.info(f"**Scenario:** {latest['scenario']}")
    st.info(f"**Trend:** {latest['trend_flag']}")
    st.info(f"**Reason:** {latest['reason']}")

with a2:
    st.info(f"**Suggested Action:** {latest['action']}")
    st.info(f"**Risk Level:** {latest['risk_level']}")

if latest["status"] == "EMERGENCY":
    st.error("🚨 Emergency detected! Immediate response required.")
elif latest["status"] == "WARNING":
    st.warning("⚠ Warning condition detected. Monitor closely.")
else:
    st.success("✅ Patient condition is stable.")

# Daily snapshot
st.markdown('<div class="section-title">Daily Snapshot</div>', unsafe_allow_html=True)
s1, s2, s3, s4, s5 = st.columns(5)

s1.metric("Avg Heart Rate", round(df["heart_rate"].mean(), 1))
s2.metric("Lowest SpO2", int(df["spo2"].min()))
s3.metric("Highest Temp", df["temperature"].max())
s4.metric("Warnings", int((df["status"] == "WARNING").sum()))
s5.metric("Emergencies", int((df["status"] == "EMERGENCY").sum()))

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
ax3.plot(df["score"], marker="o")
ax3.set_title("Risk Score Over Time")
ax3.set_xlabel("Reading")
ax3.set_ylabel("Score")
ax3.grid(True)
st.pyplot(fig3)

# Distribution
st.markdown('<div class="section-title">Distribution</div>', unsafe_allow_html=True)
d1, d2 = st.columns(2)

with d1:
    st.bar_chart(df["status"].value_counts())

with d2:
    st.bar_chart(df["scenario"].value_counts())

# Alert history
st.markdown('<div class="section-title">Recent Alert History</div>', unsafe_allow_html=True)
alert_df = df[df["status"] != "NORMAL"].tail(10)
st.dataframe(alert_df, use_container_width=True)

# Full log
st.markdown('<div class="section-title">Recent Monitoring Log</div>', unsafe_allow_html=True)
st.dataframe(df.tail(15), use_container_width=True)