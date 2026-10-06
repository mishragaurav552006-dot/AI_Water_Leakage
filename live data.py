import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
from datetime import datetime

# Lists to store raw data
time_data = []
flow_data = []

# Create figure
fig, ax = plt.subplots()

def update(frame):
    # -------- Replace this with actual sensor/MQTT data --------
    flow_rate = random.uniform(5, 12)   # Simulated raw flow rate (L/min)
    
    current_time = datetime.now().strftime("%H:%M:%S")

    # Store raw data
    time_data.append(current_time)
    flow_data.append(flow_rate)

    # Keep only latest 30 readings
    if len(time_data) > 30:
        time_data.pop(0)
        flow_data.pop(0)

    # Clear and redraw graph
    ax.clear()
    ax.plot(time_data, flow_data, marker='o')

    ax.set_title("Live Raw Data: Time vs Flow Rate")
    ax.set_xlabel("Time")
    ax.set_ylabel("Flow Rate (L/min)")
    ax.grid(True)

    # Rotate time labels
    plt.xticks(rotation=45)

# Update every 1 second
ani = FuncAnimation(fig, update, interval=1000)

plt.tight_layout()
plt.show()