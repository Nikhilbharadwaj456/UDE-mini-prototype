import requests
import sqlite3
import pandas as pd
import numpy as np
from fastapi import FastAPI
from sklearn.linear_model import LinearRegression
import uvicorn

app = FastAPI()

# Database setup
conn = sqlite3.connect("weather_data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    wind_speed REAL,
    pressure REAL
)
""")
conn.commit()

# Fetch weather data from OpenWeather API
def fetch_weather_data():
    API_KEY = "33fcc7e6ccddf9060dee5553d447f405"  # ✅ Replace with your actual OpenWeather API key
    CITY = "Bengaluru"
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an error if request fails
        data = response.json()
        
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"]
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None  # Return None if there's an error

# Store fetched data in DB
def store_weather_data(data):
    cursor.execute("INSERT INTO weather (temperature, humidity, wind_speed, pressure) VALUES (?, ?, ?, ?)",
                   (data["temperature"], data["humidity"], data["wind_speed"], data["pressure"]))
    conn.commit()

# Check how many records are stored
def check_data():
    cursor.execute("SELECT COUNT(*) FROM weather")
    count = cursor.fetchone()[0]
    print(f"Database contains {count} records.")
    return count

# Train a basic AI model (Linear Regression for weather predictions)
def train_ai_model():
    df = pd.read_sql_query("SELECT * FROM weather", conn)
    record_count = len(df)

    if record_count < 10:  # Require at least 10 records
        print(f"Not enough data: Only {record_count} records found.")
        return None

    X = df[["humidity", "wind_speed", "pressure"]]
    y = df["temperature"]
    model = LinearRegression().fit(X, y)
    return model

# API Endpoint to collect weather data
@app.get("/collect")
def collect_weather():
    data = fetch_weather_data()
    if data is None:
        return {"error": "Failed to fetch weather data. Check your API key and internet connection."}

    store_weather_data(data)
    count = check_data()  # Check how many records are stored
    return {"message": f"Weather data stored successfully! {count} records in database.", "data": data}

# API Endpoint to predict temperature
@app.get("/predict")
def predict_weather(humidity: float, wind_speed: float, pressure: float):
    model = train_ai_model()
    if model is None:
        return {"error": "Not enough data for predictions. Collect more data first."}
    
    prediction = model.predict(np.array([[humidity, wind_speed, pressure]]))[0]
    return {"predicted_temperature": prediction}

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
