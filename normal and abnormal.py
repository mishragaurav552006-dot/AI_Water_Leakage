import pandas as pd
import matplotlib.pyplot as plt

# Sample sensor data
data = {
    "Time": [
        "10:00", "10:01", "10:02", "10:03", "10:04",
        "10:05", "10:06", "10:07", "10:08", "10:09",
        "10:10", "10:11", "10:12", "10:13", "10:14"
    ],

    "Flow_Rate": [
        10.2, 10.0, 9.8, 10.3, 10.1,
        9.9, 8.5, 7.2, 6.5, 5.8,
        5.2, 4.9, 6.1, 9.7, 10.2
    ],

    "Status": [
        "Normal", "Normal", "Normal", "Normal", "Normal",
        "Normal", "Abnormal", "Abnormal", "Abnormal",
        "Abnormal", "Abnormal", "Abnormal", "Abnormal",
        "Normal", "Normal"
    ]
}

df = pd.DataFrame(data)

# Separate normal and abnormal readings
normal = df[df["Status"] == "Normal"]
abnormal = df[df["Status"] == "Abnormal"]

# Plot
plt.figure(figsize=(11, 6))

plt.plot(
    normal["Time"],
    normal["Flow_Rate"],
    marker="o",
    label="Normal Flow"
)

plt.plot(
    abnormal["Time"],
    abnormal["Flow_Rate"],
    marker="x",
    label="Abnormal / Leakage Flow"
)

plt.xlabel("Time")
plt.ylabel("Flow Rate (L/min)")
plt.title("Normal vs Abnormal: Time vs Flow Rate")

plt.legend()
plt.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()