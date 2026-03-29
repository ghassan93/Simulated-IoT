import csv
import os

FILE_NAME = "output.csv"

def init_logger():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "scenario",
                "heart_rate",
                "spo2",
                "temperature",
                "acceleration",
                "status",
                "message"
            ])

def log_data(scenario, data, status, message):
    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            scenario,
            data["heart_rate"],
            data["spo2"],
            data["temperature"],
            data["acceleration"],
            status,
            message
        ])