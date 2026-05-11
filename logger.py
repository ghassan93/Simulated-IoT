import csv
import os
from datetime import datetime

FILE_NAME = "output.csv"

FIELDNAMES = [
    "timestamp",
    "patient_id",
    "scenario",
    "heart_rate",
    "spo2",
    "temperature",
    "acceleration",
    "score",
    "status",
    "risk_level",
    "trend_flag",
    "hr_trend",
    "spo2_trend",
    "temp_trend",
    "stability_status",
    "early_warning",
    "smart_explanation",
    "reason",
    "action",
]


def init_logger():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            current_header = next(reader, [])

        if current_header == FIELDNAMES:
            return

        backup_name = f"output_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        os.replace(FILE_NAME, backup_name)

    with open(FILE_NAME, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()


def log_data(profile: dict, scenario: str, data: dict, result: dict):
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient_id": profile.get("patient_id", "Unknown"),
        "scenario": scenario,
        "heart_rate": data["heart_rate"],
        "spo2": data["spo2"],
        "temperature": data["temperature"],
        "acceleration": data["acceleration"],
        "score": result["score"],
        "status": result["status"],
        "risk_level": result["risk_level"],
        "trend_flag": result["trend_flag"],
        "hr_trend": result.get("hr_trend", "Stable"),
        "spo2_trend": result.get("spo2_trend", "Stable"),
        "temp_trend": result.get("temp_trend", "Stable"),
        "stability_status": result.get("stability_status", "Stable"),
        "early_warning": result.get("early_warning", "No early deterioration pattern detected"),
        "smart_explanation": result.get("smart_explanation", ""),
        "reason": result["reason"],
        "action": result["action"],
    }

    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)
