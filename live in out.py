import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
from datetime import datetime

# Store live data
time_data = []
flow_data = []
status_data = []

fig, ax = plt.subplots()

def update(frame):

    # -------- LIVE INPUT --------
    # Replace this with actual ESP32/MQTT flow-rate data
    flow_rate = random.uniform(4, 12)

    current_time = datetime.now().strftime("%H:%M:%S")

    # -------- AI OUTPUT --------
    # Example leakage detection rule
    if flow_rate < 7:
        status = "Abnormal"
    else:
        status = "Normal"

    # Store data
    time_data.append(current_time)
    flow_data.append(flow_rate)
    status_data.append(status)

    # Keep latest 30 readings
    if len(time_data) > 30:
        time_data.pop(0)
        flow_data.pop(0)
        status_data.pop(0)

    # Clear graph
    ax.clear()

    # Plot flow rate
    ax.plot(
        time_data,
        flow_data,
        marker="o",
        label="Flow Rate (L/min)"
    )

    # Mark abnormal points
    for i in range(len(time_data)):
        if status_data[i] == "Abnormal":
            ax.scatter(
                time_data[i],
                flow_data[i],
                marker="x",
                s=80,
                label="Leakage" if i == status_data.index("Abnormal") else ""
            )

    ax.set_title("Live Water Leakage Detection")
    ax.set_xlabel("Time")
    ax.set_ylabel("Flow Rate (L/min)")
    ax.legend()
    ax.grid(True)

    plt.xticks(rotation=45)


# Update every 1 second
ani = FuncAnimation(
    fig,
    update,
    interval=1000
)

plt.tight_layout()
plt.show()