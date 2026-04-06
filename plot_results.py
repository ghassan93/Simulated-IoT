import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output.csv")

# --- Heart Rate ---
plt.figure()
plt.plot(df["heart_rate"])
plt.title("Heart Rate Over Time")
plt.xlabel("Reading")
plt.ylabel("Heart Rate")
plt.grid()

# --- Score ---
plt.figure()
plt.plot(df["score"])
plt.title("Risk Score Over Time")
plt.xlabel("Reading")
plt.ylabel("Score")
plt.grid()

# --- Status Count ---
plt.figure()
df["status"].value_counts().plot(kind="bar")
plt.title("System Status Distribution")
plt.xlabel("Status")
plt.ylabel("Count")

plt.show()