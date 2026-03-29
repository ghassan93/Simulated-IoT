def analyze(data):
    if data["acceleration"] > 2.5:
        return "EMERGENCY", "Fall detected"

    if data["spo2"] < 90:
        return "EMERGENCY", "Low oxygen saturation"

    if data["heart_rate"] > 120:
        return "WARNING", "High heart rate"

    return "NORMAL", "Vitals within safe range"