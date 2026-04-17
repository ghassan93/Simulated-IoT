import random


def generate_normal_data():
    return {
        "heart_rate": random.randint(65, 95),
        "spo2": random.randint(95, 100),
        "temperature": round(random.uniform(36.2, 37.3), 1),
        "acceleration": round(random.uniform(0.1, 1.0), 2)
    }


def generate_fall_data():
    return {
        "heart_rate": random.randint(90, 130),
        "spo2": random.randint(88, 96),
        "temperature": round(random.uniform(36.5, 38.0), 1),
        "acceleration": round(random.uniform(2.6, 4.0), 2)
    }


def generate_low_oxygen_data():
    return {
        "heart_rate": random.randint(80, 115),
        "spo2": random.randint(84, 89),
        "temperature": round(random.uniform(36.2, 37.5), 1),
        "acceleration": round(random.uniform(0.1, 1.2), 2)
    }


def generate_high_hr_data():
    return {
        "heart_rate": random.randint(121, 145),
        "spo2": random.randint(92, 99),
        "temperature": round(random.uniform(36.5, 37.8), 1),
        "acceleration": round(random.uniform(0.2, 1.0), 2)
    }


def generate_combined_critical_data():
    return {
        "heart_rate": random.randint(125, 150),
        "spo2": random.randint(84, 90),
        "temperature": round(random.uniform(37.5, 39.0), 1),
        "acceleration": round(random.uniform(2.6, 4.2), 2)
    }