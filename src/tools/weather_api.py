import requests
from langchain_core.tools import tool

from tools.constants import NWS_BASE_URL

def _get_forecast_url(latitude: float, longitude: float) -> str:
    """
    Get the forecast URL for a given latitude and longitude.
    """
    url = f"{NWS_BASE_URL}/points/{latitude},{longitude}"
    data = requests.get(url).json()
    return data["properties"]["forecast"]

def _get_summary(forecast: dict) -> dict:
    """
    Extract only the relevant data from the forecast
    """
    return forecast

@tool
def get_weather_forecast(latitude: float, longitude: float, summarize: bool = True) -> str:
    """
    Get the weather forecast for a given city and date.
    """
    forecast_url = _get_forecast_url(latitude, longitude)
    response = requests.get(forecast_url)

    if summarize:
        return _get_summary(response.json())
    
    return response.json()

