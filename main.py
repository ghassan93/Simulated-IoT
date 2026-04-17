import time
from scenarios import generate_scenario
from decision_engine import analyze
from logger import init_logger, log_data
from patient_profile import load_patient_profile


def run_system(iterations=25, delay=1):
    profile = load_patient_profile()
    init_logger()

    print("=" * 60)
    print("Starting Edge-Based Elderly Monitoring System")
    print("Patient:", profile["name"])
    print("Conditions:", ", ".join(profile["chronic_conditions"]))
    print("=" * 60)

    for i in range(iterations):
        scenario, data = generate_scenario()
        result = analyze(data, profile)
        log_data(profile, scenario, data, result)

        print(f"Reading {i+1}")
        print("Scenario:", scenario)
        print("Data:", data)
        print("Score:", result["score"])
        print("Status:", result["status"])
        print("Risk Level:", result["risk_level"])
        print("Trend:", result["trend_flag"])
        print("Reason:", result["reason"])
        print("Suggested Action:", result["action"])
        print("-" * 60)

        time.sleep(delay)


if __name__ == "__main__":
    run_system()