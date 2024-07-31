import streamlit as st
import sqlite3
from sqlite3 import Error

import pickle



import numpy as np

o2 =  {'Obesity_Type_I': 0,
  'Obesity_Type_III': 1,
  'Obesity_Type_II': 2,
  'Overweight_Level_I': 3,
  'Overweight_Level_II': 4,
  'Normal_Weight': 5,
  'Insufficient_Weight': 6}



with open('std.pkl', 'rb') as file:
    scaler = pickle.load(file)

with open('lir.pkl', 'rb') as file:
    lir = pickle.load(file)

with open('std2.pkl', 'rb') as file:
    scaler2 = pickle.load(file)


with open('rfc2.pkl', 'rb') as file:
    rf2 = pickle.load(file)



# Function to create a connection to the SQLite database
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('patients.db')
    except Error as e:
        st.error(f"Error: {e}")
    return conn

# Function to create patients table
def create_table():
    conn = create_connection()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        phone TEXT NOT NULL,
                        disease TEXT NOT NULL,
                        status TEXT NOT NULL
                        );''')
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to add a new patient
def add_patient(name, age, phone, disease):
    conn = create_connection()
    try:
        sql = '''INSERT INTO patients (name, age, phone, disease, status)
                 VALUES (?, ?, ?, ?, ?);'''
        cur = conn.cursor()
        cur.execute(sql, (name, age, phone, disease, 'Pending'))
        conn.commit()
        st.success("Patient added successfully!")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to fetch all patients
def fetch_patients():
    conn = create_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients")
        rows = cur.fetchall()
        return rows
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to fetch patients by name filter
def fetch_patients_by_name(name_filter):
    conn = create_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM patients WHERE name LIKE ?", ('%' + name_filter + '%',))
        rows = cur.fetchall()
        return rows
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to update patient status
def update_status(patient_id, status):
    conn = create_connection()
    try:
        sql = '''UPDATE patients
                 SET status = ?
                 WHERE id = ?;'''
        cur = conn.cursor()
        cur.execute(sql, (status, patient_id))
        conn.commit()
        st.success("Patient status updated successfully!")
    except Error as e:
        st.error(f"Error: {e}")
    finally:
        if conn:
            conn.close()

# Function to predict heart disease (Dummy function, replace with actual model)
def predict_heart_disease(data):
    Inp = []
    for x in data :
        Inp.append(int(x))
    X = scaler.transform([Inp])

    out = lir.predict(X)[0]

    return out

# Create the table
create_table()

# Streamlit UI
st.sidebar.title("Patient Management System")

# Sidebar dropdown for adding/viewing patients and heart disease prediction
menu = st.sidebar.selectbox("Select an option", ["Add Patient", "View/Update Patients", "Heart Disease Prediction"])

if menu == "Add Patient":
    st.header("Add Patient Details")
    with st.form("add_patient_form"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0)
        phone = st.text_input("Phone Number")
        disease = st.text_input("Disease")
        submitted = st.form_submit_button("Add Patient")
        if submitted:
            if name and age and phone and disease:
                add_patient(name, age, phone, disease)
            else:
                st.error("Please fill all the fields")

elif menu == "View/Update Patients":
    st.header("View and Update Patient Status")
    name_filter = st.sidebar.text_input("Filter by Name")
    
    if name_filter:
        patients = fetch_patients_by_name(name_filter)
    else:
        patients = fetch_patients()

    if patients:
        for patient in patients:
            st.write(f"ID: {patient[0]}, Name: {patient[1]}, Age: {patient[2]}, Phone: {patient[3]}, Disease: {patient[4]}, Status: {patient[5]}")
            new_status = st.selectbox("Update Status", ["Pending", "Completed"], key=f"status_{patient[0]}")
            if st.button(f"Update Status for {patient[1]}", key=f"button_{patient[0]}"):
                update_status(patient[0], new_status)
                st.experimental_rerun()
    else:
        st.info("No patients found")

elif menu == "Heart Disease Prediction":
    st.header("Heart Disease Prediction")
    with st.form("heart_disease_form"):
        age = st.number_input("Age", min_value=0)
        sex = st.selectbox("Sex", [0, 1])
        chest_pain_type = st.selectbox("Chest Pain Type", [0, 1, 2, 3])
        resting_bp = st.number_input("Resting Blood Pressure", min_value=0)
        serum_cholesterol = st.number_input("Serum Cholesterol (mg/dl)", min_value=0)
        fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", [0, 1])
        rest_ecg = st.selectbox("Resting Electrocardiographic Results", [0, 1, 2])
        max_hr = st.number_input("Maximum Heart Rate Achieved", min_value=0)
        ex_angina = st.selectbox("Exercise Induced Angina", [0, 1])
        oldpeak = st.number_input("Oldpeak")
        slope = st.selectbox("Slope of the Peak Exercise ST Segment", [0, 1, 2])
        num_major_vessels = st.selectbox("Number of Major Vessels (0-3) Colored by Fluoroscopy", [0, 1, 2, 3])
        thal = st.selectbox("Thal", [0, 1, 2])
        
        submitted = st.form_submit_button("Predict Heart Disease")
        if submitted:
            inputs = [
                age, sex, chest_pain_type, resting_bp, serum_cholesterol, fasting_bs, 
                rest_ecg, max_hr, ex_angina, oldpeak, slope, num_major_vessels, thal
            ]
            prediction = predict_heart_disease(inputs)
            if prediction < 0 :
                prediction = 0
            st.write(f"Heart Disease Prediction: {prediction}")
