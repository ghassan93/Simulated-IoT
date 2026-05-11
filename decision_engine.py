from collections import deque
from statistics import mean, pstdev
from patient_profile import get_personalized_thresholds

# Short rolling histories keep the logic lightweight and suitable for edge-based monitoring.
history_hr = deque(maxlen=6)
history_spo2 = deque(maxlen=6)
history_temp = deque(maxlen=6)
history_status = deque(maxlen=3)


def reset_trend_history():
    """Clear rolling histories when starting a new dashboard simulation session."""
    history_hr.clear()
    history_spo2.clear()
    history_temp.clear()
    history_status.clear()


def _safe_avg(values):
    return mean(values) if values else 0


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


def _stability_status(hr_values, spo2_values):
    """Estimate whether recent readings are stable or fluctuating."""
    if len(hr_values) < 5 or len(spo2_values) < 5:
        return "Collecting data"

    hr_volatility = pstdev(list(hr_values))
    spo2_volatility = pstdev(list(spo2_values))

    if hr_volatility >= 12 or spo2_volatility >= 3:
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


def analyze(data: dict, profile: dict) -> dict:
    thresholds = get_personalized_thresholds(profile)

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
    stability = _stability_status(history_hr, history_spo2)
    trend_flag = _build_trend_flag(hr_trend, spo2_trend, temp_trend)

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
    # Trend scores are applied only when the current reading is near a clinical boundary.
    # This prevents old critical readings in the simulation from over-penalizing a new normal reading.
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
    # The rapid-change rule is applied only when it matches the current risk context,
    # to avoid confusing explanations after sudden scenario changes in the simulation.
    if hr_trend["rate"] >= 12 and hr_near_risk:
        score += 1
        reasons.append("Rapid heart-rate increase detected")

    if spo2_trend["rate"] <= -3 and spo2_near_risk:
        score += 1
        reasons.append("Rapid oxygen drop detected")

    # Correlated multi-sensor deterioration
    if hr_trend["is_risky"] and spo2_trend["is_risky"] and hr_near_risk and spo2_near_risk:
        score += 3
        early_warning = "Possible physiological deterioration: HR rising while SpO2 is falling"
        reasons.append("Correlated deterioration pattern detected")

    # Combined critical logic
    if acc > thresholds["fall_acceleration"] and (hr > thresholds["high_hr"] or spo2 < thresholds["low_spo2"]):
        score += 2
        reasons.append("Combined critical event after possible fall")

    # Stability is kept as an explanatory indicator on the dashboard.
    # It is not enough alone to raise the risk score unless another abnormal pattern exists.
    if stability == "Unstable" and score > 0:
        reasons.append("Unstable vital-sign pattern detected")

    # Final status
    if score >= 8:
        status = "EMERGENCY"
        risk_level = "Critical"
        actions.append("Call emergency contact immediately")
        actions.append("Trigger high-priority alert")
    elif score >= 3:
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
        reasons.append("Vitals stable within personalized thresholds")

    smart_explanation = (
        f"Trend analysis: HR is {hr_trend['direction'].lower()}, "
        f"SpO2 is {spo2_trend['direction'].lower()}, and temperature is {temp_trend['direction'].lower()}. "
        f"Overall stability: {stability.lower()}."
    )

    reason_text = " + ".join(reasons)
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
        "early_warning": early_warning,
        "smart_explanation": smart_explanation,
        "reason": reason_text,
        "action": action_text,
        "thresholds_used": thresholds,
    }
