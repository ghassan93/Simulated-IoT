import time
from scenarios import generate_scenario
from decision_engine import analyze
from logger import init_logger, log_data

def run_system(iterations=20, delay=1):
    init_logger()

    for i in range(iterations):
        scenario, data = generate_scenario()

        status, score, reason = analyze(data)

        log_data(scenario, data, score, status, reason)

        print(f"Reading {i+1}")
        print("Scenario:", scenario)
        print("Data:", data)
        print("Score:", score)
        print("Status:", status)
        print("Reason:", reason)
        print("-" * 50)

        time.sleep(delay)

if __name__ == "__main__":
    run_system()