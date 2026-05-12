from collections import deque
from statistics import mean, pstdev
from patient_profile import get_personalized_thresholds

# Short rolling histories keep the logic lightweight and suitable for edge-based monitoring.
history_hr = deque(maxlen=8)
history_spo2 = deque(maxlen=8)
history_temp = deque(maxlen=8)
history_status = deque(maxlen=3)


def reset_trend_history():
    """Clear rolling histories when starting a new dashboard simulation session."""
    history_hr.clear()
    history_spo2.clear()
    history_temp.clear()
    history_status.clear()


def _safe_avg(values):
    return mean(values) if values else 0


def _clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def _linear_membership(value, low, high, inverse=False):
    """
    Convert a clinical value into a gradual fuzzy membership score between 0 and 100.
    inverse=True means lower values are riskier, such as SpO2.
    """
    if low == high:
        return 100 if value >= high else 0

    if inverse:
        if value >= high:
            return 0
        if value <= low:
            return 100
        return round(((high - value) / (high - low)) * 100, 1)

    if value <= low:
        return 0
    if value >= high:
        return 100
    return round(((value - low) / (high - low)) * 100, 1)


def _trend_direction(values, increasing_is_risky=True, min_change=1.0):
    """
    Compare recent readings with previous readings using a lightweight moving-average approach.
    This is more stable than checking only the last 3 raw values.
    """
    if len(values) < 4:
        return {
            "direction": "Stable",
            "delta": 0,
            "rate": 0,
            "recent_avg": values[-1] if values else 0,
            "previous_avg": values[-1] if values else 0,
            "is_risky": False,
        }

    values_list = list(values)
    previous_window = values_list[-6:-3] if len(values_list) >= 6 else values_list[:-3]
    recent_window = values_list[-3:]

    previous_avg = _safe_avg(previous_window)
    recent_avg = _safe_avg(recent_window)
    delta = recent_avg - previous_avg
    rate = values_list[-1] - values_list[-2]

    if delta >= min_change:
        direction = "Rising"
    elif delta <= -min_change:
        direction = "Falling"
    else:
        direction = "Stable"

    risky_direction = "Rising" if increasing_is_risky else "Falling"
    is_risky = direction == risky_direction

    return {
        "direction": direction,
        "delta": round(delta, 2),
        "rate": round(rate, 2),
        "recent_avg": round(recent_avg, 2),
        "previous_avg": round(previous_avg, 2),
        "is_risky": is_risky,
    }


def _volatility_index(hr_values, spo2_values, temp_values):
    """Estimate instability from recent fluctuations and normalize it to 0-100."""
    if len(hr_values) < 5 or len(spo2_values) < 5:
        return 20

    hr_volatility = pstdev(list(hr_values))
    spo2_volatility = pstdev(list(spo2_values))
    temp_volatility = pstdev(list(temp_values)) if len(temp_values) >= 5 else 0

    # Normalized lightweight score. It is intentionally simple and explainable for edge use.
    return round(_clamp((hr_volatility * 3.2) + (spo2_volatility * 13) + (temp_volatility * 25)), 1)


def _stability_status(hr_values, spo2_values, temp_values, fuzzy_score=0):
    """Estimate whether recent readings are stable, unstable, or critical."""
    if len(hr_values) < 5 or len(spo2_values) < 5:
        return "Collecting data"

    volatility = _volatility_index(hr_values, spo2_values, temp_values)

    if fuzzy_score >= 80:
        return "Critical"
    if volatility >= 55 or fuzzy_score >= 55:
        return "Unstable"
    return "Stable"


def _build_trend_flag(hr_trend, spo2_trend, temp_trend):
    trend_parts = []
    if hr_trend["direction"] != "Stable":
        trend_parts.append(f"Heart rate {hr_trend['direction'].lower()}")
    if spo2_trend["direction"] != "Stable":
        trend_parts.append(f"SpO2 {spo2_trend['direction'].lower()}")
    if temp_trend["direction"] != "Stable":
        trend_parts.append(f"Temperature {temp_trend['direction'].lower()}")
    return " + ".join(trend_parts) if trend_parts else "Stable"


