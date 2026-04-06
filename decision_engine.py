from collections import deque

# Store last readings for trend analysis
history = deque(maxlen=5)

def analyze(data):
    score = 0
    reasons = []

    hr = data["heart_rate"]
    spo2 = data["spo2"]
    acc = data["acceleration"]

    # --- Rule 1: Fall Detection ---
    if acc > 2.5:
        score += 5
        reasons.append("High acceleration (possible fall)")

    # --- Rule 2: Oxygen Level ---
    if spo2 < 90:
        score += 4
        reasons.append("Low SpO2")

    # --- Rule 3: Heart Rate ---
    if hr > 120:
        score += 3
        reasons.append("High heart rate")

    # --- Trend Analysis ---
    history.append(hr)

    if len(history) >= 3:
        if history[-1] > history[-2] > history[-3]:
            score += 2
            reasons.append("Increasing heart rate trend")

    # --- Final Decision ---
    if score >= 7:
        status = "EMERGENCY"
    elif score >= 3:
        status = "WARNING"
    else:
        status = "NORMAL"

    # --- Explainability ---
    if not reasons:
        reasons.append("Vitals stable")

    return status, score, " + ".join(reasons)