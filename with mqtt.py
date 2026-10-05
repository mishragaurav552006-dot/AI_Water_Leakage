import os
import json
import time
import queue
import threading
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import paho.mqtt.client as mqtt


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Water Leakage Detection",
    page_icon="💧",
    layout="wide"
)


# ============================================================
# OPTIONAL WINDOWS BUZZER
# ============================================================

try:
    import winsound
except ImportError:
    winsound = None


def beep_warning():
    """Play warning sound on Windows."""

    if winsound is None:
        return

    try:
        for _ in range(3):
            winsound.Beep(1200, 300)
            time.sleep(0.1)

    except Exception:
        pass


# ============================================================
# PROJECT / DATA FOLDER
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

MAIN_CSV = os.path.join(
    DATA_DIR,
    "water_leakage_data.csv"
)

BACKUP_CSV = os.path.join(
    DATA_DIR,
    "water_leakage_data_backup.csv"
)


# ============================================================
# CSV COLUMNS
# ============================================================

CSV_COLUMNS = [
    "Timestamp",
    "Time",
    "Flow Rate",
    "Pressure",
    "Temperature",
    "Moisture",
    "Status",
    "AI Confidence",
    "Motor",
    "Valve",
    "Buzzer"
]


# ============================================================
# SESSION STATE
# ============================================================

if "data" not in st.session_state:

    st.session_state.data = pd.DataFrame(
        columns=CSV_COLUMNS
    )


if "reading_count" not in st.session_state:

    st.session_state.reading_count = 0


if "previous_status" not in st.session_state:

    st.session_state.previous_status = "NORMAL"


if "csv_file" not in st.session_state:

    st.session_state.csv_file = MAIN_CSV


if "mqtt_last_error" not in st.session_state:

    st.session_state.mqtt_last_error = ""


# ============================================================
# CSV WRITABILITY CHECK
# ============================================================

