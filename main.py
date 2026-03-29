import time
from scenarios import generate_scenario
from decision_engine import analyze
from logger import init_logger, log_data

def run_system(iterations=20, delay=1):
    init_logger()

    for i in range(iterations):
        scenario, data = generate_scenario()
        status, message = analyze(data)
        log_data(scenario, data, status, message)

        print(f"Reading {i+1}")
        print("Scenario:", scenario)
        print("Data:", data)
        print("Status:", status)
        print("Message:", message)
        print("-" * 40)

        time.sleep(delay)

if __name__ == "__main__":
    run_system()