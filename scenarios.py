import random
from sensor_simulation import (
    generate_normal_data,
    generate_fall_data,
    generate_low_oxygen_data,
    generate_high_hr_data,
)

def generate_scenario():
    scenario = random.choice([
        "normal", "fall", "low_oxygen", "high_hr"
    ])

    if scenario == "normal":
        return scenario, generate_normal_data()
    if scenario == "fall":
        return scenario, generate_fall_data()
    if scenario == "low_oxygen":
        return scenario, generate_low_oxygen_data()
    return scenario, generate_high_hr_data()