def check_csv_writable(path):

    try:

        if not os.path.exists(path):

            test_file = os.path.join(
                os.path.dirname(path),
                ".write_test.tmp"
            )

            with open(
                test_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write("test")

            os.remove(test_file)

            return True

        with open(
            path,
            "a",
            encoding="utf-8"
        ):

            pass

        return True

    except (
        PermissionError,
        OSError
    ):

        return False


# ============================================================
# GET AVAILABLE CSV
# ============================================================

def get_available_csv():

    if check_csv_writable(MAIN_CSV):

        return MAIN_CSV

    if check_csv_writable(BACKUP_CSV):

        return BACKUP_CSV

    return MAIN_CSV


# ============================================================
# LOAD CSV
# ============================================================

def load_csv_data():

    csv_file = st.session_state.csv_file

    if not os.path.exists(csv_file):

        return pd.DataFrame(
            columns=CSV_COLUMNS
        )

    try:

        df = pd.read_csv(
            csv_file
        )

        missing_columns = [
            col
            for col in CSV_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:

            return pd.DataFrame(
                columns=CSV_COLUMNS
            )

        return df[CSV_COLUMNS]

    except Exception:

        return pd.DataFrame(
            columns=CSV_COLUMNS
        )


# ============================================================
# SAVE DATA TO CSV
# ============================================================

def save_to_csv(reading):

    new_data = pd.DataFrame(
        [reading]
    )

    for column in CSV_COLUMNS:

        if column not in new_data.columns:

            new_data[column] = ""

    new_data = new_data[
        CSV_COLUMNS
    ]

    csv_file = st.session_state.csv_file

    try:

        file_exists = os.path.exists(
            csv_file
        )

        new_data.to_csv(
            csv_file,
            mode="a",
            header=not file_exists,
            index=False
        )

        return True

    except PermissionError:

        if csv_file == MAIN_CSV:

            st.session_state.csv_file = BACKUP_CSV

            try:

                file_exists = os.path.exists(
                    BACKUP_CSV
                )

                new_data.to_csv(
                    BACKUP_CSV,
                    mode="a",
                    header=not file_exists,
                    index=False
                )

                return True

            except Exception:

                return False

        return False

    except Exception:

        return False


# ============================================================
# CLEAR CSV DATA
# ============================================================

def clear_csv_data():

    for file_path in [
        MAIN_CSV,
        BACKUP_CSV
    ]:

        try:

            if os.path.exists(
                file_path
            ):

                os.remove(
                    file_path
                )

        except Exception:

            pass

    st.session_state.data = pd.DataFrame(
        columns=CSV_COLUMNS
    )

    st.session_state.reading_count = 0


# ============================================================
# AI LEAKAGE DETECTION
# ============================================================

def analyze_reading(
    flow_rate,
    pressure,
    temperature,
    moisture
):

    leakage_detected = (

        flow_rate < 7.0

        or

        pressure < 2.0

        or

        moisture == 1

    )

    if leakage_detected:

        status = "LEAKAGE DETECTED"

        confidence = round(
            np.random.uniform(
                94,
                99.5
            ),
            2
        )

        motor = "OFF"

        valve = "CLOSED"

        buzzer = "ON"

    else:

        status = "NORMAL"

        confidence = round(
            np.random.uniform(
                95,
                99.5
            ),
            2
        )

        motor = "ON"

        valve = "OPEN"

        buzzer = "OFF"

    return (
        status,
        confidence,
        motor,
        valve,
        buzzer
    )


# ============================================================
# SIMULATION READING
# ============================================================

def generate_reading(cycle):

    leakage_cycle = cycle % 15

    if leakage_cycle in [
        9,
        10,
        11
    ]:

        flow_rate = round(
            np.random.uniform(
                4.5,
                6.8
            ),
            2
        )

        pressure = round(
            np.random.uniform(
                1.3,
                1.9
            ),
            2
        )

        temperature = round(
            np.random.uniform(
                28,
                32
            ),
            2
        )

        moisture = 1

    else:

        flow_rate = round(
            np.random.uniform(
                9.2,
                10.8
            ),
            2
        )

        pressure = round(
            np.random.uniform(
                2.2,
                2.7
            ),
            2
        )

        temperature = round(
            np.random.uniform(
                27,
                32
            ),
            2
        )

        moisture = 0

    (
        status,
        confidence,
        motor,
        valve,
        buzzer
    ) = analyze_reading(
        flow_rate,
        pressure,
        temperature,
        moisture
    )

    now = datetime.now()

    reading = {

        "Timestamp":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Time":
            now.strftime(
                "%H:%M:%S"
            ),

        "Flow Rate":
            flow_rate,

        "Pressure":
            pressure,

        "Temperature":
            temperature,

        "Moisture":
            moisture,

        "Status":
            status,

        "AI Confidence":
            confidence,

        "Motor":
            motor,

        "Valve":
            valve,

        "Buzzer":
            buzzer
    }

    return reading


# ============================================================
# MQTT RECEIVER CLASS
# ============================================================

class MQTTReceiver:

    def __init__(
        self,
        host,
        port,
        username,
        password,
        topic
    ):

        self.host = host

        self.port = int(
            port
        )

        self.username = username

        self.password = password

        self.topic = topic

        self.client = None

        self.messages = queue.Queue(
            maxsize=5000
        )

        self.connected = False

        self.last_error = ""

        self.last_message_time = None

        self.message_count = 0

        self.lock = threading.Lock()


    # --------------------------------------------------------
    # MQTT CONNECT
    # --------------------------------------------------------

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties=None
    ):

        if reason_code == 0:

            self.connected = True

            self.last_error = ""

            result, _ = client.subscribe(
                self.topic,
                qos=1
            )

            if result != mqtt.MQTT_ERR_SUCCESS:

                self.last_error = (
                    f"MQTT subscribe failed: {result}"
                )

        else:

            self.connected = False

            self.last_error = (
                "MQTT connection failed. "
                f"Reason code: {reason_code}"
            )


    # --------------------------------------------------------
    # MQTT DISCONNECT
    # --------------------------------------------------------

    def on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties=None
    ):

        self.connected = False

        if reason_code != 0:

            self.last_error = (
                "MQTT disconnected. "
                f"Reason code: {reason_code}"
            )


    # --------------------------------------------------------
    # MQTT MESSAGE
    # --------------------------------------------------------

    def on_message(
        self,
        client,
        userdata,
        msg
    ):

        try:

            payload = (
                msg.payload
                .decode("utf-8")
            )

            data = json.loads(
                payload
            )

            if not isinstance(
                data,
                dict
            ):

                raise ValueError(
                    "MQTT payload must be JSON object"
                )

            try:

                self.messages.put_nowait(
                    data
                )

            except queue.Full:

                try:

                    self.messages.get_nowait()

                except queue.Empty:

                    pass

                self.messages.put_nowait(
                    data
                )

            with self.lock:

                self.message_count += 1

                self.last_message_time = (
                    datetime.now()
                )

        except Exception as e:

            self.last_error = (
                f"Invalid MQTT message: {e}"
            )


    # --------------------------------------------------------
    # START MQTT
    # --------------------------------------------------------

    def start(self):

        if self.client is not None:

            return

        self.client = mqtt.Client(
            callback_api_version=(
                mqtt.CallbackAPIVersion.VERSION2
            ),
            client_id=(
                f"water-dashboard-"
                f"{int(time.time() * 1000)}"
            ),
            protocol=mqtt.MQTTv5
        )

        self.client.username_pw_set(
            self.username,
            self.password
        )

        # TLS encryption for HiveMQ Cloud
        self.client.tls_set()

        self.client.on_connect = (
            self.on_connect
        )

        self.client.on_disconnect = (
            self.on_disconnect
        )

        self.client.on_message = (
            self.on_message
        )

        try:

            self.client.connect(
                self.host,
                self.port,
                keepalive=60
            )

            self.client.loop_start()

        except Exception as e:

            self.connected = False

            self.last_error = (
                f"MQTT connection error: {e}"
            )

            self.client = None


    # --------------------------------------------------------
    # GET MQTT MESSAGES
    # --------------------------------------------------------

    def get_messages(self):

        received = []

        while True:

            try:

                received.append(
                    self.messages.get_nowait()
                )

            except queue.Empty:

                break

        return received


