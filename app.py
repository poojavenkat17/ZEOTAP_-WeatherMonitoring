from flask import Flask, render_template, jsonify, request
import requests
from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from bson import ObjectId

app = Flask(__name__)

# MongoDB Setup
client = MongoClient('mongodb://localhost:27017')
db = client.weather_db
weather_collection = db.weather_data

# OpenWeatherMap API key and URL
API_KEY = '62450284d94dc27a8171fdfacc17e543'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Cities to monitor
cities = ["Chennai", "Delhi", "Mumbai", "Bangalore", "Kolkata", "Hyderabad"]

# User Preferences (Default: Celsius)
temp_unit = 'Celsius'
alert_thresholds = {
    "temperature": 35  # Celsius
}
consecutive_breach_count = {city: 0 for city in cities}

# Email Configuration
SENDER_EMAIL = "venkatpooja2003@gmail.com"
RECEIVER_EMAIL = "aishwarya.rajvedi@zeotap.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_PASSWORD = "your_email_password"  # Use environment variable or secret manager

# Convert Kelvin to Celsius/Fahrenheit with unique representation
def convert_temperature(temp_k, unit='Celsius'):
    if unit == 'Celsius':
        return f"{round(temp_k - 273.15, 2)}°C"
    elif unit == 'Fahrenheit':
        return f"{round((temp_k - 273.15) * 9/5 + 32, 2)}°F"

# Function to send alert email
def send_alert_email(city, temperature):
    subject = f"Temperature Alert for {city}"
    body = f"The temperature in {city} has exceeded {alert_thresholds['temperature']}°C for two consecutive updates. Current temperature: {temperature}°C."
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
    print(f"Alert email sent for {city}!")

# Function to check thresholds and trigger alerts
def check_alerts(city, temp):
    if temp > alert_thresholds["temperature"]:
        consecutive_breach_count[city] += 1
        if consecutive_breach_count[city] >= 2:
            send_alert_email(city, temp)
            consecutive_breach_count[city] = 0  # Reset after sending email
    else:
        consecutive_breach_count[city] = 0  # Reset if temperature falls below threshold

# Convert Kelvin to Celsius/Fahrenheit with unique representation
def convert_temperature(temp_k, unit='Celsius'):
    if unit == 'Celsius':
        return f"{round(temp_k - 273.15, 2)}°C"
    elif unit == 'Fahrenheit':
        return f"{round((temp_k - 273.15) * 9/5 + 32, 2)}°F"

# Function to check thresholds and trigger alerts
def check_alerts(city, temp, condition):
    if temp > alert_thresholds["temperature"]:
        print(f"ALERT: Temperature in {city} has exceeded {alert_thresholds['temperature']}°C!")

# Fetch Weather Data from API
def fetch_weather_data():
    for city in cities:
        params = {'q': city, 'appid': API_KEY}
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            temp = convert_temperature(data['main']['temp'], 'Celsius')  # Keep this as Celsius
            feels_like = convert_temperature(data['main']['feels_like'], 'Celsius')  # Keep this as Celsius
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            condition = data['weather'][0]['description']
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Store data in MongoDB
            weather_collection.insert_one({
                "city": city,
                "temperature": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "condition": condition,
                "timestamp": timestamp
            })

            # Check for alerts
            check_alerts(city, float(temp.split('°')[0]), condition)

# Schedule API calls (every 5 minutes)
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_weather_data, 'interval', minutes=5)
scheduler.start()



def calculate_daily_summary():
    for city in cities:
        # Get the latest weather entry for today
        latest_entry = weather_collection.find_one(
            {"city": city},
            sort=[("timestamp", DESCENDING)]
        )
        
        if latest_entry:
            temperatures = []
            conditions = []
            # We can add the latest entry to our calculations
            if isinstance(latest_entry['temperature'], str):
                temp_value = float(latest_entry['temperature'].replace('°C', ''))
            else:
                temp_value = float(latest_entry['temperature'])
                
            temperatures.append(temp_value)
            conditions.append(latest_entry['condition'])

            avg_temp = round(sum(temperatures) / len(temperatures), 2)
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            dominant_condition = max(set(conditions), key=conditions.count)

            db.daily_summaries.insert_one({
                "city": city,
                "date": datetime.now().strftime('%Y-%m-%d'),  # Current date
                "average_temperature": avg_temp,
                "maximum_temperature": max_temp,
                "minimum_temperature": min_temp,
                "dominant_condition": dominant_condition
            })
        else:
            print(f"No data found for {city} for the current day.")  # Debug statement


# scheduler.add_job(calculate_daily_summary, 'interval', minutes=15)
scheduler.add_job(calculate_daily_summary, 'cron', hour='*') 
# scheduler.add_job(calculate_daily_summary, 'interval', hours=2)

def clear_daily_summary():
    db.daily_summaries.delete_many({})  # This will remove all entries in the daily_summaries collection
    print("Daily summary data cleared.")
    
scheduler.add_job(clear_daily_summary, 'interval', hours=2)

with app.app_context():
    calculate_daily_summary()

@app.route('/city/<city_name>', methods=['GET'])
def city_weather(city_name):
    city_data = db.weather.find_one({'city': city_name})
    
    if city_data:
        return jsonify({
            'city': city_name,
            'weather_data': {
                'condition': city_data['condition'],
                'temperature': city_data['temperature'],
                'feels_like': city_data['feels_like'],
                'humidity': city_data['humidity'],
                'wind_speed': city_data['wind_speed'],
                'timestamp': city_data['timestamp'],
            },
            'daily_summaries': [
                {
                    'date': summary['date'],
                    'average_temperature': summary['average_temperature'],
                    'maximum_temperature': summary['maximum_temperature'],
                    'minimum_temperature': summary['minimum_temperature'],
                    'dominant_condition': summary['dominant_condition']
                } for summary in city_data['daily_summaries']
            ],
            'id': str(city_data['_id'])  # Convert ObjectId to string here
        })
    else:
        return jsonify({'error': 'City not found'}), 404
    
@app.route('/')
def home():
    latest_weather = {}
    daily_summary = {}
    max_temps = []
    min_temps = []
    labels = []

    for city in cities:
        latest_weather[city] = weather_collection.find_one({"city": city}, sort=[("timestamp", -1)])
        daily_summary[city] = list(db.daily_summaries.find({"city": city}).sort("date", DESCENDING).limit(3))

        if latest_weather[city]:
            max_temp = float(latest_weather[city]['temperature'].replace('°C', ''))  # Max temp
            min_temp = max_temp - 10  # Adjust this based on your actual min temp logic
            
            max_temps.append(max_temp)
            min_temps.append(min_temp)
            labels.append(city)

    return render_template('home.html', weather_data=latest_weather, daily_summary=daily_summary,
                           labels=labels, max_temps=max_temps, min_temps=min_temps)

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        scheduler.shutdown()




if __name__ == '__main__':
    fetch_weather_data()  # Initial call to fetch data on app startup
    app.run(debug=True)
