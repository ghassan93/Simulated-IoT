import json


def load_patient_profile(file_path="patient_data.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_personalized_thresholds(profile: dict) -> dict:
    age = profile.get("age", 65)
    conditions = [c.lower() for c in profile.get("chronic_conditions", [])]

    thresholds = {
        "high_hr": 120,
        "low_spo2": 90,
        "high_temp": 38.0,
        "fall_acceleration": 2.5
    }

    if age >= 70:
        thresholds["high_hr"] = 115
        thresholds["low_spo2"] = 91

    if "heart disease" in conditions:
        thresholds["high_hr"] = min(thresholds["high_hr"], 110)

    if "hypertension" in conditions:
        thresholds["high_hr"] = min(thresholds["high_hr"], 112)

    return thresholds