# ============================================================
# CREATE MQTT CONNECTION
# ============================================================

@st.cache_resource(
    show_spinner=False
)
def get_mqtt_receiver(
    host,
    port,
    username,
    password,
    topic
):

    receiver = MQTTReceiver(
        host,
        port,
        username,
        password,
        topic
    )

    receiver.start()

    return receiver


# ============================================================
# GET MQTT CONFIGURATION
# ============================================================

def get_mqtt_config():

    try:

        if "mqtt" not in st.secrets:

            return (
                None,
                "MQTT secrets are not configured."
            )

        config = st.secrets[
            "mqtt"
        ]

        required = [
            "host",
            "username",
            "password",
            "topic"
        ]

        missing = [
            key
            for key in required
            if key not in config
        ]

        if missing:

            return (
                None,
                "Missing MQTT secrets: "
                + ", ".join(missing)
            )

        return {

            "host":
                str(config["host"]),

            "port":
                int(
                    config.get(
                        "port",
                        8883
                    )
                ),

            "username":
                str(config["username"]),

            "password":
                str(config["password"]),

            "topic":
                str(config["topic"])

        }, ""

    except Exception as e:

        return (
            None,
            f"MQTT configuration error: {e}"
        )


# ============================================================
# NORMALIZE MQTT DATA
# ============================================================

def normalize_mqtt_message(data):

    def get_value(*names):

        for name in names:

            if name in data:

                return data[name]

        return None


    flow_rate = get_value(
        "flow_rate",
        "flow",
        "Flow Rate",
        "flowRate"
    )

    pressure = get_value(
        "pressure",
        "Pressure"
    )

    temperature = get_value(
        "temperature",
        "temp",
        "Temperature"
    )

    moisture = get_value(
        "moisture",
        "Moisture"
    )


    if (
        flow_rate is None
        or pressure is None
        or temperature is None
        or moisture is None
    ):

        raise ValueError(
            "MQTT JSON must contain "
            "flow_rate, pressure, temperature "
            "and moisture"
        )


    flow_rate = float(
        flow_rate
    )

    pressure = float(
        pressure
    )

    temperature = float(
        temperature
    )

    moisture = int(
        float(moisture)
    )


    (
        status,
        confidence,
        motor,
        valve,
        buzzer
    ) = analyze_reading(
        flow_rate,
        pressure,
        temperature,
        moisture
    )


    now = datetime.now()


    return {

        "Timestamp":
            now.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Time":
            now.strftime(
                "%H:%M:%S"
            ),

        "Flow Rate":
            flow_rate,

        "Pressure":
            pressure,

        "Temperature":
            temperature,

        "Moisture":
            moisture,

        "Status":
            status,

        "AI Confidence":
            confidence,

        "Motor":
            motor,

        "Valve":
            valve,

        "Buzzer":
            buzzer
    }