def _profile_sensitivity(profile):
    """Add a small sensitivity factor for elderly or chronic-condition patients."""
    sensitivity = 0
    age = int(profile.get("age", 0) or 0)
    conditions = [str(c).lower() for c in profile.get("chronic_conditions", [])]

    if age >= 70:
        sensitivity += 8
    elif age >= 60:
        sensitivity += 4

    if any("heart" in c or "cardio" in c for c in conditions):
        sensitivity += 7
    if any("hypertension" in c or "blood pressure" in c for c in conditions):
        sensitivity += 4
    if any("respir" in c or "asthma" in c or "copd" in c for c in conditions):
        sensitivity += 5

    return min(sensitivity, 18)


def _fuzzy_risk_evaluation(hr, spo2, temp, acc, thresholds, hr_trend, spo2_trend, temp_trend, profile):
    """
    Fuzzy-inspired decision support layer.
    It transforms clinical inputs into gradual risk memberships, then combines them into one score.
    This is not a trained ML model; it is an explainable fuzzy-inspired edge AI layer.
    """
    high_hr = thresholds["high_hr"]
    low_spo2 = thresholds["low_spo2"]
    high_temp = thresholds["high_temp"]
    fall_acc = thresholds["fall_acceleration"]

    hr_risk = _linear_membership(hr, high_hr - 18, high_hr + 22)
    spo2_risk = _linear_membership(spo2, low_spo2 - 6, low_spo2 + 5, inverse=True)
    temp_risk = _linear_membership(temp, high_temp - 0.7, high_temp + 1.3)
    fall_risk = _linear_membership(acc, fall_acc - 0.7, fall_acc + 0.8)
    if acc > fall_acc:
        fall_risk = max(fall_risk, 75)

    trend_risk = 0
    if hr_trend["is_risky"]:
        trend_risk += min(35, abs(hr_trend["delta"]) * 5 + max(0, hr_trend["rate"]) * 2)
    if spo2_trend["is_risky"]:
        trend_risk += min(45, abs(spo2_trend["delta"]) * 14 + max(0, -spo2_trend["rate"]) * 8)
    if temp_trend["is_risky"]:
        trend_risk += min(20, abs(temp_trend["delta"]) * 20 + max(0, temp_trend["rate"]) * 15)
    trend_risk = round(_clamp(trend_risk), 1)

    correlated_deterioration = hr_trend["is_risky"] and spo2_trend["is_risky"]
    correlation_bonus = 12 if correlated_deterioration else 0
    sensitivity = _profile_sensitivity(profile)

    fuzzy_score = (
        hr_risk * 0.22
        + spo2_risk * 0.30
        + temp_risk * 0.08
        + fall_risk * 0.22
        + trend_risk * 0.18
        + correlation_bonus
        + sensitivity * 0.6
    )

    # Strong safety override: very severe single indicators should not be hidden by averaging.
    fuzzy_score = max(
        fuzzy_score,
        fall_risk * 0.85,
        spo2_risk * 0.78,
        hr_risk * 0.65,
    )

    fuzzy_score = round(_clamp(fuzzy_score), 1)

    breakdown = {
        "Heart Rate": round(hr_risk, 1),
        "SpO2": round(spo2_risk, 1),
        "Temperature": round(temp_risk, 1),
        "Fall": round(fall_risk, 1),
        "Trend": trend_risk,
        "Profile Sensitivity": round(sensitivity, 1),
    }

    return fuzzy_score, breakdown, correlated_deterioration


def _patient_state(fuzzy_score, early_warning_active=False):
    if fuzzy_score >= 80:
        return "Critical"
    if fuzzy_score >= 58:
        return "Deteriorating"
    if fuzzy_score >= 32 or early_warning_active:
        return "Observation Needed"
    return "Stable"


def _confidence_score(fuzzy_score, breakdown, history_length, correlated_deterioration):
    """Estimate how confident the system is in its current interpretation."""
    data_confidence = min(25, history_length * 4)
    signal_strength = min(25, fuzzy_score * 0.25)
    dominant_evidence = max(breakdown.values()) if breakdown else 0
    evidence_confidence = min(18, dominant_evidence * 0.18)
    correlation_confidence = 8 if correlated_deterioration else 0

    return round(_clamp(40 + data_confidence + signal_strength + evidence_confidence + correlation_confidence, 45, 95), 1)


