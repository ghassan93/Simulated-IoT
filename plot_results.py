import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output.csv")

plt.figure(figsize=(8, 4))
plt.plot(df["heart_rate"], marker="o")
plt.title("Heart Rate Over Time")
plt.xlabel("Reading")
plt.ylabel("Heart Rate (bpm)")
plt.grid(True)

plt.figure(figsize=(8, 4))
plt.plot(df["spo2"], marker="o")
plt.title("SpO2 Over Time")
plt.xlabel("Reading")
plt.ylabel("SpO2 (%)")
plt.grid(True)

plt.figure(figsize=(8, 4))
plt.plot(df["score"], marker="o")
plt.title("Risk Score Over Time")
plt.xlabel("Reading")
plt.ylabel("Risk Score")
plt.grid(True)

plt.figure(figsize=(8, 4))
df["status"].value_counts().plot(kind="bar")
plt.title("Status Distribution")
plt.xlabel("Status")
plt.ylabel("Count")
plt.grid(axis="y")

plt.figure(figsize=(8, 4))
df["scenario"].value_counts().plot(kind="bar")
plt.title("Scenario Distribution")
plt.xlabel("Scenario")
plt.ylabel("Count")
plt.grid(axis="y")

plt.tight_layout()
plt.show()