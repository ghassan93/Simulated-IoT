import random
from sensor_simulation import (
    generate_normal_data,
    generate_fall_data,
    generate_low_oxygen_data,
    generate_high_hr_data,
    generate_combined_critical_data,
    generate_spo2_borderline_data,
    generate_gradual_deterioration_data,
)


SCENARIO_GENERATORS = {
    "normal": generate_normal_data,
    "fall": generate_fall_data,
    "low_oxygen": generate_low_oxygen_data,
    "high_hr": generate_high_hr_data,
    "combined_critical": generate_combined_critical_data,
    "spo2_borderline": generate_spo2_borderline_data,
    "gradual_deterioration": generate_gradual_deterioration_data,
}


SCENARIO_OPTIONS = [
    "Random",
    "normal",
    "fall",
    "low_oxygen",
    "high_hr",
    "combined_critical",
    "spo2_borderline",
    "gradual_deterioration",
]

SCENARIO_LABELS = {
    "Random": "Random mixed scenarios",
    "normal": "Normal stable condition",
    "fall": "Fall detection",
    "low_oxygen": "Low oxygen",
    "high_hr": "High heart rate",
    "combined_critical": "Combined critical event",
    "spo2_borderline": "Borderline SpO2",
    "gradual_deterioration": "Gradual deterioration",
}


def generate_scenario(selected_scenario="Random"):
    # Weighted selection keeps normal readings frequent while still testing critical and borderline cases.
    if selected_scenario and selected_scenario != "Random":
        if selected_scenario not in SCENARIO_GENERATORS:
            raise ValueError(f"Unknown scenario: {selected_scenario}")
        scenario = selected_scenario
    else:
        scenario = random.choices(
            population=list(SCENARIO_GENERATORS.keys()),
            weights=[35, 10, 14, 14, 9, 10, 8],
            k=1
        )[0]

    return scenario, SCENARIO_GENERATORS[scenario]()
