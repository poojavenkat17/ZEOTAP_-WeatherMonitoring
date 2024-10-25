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