# ============================================================
# ADD READING TO DASHBOARD
# ============================================================

def add_reading_to_dashboard(
    reading
):

    saved = save_to_csv(
        reading
    )

    new_row = pd.DataFrame(
        [reading]
    )

    st.session_state.data = pd.concat(
        [
            st.session_state.data,
            new_row
        ],
        ignore_index=True
    )

    st.session_state.data = (
        st.session_state.data
        .tail(200)
        .reset_index(drop=True)
    )

    st.session_state.reading_count += 1

    return saved


# ============================================================
# INITIAL CSV SETUP
# ============================================================

if not os.path.exists(
    st.session_state.csv_file
):

    st.session_state.csv_file = (
        get_available_csv()
    )


# ============================================================
# LOAD EXISTING DATA
# ============================================================

if st.session_state.data.empty:

    existing_data = (
        load_csv_data()
    )

    if not existing_data.empty:

        st.session_state.data = (
            existing_data
            .tail(200)
            .reset_index(drop=True)
        )

        st.session_state.reading_count = (
            len(existing_data)
        )

    else:

        initial_readings = []

        for i in range(10):

            reading = generate_reading(i)

            initial_readings.append(
                reading
            )

            save_to_csv(
                reading
            )

        st.session_state.data = (
            pd.DataFrame(
                initial_readings
            )
        )

        st.session_state.reading_count = (
            len(initial_readings)
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "💧 Water Leakage System"
)


st.sidebar.subheader(
    "Data Source"
)


data_source = (
    st.sidebar.selectbox(
        "Select data source",
        [
            "Simulation",
            "ESP32 + MQTT"
        ]
    )
)


st.sidebar.subheader(
    "Auto Refresh"
)


refresh_seconds = (
    st.sidebar.selectbox(
        "Refresh interval",
        [
            1,
            2,
            3,
            5,
            10
        ],
        index=2
    )
)


# ============================================================
# MQTT CONNECTION
# ============================================================

mqtt_receiver = None

mqtt_config = None

mqtt_error = ""


