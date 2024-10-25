
# Real-Time Data Processing System for Weather Monitoring

## Overview

This project is a real-time weather monitoring system built using Flask, MongoDB, and the OpenWeatherMap API. It fetches weather data for multiple cities, processes it, and provides a dashboard for visualizing the current weather and daily summaries.

## Features

- Fetches real-time weather data from the OpenWeatherMap API every 5 minutes.
- Stores weather data in a MongoDB database.
- Monitors temperature and sends email alerts if thresholds are exceeded.
- Calculates daily weather summaries (average, maximum, and minimum temperatures) every hour.
- Provides a user-friendly web interface to display current weather conditions and historical summaries.

## Prerequisites

- Python 3.x
- Flask
- Requests
- PyMongo
- APScheduler
- MongoDB
- OpenWeatherMap API key

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install the required Python packages:**
   ```bash
   pip install flask requests pymongo apscheduler
   ```

3. **Set up MongoDB:**
   Make sure MongoDB is installed and running on your local machine or configure the connection string to your MongoDB server.

4. **Set your OpenWeatherMap API key:**
   Replace the `API_KEY` variable in `app.py` with your OpenWeatherMap API key.

5. **Configure email settings:**
   Update the `SENDER_EMAIL`, `RECEIVER_EMAIL`, and `SMTP_PASSWORD` variables with your email credentials in `app.py`.

## Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

- The dashboard will display the current weather conditions for the specified cities.
- A summary of the daily weather data will also be shown.
- Alerts will be sent via email if the temperature exceeds the defined threshold for two consecutive updates.

## Code Overview

### app.py

- The main application file that sets up the Flask app, connects to MongoDB, fetches weather data, and handles email alerts.
- Key functions include:
  - `fetch_weather_data()`: Retrieves weather data from the OpenWeatherMap API.
  - `send_alert_email()`: Sends an alert email when temperature thresholds are breached.
  - `calculate_daily_summary()`: Computes daily summaries and stores them in the database.

### home.html

- The front-end HTML template that displays weather data and daily summaries.
- Utilizes Bootstrap for styling and Chart.js for visualizing temperature trends.

