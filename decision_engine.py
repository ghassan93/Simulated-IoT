from collections import deque
from patient_profile import get_personalized_thresholds

history_hr = deque(maxlen=5)
history_spo2 = deque(maxlen=5)
history_status = deque(maxlen=3)


def analyze(data: dict, profile: dict) -> dict:
    thresholds = get_personalized_thresholds(profile)

    score = 0
    reasons = []
    actions = []
    trend_flag = "Stable"

    hr = data["heart_rate"]
    spo2 = data["spo2"]
    temp = data["temperature"]
    acc = data["acceleration"]

    history_hr.append(hr)
    history_spo2.append(spo2)

    # Fall detection
    if acc > thresholds["fall_acceleration"]:
        score += 5
        reasons.append("High acceleration (possible fall)")

    # Low oxygen
    if spo2 < thresholds["low_spo2"]:
        score += 4
        reasons.append(f"Low SpO2 (< {thresholds['low_spo2']}%)")

    # High heart rate
    if hr > thresholds["high_hr"]:
        score += 3
        reasons.append(f"High heart rate (> {thresholds['high_hr']} bpm)")

    # Temperature
    if temp >= thresholds["high_temp"]:
        score += 1
        reasons.append("Elevated temperature")

    # Heart rate trend
    if len(history_hr) >= 3:
        if history_hr[-1] > history_hr[-2] > history_hr[-3]:
            score += 2
            trend_flag = "Heart rate increasing"
            reasons.append("Increasing heart rate trend")

    # SpO2 trend
    if len(history_spo2) >= 3:
        if history_spo2[-1] < history_spo2[-2] < history_spo2[-3]:
            score += 2
            trend_flag = "SpO2 decreasing"
            reasons.append("Decreasing oxygen trend")

    # Combined critical logic
    if acc > thresholds["fall_acceleration"] and (hr > thresholds["high_hr"] or spo2 < thresholds["low_spo2"]):
        score += 2
        reasons.append("Combined critical event")

    # Final status
    if score >= 8:
        status = "EMERGENCY"
        risk_level = "Critical"
        actions.append("Call emergency contact immediately")
        actions.append("Trigger high-priority alert")
    elif score >= 4:
        status = "WARNING"
        risk_level = "Moderate"
        actions.append("Notify caregiver")
        actions.append("Continue close monitoring")
    else:
        status = "NORMAL"
        risk_level = "Low"
        actions.append("Continue monitoring")

    # Repeated alert escalation
    history_status.append(status)
    if len(history_status) >= 2 and history_status[-1] == "EMERGENCY" and history_status[-2] == "EMERGENCY":
        actions.append("Escalated due to repeated emergency pattern")

    if not reasons:
        reasons.append("Vitals stable")

    reason_text = " + ".join(reasons)
    action_text = " | ".join(actions)

    return {
        "status": status,
        "score": score,
        "risk_level": risk_level,
        "trend_flag": trend_flag,
        "reason": reason_text,
        "action": action_text,
        "thresholds_used": thresholds
    }