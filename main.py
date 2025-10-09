import os
from dotenv import load_dotenv

from core.constants import APP_NAME
from tools.weather_api import get_weather_forecast

load_dotenv()

if __name__ == "__main__":
    print(f"Welcome to {APP_NAME} - an AI powered wardrobe planner")

    print(get_weather_forecast(41.4553,-81.9179))