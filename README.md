# SmartCare – Patient Health Monitoring System

A Python + Streamlit educational web application inspired by the topic:
**IoMT Patient Data Generation and Analysis**.

## Features
- Dashboard with patient and vital-reading summaries
- Patient registration (SQLite database)
- Health-reading entry (temperature, heart rate, blood pressure, SpO2)
- Illustrative threshold alerts
- Charts and CSV downloads
- Responsive browser interface suitable for laptop and mobile screens

## Requirements
- Python 3.10 or newer recommended
- VS Code (optional)
- Internet connection for first-time package installation

## Run on Windows
1. Extract `SmartCare_Project.zip`.
2. Open the extracted `SmartCare_Project` folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

5. A browser tab should open. If it does not, copy the local URL shown in the terminal (usually `http://localhost:8501`) into your browser.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Notes
- The app creates `data/smartcare.db` automatically on first run.
- It inserts a small set of fictional demo records the first time the database is empty.
- Readings and patients added through the interface are saved locally in SQLite.
- This is an educational demonstration, not a medical device. It is not connected to real sensors and must not be used for diagnosis or treatment.
- Alerts are based on simple illustrative thresholds and are not clinical advice.