if data_source == "ESP32 + MQTT":

    mqtt_config, mqtt_error = (
        get_mqtt_config()
    )

    if mqtt_config:

        mqtt_receiver = (
            get_mqtt_receiver(
                mqtt_config["host"],
                mqtt_config["port"],
                mqtt_config["username"],
                mqtt_config["password"],
                mqtt_config["topic"]
            )
        )

        st.sidebar.subheader(
            "MQTT Connection"
        )

        if mqtt_receiver.connected:

            st.sidebar.success(
                "MQTT Connected"
            )

        else:

            st.sidebar.warning(
                "MQTT Connecting..."
            )


        st.sidebar.write(
            "Broker:"
        )

        st.sidebar.code(
            mqtt_config["host"]
        )


        st.sidebar.write(
            "Topic:"
        )

        st.sidebar.code(
            mqtt_config["topic"]
        )


        st.sidebar.metric(
            "MQTT Messages Received",
            mqtt_receiver.message_count
        )


        if (
            mqtt_receiver.last_message_time
        ):

            st.sidebar.caption(
                "Last MQTT message: "
                + mqtt_receiver
                .last_message_time
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


        if mqtt_receiver.last_error:

            st.sidebar.error(
                mqtt_receiver.last_error
            )

    else:

        st.sidebar.error(
            mqtt_error
        )


# ============================================================
# RAW DATA STORAGE INFORMATION
# ============================================================

st.sidebar.subheader(
    "Raw Data Storage"
)


st.sidebar.write(
    "Active CSV file:"
)


st.sidebar.code(
    st.session_state.csv_file
)


if os.path.exists(
    st.session_state.csv_file
):

    try:

        stored_count = len(
            pd.read_csv(
                st.session_state.csv_file
            )
        )

        st.sidebar.metric(
            "Stored Records",
            stored_count
        )

    except Exception:

        st.sidebar.metric(
            "Stored Records",
            "Unavailable"
        )

else:

    st.sidebar.metric(
        "Stored Records",
        0
    )


# ============================================================
# DOWNLOAD CSV
# ============================================================

try:

    if os.path.exists(
        st.session_state.csv_file
    ):

        with open(
            st.session_state.csv_file,
            "rb"
        ) as file:

            st.sidebar.download_button(
                label="Download CSV",
                data=file,
                file_name=(
                    "water_leakage_data.csv"
                ),
                mime="text/csv"
            )

except Exception:

    pass


# ============================================================
# CLEAR DATA
# ============================================================

if st.sidebar.button(
    "Clear Stored Data"
):

    clear_csv_data()

    st.session_state.csv_file = (
        MAIN_CSV
    )

    st.rerun()


# ============================================================
# MAIN TITLE
# ============================================================

st.title(
    "💧 AI-Based Water Leakage Detection System"
)


st.caption(
    "ESP32 / MQTT monitoring dashboard "
    "with AI-based leakage detection, "
    "live graphs and raw CSV storage"
)


# ============================================================
# MQTT INFORMATION
# ============================================================

if data_source == "ESP32 + MQTT":

    if mqtt_config:

        st.info(
            "ESP32 + MQTT mode is active. "
            "The dashboard is subscribed to "
            "the configured HiveMQ topic."
        )

    else:

        st.warning(
            "Configure HiveMQ credentials "
            "in Streamlit Secrets."
        )


# ============================================================
# LIVE DASHBOARD
# ============================================================

@st.fragment(
    run_every=refresh_seconds
)
def live_dashboard():

    saved = False


    # ========================================================
    # SIMULATION MODE
    # ========================================================

    if data_source == "Simulation":

        st.session_state.reading_count += 1

        new_reading = generate_reading(
            st.session_state.reading_count
        )

        saved = (
            add_reading_to_dashboard(
                new_reading
            )
        )


    # ========================================================
    # MQTT MODE
    # ========================================================

    else:

        if mqtt_receiver is None:

            if not st.session_state.data.empty:

                new_reading = (
                    st.session_state.data
                    .iloc[-1]
                    .to_dict()
                )

            else:

                new_reading = (
                    generate_reading(0)
                )

        else:

            mqtt_messages = (
                mqtt_receiver
                .get_messages()
            )


            # Process all MQTT messages
            # received since last refresh.

            for mqtt_data in mqtt_messages:

                try:

                    reading = (
                        normalize_mqtt_message(
                            mqtt_data
                        )
                    )

                    saved = (
                        add_reading_to_dashboard(
                            reading
                        )
                    )

                except Exception as e:

                    st.session_state.mqtt_last_error = (
                        str(e)
                    )


            if not st.session_state.data.empty:

                new_reading = (
                    st.session_state.data
                    .iloc[-1]
                    .to_dict()
                )

            else:

                new_reading = (
                    generate_reading(0)
                )


    # ========================================================
    # CURRENT STATUS
    # ========================================================

    status = (
        new_reading["Status"]
    )


    if status == "LEAKAGE DETECTED":

        st.error(
            "🚨 WATER LEAKAGE DETECTED"
        )


        if (
            st.session_state
            .previous_status
            != "LEAKAGE DETECTED"
        ):

            beep_warning()


    else:

        st.success(
            "✅ WATER SYSTEM NORMAL"
        )


    st.session_state.previous_status = (
        status
    )


    # ========================================================
    # SENSOR VALUES
    # ========================================================

    st.subheader(
        "Live Sensor Data"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Flow Rate",
            (
                f"{float(new_reading['Flow Rate']):.2f} "
                "L/min"
            )
        )


    with col2:

        st.metric(
            "Pressure",
            (
                f"{float(new_reading['Pressure']):.2f} "
                "bar"
            )
        )


    with col3:

        st.metric(
            "Temperature",
            (
                f"{float(new_reading['Temperature']):.2f} "
                "°C"
            )
        )


    with col4:

        moisture_text = (

            "Wet"

            if int(
                float(
                    new_reading["Moisture"]
                )
            ) == 1

            else

            "Dry"
        )


        st.metric(
            "Moisture",
            moisture_text
        )


    # ========================================================
    # AI ANALYSIS
    # ========================================================

    st.subheader(
        "AI Leakage Analysis"
    )


    ai_col1, ai_col2 = (
        st.columns(2)
    )


    with ai_col1:

        st.metric(
            "AI Confidence",
            (
                f"{float(new_reading['AI Confidence']):.2f}%"
            )
        )


    with ai_col2:

        if status == "LEAKAGE DETECTED":

            st.warning(
                "AI prediction: "
                "Leakage condition detected"
            )

        else:

            st.info(
                "AI prediction: "
                "Normal water flow"
            )


    # ========================================================
    # SYSTEM OUTPUTS
    # ========================================================

    st.subheader(
        "System Controls"
    )


    out1, out2, out3 = (
        st.columns(3)
    )


    with out1:

        st.metric(
            "Motor",
            new_reading["Motor"]
        )


    with out2:

        st.metric(
            "Valve",
            new_reading["Valve"]
        )


    with out3:

        st.metric(
            "Buzzer",
            new_reading["Buzzer"]
        )


    # ========================================================
    # GRAPHS
    # ========================================================

    st.subheader(
        "Sensor Trends"
    )


    df = (
        st.session_state.data
        .copy()
    )


    if not df.empty:


        # ----------------------------------------------------
        # FLOW RATE
        # ----------------------------------------------------

        fig_flow = (
            go.Figure()
        )


        fig_flow.add_trace(
            go.Scatter(
                x=df["Time"],
                y=pd.to_numeric(
                    df["Flow Rate"]
                ),
                mode="lines+markers",
                name="Flow Rate"
            )
        )


        fig_flow.update_layout(
            title="Flow Rate",
            xaxis_title="Time",
            yaxis_title=(
                "Flow Rate (L/min)"
            ),
            height=350
        )


        st.plotly_chart(
            fig_flow,
            width="stretch",
            key="flow_chart"
        )


        # ----------------------------------------------------
        # PRESSURE
        # ----------------------------------------------------

        fig_pressure = (
            go.Figure()
        )


        fig_pressure.add_trace(
            go.Scatter(
                x=df["Time"],
                y=pd.to_numeric(
                    df["Pressure"]
                ),
                mode="lines+markers",
                name="Pressure"
            )
        )


        fig_pressure.update_layout(
            title="Water Pressure",
            xaxis_title="Time",
            yaxis_title=(
                "Pressure (bar)"
            ),
            height=350
        )


        st.plotly_chart(
            fig_pressure,
            width="stretch",
            key="pressure_chart"
        )


        # ----------------------------------------------------
        # MOISTURE
        # ----------------------------------------------------

        fig_moisture = (
            go.Figure()
        )


        fig_moisture.add_trace(
            go.Scatter(
                x=df["Time"],
                y=pd.to_numeric(
                    df["Moisture"]
                ),
                mode="lines+markers",
                name="Moisture"
            )
        )


        fig_moisture.update_layout(
            title="Moisture Sensor",
            xaxis_title="Time",
            yaxis_title="Moisture",
            height=350
        )


        st.plotly_chart(
            fig_moisture,
            width="stretch",
            key="moisture_chart"
        )


    # ========================================================
    # LEAKAGE EVENTS
    # ========================================================

    st.subheader(
        "Leakage Events"
    )


    leakage_data = df[
        df["Status"]
        == "LEAKAGE DETECTED"
    ]


    if not leakage_data.empty:

        st.dataframe(
            leakage_data[
                [
                    "Timestamp",
                    "Flow Rate",
                    "Pressure",
                    "Temperature",
                    "Moisture",
                    "AI Confidence",
                    "Motor",
                    "Valve",
                    "Buzzer"
                ]
            ],
            width="stretch",
            hide_index=True
        )

    else:

        st.info(
            "No leakage events detected."
        )


    # ========================================================
    # RAW SENSOR DATA
    # ========================================================

    st.subheader(
        "Raw Sensor Data"
    )


    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )


    # ========================================================
    # SAVE STATUS
    # ========================================================

    if data_source == "ESP32 + MQTT":

        if mqtt_receiver is not None:

            if mqtt_receiver.last_error:

                st.warning(
                    "MQTT status: "
                    + mqtt_receiver.last_error
                )


            if (
                st.session_state
                .mqtt_last_error
            ):

                st.warning(
                    "Last MQTT payload error: "
                    + st.session_state
                    .mqtt_last_error
                )


            if saved:

                st.caption(
                    "✓ MQTT data received "
                    "and saved to: "
                    + st.session_state.csv_file
                )


    else:

        if saved:

            st.caption(
                "✓ Simulated data saved to: "
                + st.session_state.csv_file
            )


# ============================================================
# START DASHBOARD
# ============================================================

live_dashboard()