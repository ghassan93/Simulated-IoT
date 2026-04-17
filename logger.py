import csv
import os
from datetime import datetime

FILE_NAME = "output.csv"


def init_logger():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
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
                "reason",
                "action"
            ])


def log_data(profile: dict, scenario: str, data: dict, result: dict):
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            profile.get("patient_id", "Unknown"),
            scenario,
            data["heart_rate"],
            data["spo2"],
            data["temperature"],
            data["acceleration"],
            result["score"],
            result["status"],
            result["risk_level"],
            result["trend_flag"],
            result["reason"],
            result["action"]
        ])