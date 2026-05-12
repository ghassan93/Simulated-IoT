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
        print("Legacy Rule Score:", result["score"])
        print("Fuzzy Risk Score:", result.get("fuzzy_risk_score", result["score"]))
        print("Confidence Score:", result.get("confidence_score", "N/A"))
        print("Patient State:", result.get("patient_state", "Stable"))
        print("Status:", result["status"])
        print("Risk Level:", result["risk_level"])
        print("Trend:", result["trend_flag"])
        print("Stability:", result.get("stability_status", "Stable"))
        print("Stability Index:", result.get("stability_index", "N/A"))
        print("Early Warning:", result.get("early_warning", "No early deterioration pattern detected"))
        print("Smart Explanation:", result.get("smart_explanation", ""))
        print("AI Explanation:", result.get("ai_explanation", ""))
        print("Reason:", result["reason"])
        print("Suggested Action:", result["action"])
        print("-" * 60)

        time.sleep(delay)


if __name__ == "__main__":
    run_system()