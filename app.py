import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import numpy as np

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "data" / "smartcare.db"
DB_PATH.parent.mkdir(exist_ok=True)

st.set_page_config(page_title="SmartCare | Patient Monitoring", page_icon="🏥", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
:root { --navy:#14243a; --teal:#16a6a1; --muted:#718096; }
.stApp { background: #f4f7fb; }
[data-testid="stSidebar"] { background: #14243a; }
[data-testid="stSidebar"] * { color: #f5f8fc !important; }
.block-container { padding-top: 1.7rem; padding-bottom: 2rem; max-width: 1400px; }
.hero { background: linear-gradient(120deg,#14243a,#20516a); padding: 25px 28px; border-radius: 18px; color: white; margin-bottom: 18px; }
.hero h1 { color:white; margin:0; font-size:2rem; }
.hero p { color:#d8e7ef; margin:6px 0 0 0; }
.metric-card { background:white; padding:18px 20px; border:1px solid #e6edf4; border-radius:15px; box-shadow:0 4px 16px rgba(20,36,58,.04); }
.metric-label { color:#718096; font-size:.85rem; }
.metric-value { color:#14243a; font-size:1.65rem; font-weight:700; margin-top:5px; }
.section-title { color:#14243a; font-size:1.2rem; font-weight:700; margin:12px 0; }
.small-note { color:#718096; font-size:.82rem; }
div.stButton > button { border-radius:10px; border:0; background:#16a6a1; color:white; font-weight:600; }
div.stButton > button:hover { background:#118783; color:white; }
</style>
""", unsafe_allow_html=True)

# ---------- Database ----------
def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            created_at TEXT NOT NULL
        )""")
        con.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT NOT NULL,
            temperature REAL NOT NULL,
            heart_rate INTEGER NOT NULL,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            spo2 INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY(patient_code) REFERENCES patients(patient_code)
        )""")

def get_patients():
    with connect() as con:
        return pd.read_sql_query("SELECT * FROM patients ORDER BY id DESC", con)

def get_readings():
    with connect() as con:
        return pd.read_sql_query("""
        SELECT r.*, p.name FROM readings r
        LEFT JOIN patients p ON p.patient_code=r.patient_code
        ORDER BY r.id DESC
        """, con)

def seed_demo():
    if len(get_patients()) == 0:
        demo = [
            ("SC001","Aarav Sharma",24,"Male"),
            ("SC002","Priya Singh",29,"Female"),
            ("SC003","Kabir Das",35,"Male"),
            ("SC004","Ananya Roy",21,"Female"),
            ("SC005","Meera Kumari",42,"Female"),
        ]
        with connect() as con:
            for code,name,age,gender in demo:
                con.execute("INSERT INTO patients(patient_code,name,age,gender,created_at) VALUES(?,?,?,?,?)",
                            (code,name,age,gender,datetime.now().strftime("%Y-%m-%d %H:%M")))
            readings = [
                ("SC001",98.6,74,118,76,98),
                ("SC002",99.0,82,122,80,97),
                ("SC003",98.4,88,128,84,96),
                ("SC004",98.2,72,110,72,99),
                ("SC005",100.1,96,135,88,95),
            ]
            for row in readings:
                con.execute("""INSERT INTO readings(patient_code,temperature,heart_rate,systolic,diastolic,spo2,recorded_at)
                VALUES(?,?,?,?,?,?,?)""", (*row,datetime.now().strftime("%Y-%m-%d %H:%M")))

init_db()
seed_demo()

# ---------- Helpers ----------
def classify_reading(row):
    flags = []
    # Broad demo thresholds only; not medical advice or diagnosis.
    if row["temperature"] >= 100.4: flags.append("Temperature above demo threshold")
    if row["heart_rate"] < 50 or row["heart_rate"] > 120: flags.append("Heart rate outside demo range")
    if row["spo2"] < 94: flags.append("SpO₂ below demo threshold")
    if row["systolic"] >= 140 or row["diastolic"] >= 90: flags.append("BP above demo threshold")
    return flags

patients = get_patients()
readings = get_readings()

# ---------- Sidebar ----------
st.sidebar.markdown("## 🏥 SmartCare")
st.sidebar.caption("Patient Health Monitoring")
page = st.sidebar.radio("NAVIGATION", ["Dashboard", "Patients", "Add Patient", "Health Monitoring", "Analysis & Reports", "About"])
st.sidebar.markdown("---")
st.sidebar.caption("Educational demo • Sample data")
st.sidebar.caption("Not for medical diagnosis")

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>SmartCare Health Portal</h1>
  <p>Patient records, health readings and data insights in one place.</p>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    patients = get_patients()
    readings = get_readings()
    latest = readings.drop_duplicates("patient_code") if not readings.empty else readings
    avg_hr = round(latest["heart_rate"].mean(),1) if not latest.empty else 0
    avg_temp = round(latest["temperature"].mean(),1) if not latest.empty else 0
    avg_spo2 = round(latest["spo2"].mean(),1) if not latest.empty else 0

    c1,c2,c3,c4 = st.columns(4)
    metrics = [("Total patients",len(patients)),("Avg. heart rate",f"{avg_hr} bpm"),("Avg. temperature",f"{avg_temp} °F"),("Avg. SpO₂",f"{avg_spo2}%")]
    for col,(label,value) in zip([c1,c2,c3,c4],metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">Recent patient readings</div>',unsafe_allow_html=True)
    if not readings.empty:
        st.dataframe(readings[["patient_code","name","temperature","heart_rate","systolic","diastolic","spo2","recorded_at"]].head(8),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No readings have been added yet.")
    st.markdown('<div class="section-title">Latest heart-rate overview</div>',unsafe_allow_html=True)
    if not latest.empty:
        chart = latest.set_index("name")[["heart_rate"]]
        st.bar_chart(chart, use_container_width=True)
    st.info("Demo dashboard uses illustrative sample readings. It is not connected to real medical devices.")

elif page == "Patients":
    patients = get_patients()
    st.subheader("Patient Directory")
    st.write("Registered patient records.")
    if patients.empty:
        st.info("No patients registered yet.")
    else:
        st.dataframe(patients[["patient_code","name","age","gender","created_at"]],
                     use_container_width=True, hide_index=True)
        selected = st.selectbox("Select a patient to view their record", patients["patient_code"].tolist())
        p = patients[patients.patient_code == selected].iloc[0]
        st.markdown(f"**Patient:** {p['name']}  ·  **Code:** {p['patient_code']}  ·  **Age:** {p['age']}")

elif page == "Add Patient":
    st.subheader("Register a Patient")
    with st.form("patient_form", clear_on_submit=True):
        a,b = st.columns(2)
        code = a.text_input("Patient ID", placeholder="e.g. SC006")
        name = b.text_input("Full name")
        age = a.number_input("Age", min_value=0, max_value=120, value=20)
        gender = b.selectbox("Gender", ["Prefer not to say","Female","Male","Other"])
        submitted = st.form_submit_button("Save patient")
        if submitted:
            if not code.strip() or not name.strip():
                st.error("Please enter both Patient ID and name.")
            else:
                try:
                    with connect() as con:
                        con.execute("INSERT INTO patients(patient_code,name,age,gender,created_at) VALUES(?,?,?,?,?)",
                                    (code.strip().upper(),name.strip(),int(age),gender,datetime.now().strftime("%Y-%m-%d %H:%M")))
                    st.success(f"Patient {name} added successfully.")
                except sqlite3.IntegrityError:
                    st.error("This Patient ID already exists. Please use a different ID.")

elif page == "Health Monitoring":
    st.subheader("Add Health Reading")
    patients = get_patients()
    if patients.empty:
        st.warning("Add a patient first.")
    else:
        with st.form("reading_form", clear_on_submit=True):
            code = st.selectbox("Patient", patients["patient_code"].tolist(),
                                format_func=lambda x: f"{x} — {patients.loc[patients.patient_code==x,'name'].iloc[0]}")
            a,b = st.columns(2)
            temp = a.number_input("Temperature (°F)", min_value=85.0, max_value=110.0, value=98.6, step=0.1)
            hr = b.number_input("Heart rate (bpm)", min_value=20, max_value=250, value=75)
            systolic = a.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, value=120)
            diastolic = b.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, value=80)
            spo2 = a.number_input("SpO₂ (%)", min_value=50, max_value=100, value=98)
            save = st.form_submit_button("Save reading")
            if save:
                with connect() as con:
                    con.execute("""INSERT INTO readings(patient_code,temperature,heart_rate,systolic,diastolic,spo2,recorded_at)
                    VALUES(?,?,?,?,?,?,?)""",(code,float(temp),int(hr),int(systolic),int(diastolic),int(spo2),datetime.now().strftime("%Y-%m-%d %H:%M")))
                st.success("Reading saved.")
                newrow = {"temperature":temp,"heart_rate":hr,"systolic":systolic,"diastolic":diastolic,"spo2":spo2}
                flags = classify_reading(newrow)
                if flags:
                    st.warning("Demo alert: " + " • ".join(flags))
                else:
                    st.success("No demo threshold alerts for this reading.")

    st.markdown("---")
    st.markdown("**Latest readings**")
    readings = get_readings()
    if not readings.empty:
        st.dataframe(readings[["patient_code","name","temperature","heart_rate","systolic","diastolic","spo2","recorded_at"]].head(20),
                     use_container_width=True, hide_index=True)

elif page == "Analysis & Reports":
    st.subheader("Analysis & Reports")
    readings = get_readings()
    if readings.empty:
        st.info("No readings available for analysis.")
    else:
        st.caption("Charts summarize the saved sample readings. Thresholds are illustrative only.")
        a,b = st.columns(2)
        with a:
            st.markdown("**Heart rate by patient**")
            st.bar_chart(readings.groupby("name")["heart_rate"].mean())
        with b:
            st.markdown("**Temperature by patient**")
            st.bar_chart(readings.groupby("name")["temperature"].mean())
        st.markdown("**Oxygen saturation readings**")
        st.line_chart(readings[["spo2"]].reset_index(drop=True))
        csv = readings.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download readings as CSV", data=csv,
                           file_name="smartcare_patient_readings.csv", mime="text/csv")
        p_csv = get_patients().to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download patient directory", data=p_csv,
                           file_name="smartcare_patients.csv", mime="text/csv")

elif page == "About":
    st.subheader("About SmartCare")
    st.write("""
    SmartCare is a Python-based educational web application inspired by the
    Internet of Medical Things (IoMT). It demonstrates how sample patient
    information and vital-sign readings can be stored, summarized and visualized.
    """)
    st.markdown("**Main technologies:** Python, Streamlit, Pandas, NumPy, Matplotlib and SQLite.")
    st.warning("This application uses sample/demo data. It is not a medical device, does not provide diagnosis, and should not be used for treatment decisions.")

st.markdown("---")
st.caption("SmartCare • Educational IoMT data-generation and analysis project")
