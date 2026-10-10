# Machine-Health-detector
Machine Health Monitoring and Early Failure Detection

Software prototype (Problem Statement 14): uses combined temperature, vibration, and sound measurements to determine early machinery failure.

Note: readings are dummy (or from a CSV file). They are not from actual sensors. The threshold values are only indicative and have to be calibrated for a particular machine.

Features
Live dashboard with graphs for temperature, vibration, and sound measurements
Health score of the machine (0-100)
Status of each parameter (Normal/Warning/Critical) and overall status (Healthy->Warning->Potential failure/Inspection required)
Early detection if a measurement value is increasing
Scenarios demonstrated: Normal, Overheating, Bearing wear, Imbalance, Potential failure
Adjustable thresholds, import from and export to a CSV file
Run
pip install -r requirements.txt
streamlit run app.py
Implementation details
health.py - sensor simulator, health score calculation, and rule-based status detection
app.py - Streamlit app

Health score = 100 minus a weighted sum of penalties (temperature 35%, vibration 40%, sound 25%). The penalty increases as a reading reaches its critical value. If two or more abnormal parameters detected: "Potential failure/Inspection required"

Future work

Real ESP32 sensors via USB serial and Wi-Fi/IoT uploading, ML-based anomaly detection in recorded data.
