import streamlit as st
import requests

st.title("Weather Prediction Dashboard")

# Collect new weather data
if st.button("Collect Weather Data"):
    response = requests.get("http://127.0.0.1:8000/collect")
    if response.status_code == 200:
        st.success(f"Data Collected: {response.json()}")
    else:
        st.error("Error fetching data!")

# Prediction Input
st.header("Predict Temperature")
humidity = st.number_input("Enter Humidity", min_value=0.0, max_value=100.0, step=0.1)
wind_speed = st.number_input("Enter Wind Speed", min_value=0.0, max_value=50.0, step=0.1)
pressure = st.number_input("Enter Pressure", min_value=800.0, max_value=1100.0, step=0.1)

# Predict Button
if st.button("Predict Temperature"):
    response = requests.get(f"http://127.0.0.1:8000/predict?humidity={humidity}&wind_speed={wind_speed}&pressure={pressure}")
    if response.status_code == 200:
        st.success(f"Predicted Temperature: {response.json()['predicted_temperature']:.2f}°C")
    else:
        st.error("Prediction failed!")
