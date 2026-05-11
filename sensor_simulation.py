import random


def _jitter(value, spread, min_value=None, max_value=None, digits=1):
    noisy_value = value + random.uniform(-spread, spread)
    if min_value is not None:
        noisy_value = max(min_value, noisy_value)
    if max_value is not None:
        noisy_value = min(max_value, noisy_value)
    return round(noisy_value, digits)


def generate_normal_data():
    return {
        "heart_rate": int(_jitter(random.randint(65, 95), 2, 55, 105, 0)),
        "spo2": int(_jitter(random.randint(95, 100), 1, 93, 100, 0)),
        "temperature": _jitter(random.uniform(36.2, 37.3), 0.15, 35.8, 37.8, 1),
        "acceleration": _jitter(random.uniform(0.1, 1.0), 0.08, 0.0, 1.5, 2)
    }


def generate_fall_data():
    return {
        "heart_rate": int(_jitter(random.randint(90, 130), 4, 80, 145, 0)),
        "spo2": int(_jitter(random.randint(88, 96), 2, 84, 98, 0)),
        "temperature": _jitter(random.uniform(36.5, 38.0), 0.2, 36.0, 38.4, 1),
        "acceleration": _jitter(random.uniform(2.6, 4.0), 0.15, 2.4, 4.5, 2)
    }


def generate_low_oxygen_data():
    return {
        "heart_rate": int(_jitter(random.randint(80, 115), 3, 70, 125, 0)),
        "spo2": int(_jitter(random.randint(84, 89), 1.5, 82, 92, 0)),
        "temperature": _jitter(random.uniform(36.2, 37.5), 0.15, 36.0, 37.9, 1),
        "acceleration": _jitter(random.uniform(0.1, 1.2), 0.08, 0.0, 1.6, 2)
    }


def generate_high_hr_data():
    return {
        "heart_rate": int(_jitter(random.randint(121, 145), 4, 110, 155, 0)),
        "spo2": int(_jitter(random.randint(92, 99), 1.5, 89, 100, 0)),
        "temperature": _jitter(random.uniform(36.5, 37.8), 0.15, 36.1, 38.1, 1),
        "acceleration": _jitter(random.uniform(0.2, 1.0), 0.08, 0.0, 1.4, 2)
    }


def generate_combined_critical_data():
    return {
        "heart_rate": int(_jitter(random.randint(125, 150), 5, 115, 160, 0)),
        "spo2": int(_jitter(random.randint(84, 90), 2, 80, 92, 0)),
        "temperature": _jitter(random.uniform(37.5, 39.0), 0.25, 37.0, 39.5, 1),
        "acceleration": _jitter(random.uniform(2.6, 4.2), 0.2, 2.3, 4.7, 2)
    }


def generate_spo2_borderline_data():
    """Borderline readings test whether personalized thresholds catch early risk."""
    return {
        "heart_rate": int(_jitter(random.randint(98, 116), 3, 90, 125, 0)),
        "spo2": int(_jitter(random.randint(90, 93), 1.2, 88, 95, 0)),
        "temperature": _jitter(random.uniform(36.4, 37.6), 0.15, 36.0, 38.0, 1),
        "acceleration": _jitter(random.uniform(0.2, 1.2), 0.08, 0.0, 1.5, 2)
    }


def generate_gradual_deterioration_data():
    """Simulates early deterioration with rising HR and falling SpO2 before extreme values appear."""
    return {
        "heart_rate": int(_jitter(random.randint(104, 122), 3, 95, 132, 0)),
        "spo2": int(_jitter(random.randint(89, 94), 1.2, 86, 96, 0)),
        "temperature": _jitter(random.uniform(36.8, 38.2), 0.2, 36.3, 38.5, 1),
        "acceleration": _jitter(random.uniform(0.3, 1.4), 0.1, 0.0, 1.8, 2)
    }