def _stability_index(fuzzy_score, volatility):
    """Higher value means more stable patient state."""
    return round(_clamp(100 - (fuzzy_score * 0.65) - (volatility * 0.35)), 1)


def _build_fuzzy_explanation(fuzzy_score, breakdown, patient_state, confidence, hr_trend, spo2_trend, temp_trend, stability_index):
    dominant = sorted(breakdown.items(), key=lambda item: item[1], reverse=True)[:3]
    dominant_text = ", ".join([f"{name}: {value}%" for name, value in dominant])

    return (
        f"Fuzzy-inspired edge AI evaluation classified the patient state as {patient_state}. "
        f"Overall fuzzy risk score is {fuzzy_score}% with {confidence}% decision confidence. "
        f"The strongest contributing factors are {dominant_text}. "
        f"Temporal analysis indicates HR is {hr_trend['direction'].lower()}, "
        f"SpO2 is {spo2_trend['direction'].lower()}, and temperature is {temp_trend['direction'].lower()}. "
        f"Current stability index is {stability_index}%."
    )


def analyze(data: dict, profile: dict) -> dict:
    thresholds = get_personalized_thresholds(profile)

    # Legacy rule score is kept for backward compatibility with previous reports and logs.
    score = 0
    reasons = []
    actions = []
    early_warning = "No early deterioration pattern detected"

    hr = data["heart_rate"]
    spo2 = data["spo2"]
    temp = data["temperature"]
    acc = data["acceleration"]

    history_hr.append(hr)
    history_spo2.append(spo2)
    history_temp.append(temp)

    hr_trend = _trend_direction(history_hr, increasing_is_risky=True, min_change=3)
    spo2_trend = _trend_direction(history_spo2, increasing_is_risky=False, min_change=1)
    temp_trend = _trend_direction(history_temp, increasing_is_risky=True, min_change=0.3)
    trend_flag = _build_trend_flag(hr_trend, spo2_trend, temp_trend)

    fuzzy_score, fuzzy_breakdown, correlated_deterioration = _fuzzy_risk_evaluation(
        hr, spo2, temp, acc, thresholds, hr_trend, spo2_trend, temp_trend, profile
    )
    volatility = _volatility_index(history_hr, history_spo2, history_temp)
    stability_index = _stability_index(fuzzy_score, volatility)
    early_warning_active = False

    # Fall detection
    if acc > thresholds["fall_acceleration"]:
        score += 5
        reasons.append("High acceleration detected (possible fall)")

    # Low oxygen
    if spo2 < thresholds["low_spo2"]:
        score += 4
        reasons.append(f"Low SpO2 below personalized threshold (< {thresholds['low_spo2']}%)")

    # High heart rate
    if hr > thresholds["high_hr"]:
        score += 3
        reasons.append(f"High heart rate above personalized threshold (> {thresholds['high_hr']} bpm)")

    # Temperature
    if temp >= thresholds["high_temp"]:
        score += 1
        reasons.append("Elevated temperature")

    # Moving-average trend analysis.
    hr_near_risk = hr >= thresholds["high_hr"] - 10
    spo2_near_risk = spo2 <= thresholds["low_spo2"] + 4
    temp_near_risk = temp >= thresholds["high_temp"] - 0.5

    if hr_trend["is_risky"] and hr_near_risk:
        score += 1
        reasons.append(
            f"Heart rate rising over recent readings (avg change: +{hr_trend['delta']} bpm)"
        )

    if spo2_trend["is_risky"] and spo2_near_risk:
        score += 2
        reasons.append(
            f"Oxygen saturation falling over recent readings (avg change: {spo2_trend['delta']}%)"
        )

    if temp_trend["is_risky"] and temp_near_risk:
        score += 1
        reasons.append(
            f"Temperature rising over recent readings (avg change: +{temp_trend['delta']} °C)"
        )

    # Rate-of-change detection for rapid shifts.
    if hr_trend["rate"] >= 12 and hr_near_risk:
        score += 1
        reasons.append("Rapid heart-rate increase detected")

    if spo2_trend["rate"] <= -3 and spo2_near_risk:
        score += 1
        reasons.append("Rapid oxygen drop detected")

    # Correlated multi-sensor deterioration
    if correlated_deterioration and (hr_near_risk or spo2_near_risk or fuzzy_score >= 45):
        score += 3
        early_warning_active = True
        early_warning = "Possible physiological deterioration: HR rising while SpO2 is falling"
        reasons.append("Correlated deterioration pattern detected")

    # Fuzzy early warning: risk is not yet critical, but the pattern is moving toward risk.
    if 38 <= fuzzy_score < 70 and (fuzzy_breakdown["Trend"] >= 25 or fuzzy_breakdown["SpO2"] >= 45 or fuzzy_breakdown["Heart Rate"] >= 45):
        early_warning_active = True
        if early_warning == "No early deterioration pattern detected":
            early_warning = "Early warning: fuzzy risk pattern suggests possible deterioration"
        reasons.append("Fuzzy early-warning pattern detected")

    # Combined critical logic
    if acc > thresholds["fall_acceleration"] and (hr > thresholds["high_hr"] or spo2 < thresholds["low_spo2"]):
        score += 2
        reasons.append("Combined critical event after possible fall")

    patient_state = _patient_state(fuzzy_score, early_warning_active)
    stability = _stability_status(history_hr, history_spo2, history_temp, fuzzy_score)
    confidence = _confidence_score(fuzzy_score, fuzzy_breakdown, len(history_hr), correlated_deterioration)

    # Stability is kept as an explanatory indicator on the dashboard.
    if stability in ["Unstable", "Critical"] and (score > 0 or fuzzy_score >= 45):
        reasons.append("Unstable vital-sign pattern detected")

    # Final status uses the fuzzy layer while preserving previous safety thresholds.
    if fuzzy_score >= 78 or score >= 8 or patient_state == "Critical":
        status = "EMERGENCY"
        risk_level = "Critical"
        actions.append("Call emergency contact immediately")
        actions.append("Trigger high-priority alert")
    elif fuzzy_score >= 35 or score >= 3 or early_warning_active:
        status = "WARNING"
        risk_level = "Moderate"
        actions.append("Notify caregiver")
        actions.append("Continue close monitoring")
    else:
        status = "NORMAL"
        risk_level = "Low"
        actions.append("Continue monitoring")

    if status == "EMERGENCY":
        patient_state = "Critical"
    elif status == "WARNING" and patient_state == "Stable":
        patient_state = "Observation Needed"

    # Repeated alert escalation
    history_status.append(status)
    if len(history_status) >= 2 and history_status[-1] == "EMERGENCY" and history_status[-2] == "EMERGENCY":
        actions.append("Escalated due to repeated emergency pattern")

    if not reasons:
        reasons.append("Vitals stable within personalized thresholds")

    fuzzy_breakdown_text = " | ".join([f"{key}: {value}%" for key, value in fuzzy_breakdown.items()])

    smart_explanation = (
        f"Trend analysis: HR is {hr_trend['direction'].lower()}, "
        f"SpO2 is {spo2_trend['direction'].lower()}, and temperature is {temp_trend['direction'].lower()}. "
        f"Overall stability: {stability.lower()}."
    )

    ai_explanation = _build_fuzzy_explanation(
        fuzzy_score, fuzzy_breakdown, patient_state, confidence, hr_trend, spo2_trend, temp_trend, stability_index
    )

    reason_text = " + ".join(dict.fromkeys(reasons))
    action_text = " | ".join(actions)

    return {
        "status": status,
        "score": score,
        "risk_level": risk_level,
        "trend_flag": trend_flag,
        "hr_trend": hr_trend["direction"],
        "spo2_trend": spo2_trend["direction"],
        "temp_trend": temp_trend["direction"],
        "stability_status": stability,
        "stability_index": stability_index,
        "early_warning": early_warning,
        "patient_state": patient_state,
        "confidence_score": confidence,
        "fuzzy_risk_score": fuzzy_score,
        "fuzzy_breakdown": fuzzy_breakdown_text,
        "smart_explanation": smart_explanation,
        "ai_explanation": ai_explanation,
        "reason": reason_text,
        "action": action_text,
        "thresholds_used": thresholds,
    }
