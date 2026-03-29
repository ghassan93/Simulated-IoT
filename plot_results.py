import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output.csv")

plt.figure(figsize=(8, 4))
plt.plot(df.index, df["heart_rate"], marker="o")
plt.title("Heart Rate Readings Over Time")
plt.xlabel("Reading Index")
plt.ylabel("Heart Rate (bpm)")
plt.grid(True)
plt.tight_layout()
plt.show()