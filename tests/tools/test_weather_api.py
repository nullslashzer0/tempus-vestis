import pytest
from unittest.mock import patch, Mock, MagicMock
from tools.weather_api import get_weather_forecast, _get_forecast_url, _get_summary
from tools.constants import NWS_BASE_URL


class TestGetForecastUrl:
    """Test suite for _get_forecast_url helper function."""
    
    @patch('tools.weather_api.requests.get')
    def test_returns_forecast_url(self, mock_get):
        """Test that _get_forecast_url returns the correct forecast URL."""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
            }
        }
        mock_get.return_value = mock_response
        
        result = _get_forecast_url(39.7456, -97.0892)
        
        # Verify the correct URL was called
        expected_url = f"{NWS_BASE_URL}/points/39.7456,-97.0892"
        mock_get.assert_called_once_with(expected_url)
        
        # Verify the correct forecast URL was returned
        assert result == "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
    
    @patch('tools.weather_api.requests.get')
    def test_handles_different_coordinates(self, mock_get):
        """Test _get_forecast_url with different coordinate values."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/LOX/123,456/forecast"
            }
        }
        mock_get.return_value = mock_response
        
        result = _get_forecast_url(34.0522, -118.2437)  # Los Angeles
        
        expected_url = f"{NWS_BASE_URL}/points/34.0522,-118.2437"
        mock_get.assert_called_once_with(expected_url)
        assert result == "https://api.weather.gov/gridpoints/LOX/123,456/forecast"
    
    @patch('tools.weather_api.requests.get')
    def test_handles_negative_coordinates(self, mock_get):
        """Test _get_forecast_url with negative latitude and longitude."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TEST/1,2/forecast"
            }
        }
        mock_get.return_value = mock_response
        
        result = _get_forecast_url(-10.5, -75.3)
        
        expected_url = f"{NWS_BASE_URL}/points/-10.5,-75.3"
        mock_get.assert_called_once_with(expected_url)
        assert isinstance(result, str)
    
    @patch('tools.weather_api.requests.get')
    def test_raises_key_error_on_invalid_response(self, mock_get):
        """Test _get_forecast_url raises error when API response is malformed."""
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "response"}
        mock_get.return_value = mock_response
        
        with pytest.raises(KeyError):
            _get_forecast_url(39.7456, -97.0892)


class TestGetSummary:
    """Test suite for _get_summary helper function."""
    
    def test_returns_forecast_data(self):
        """Test that _get_summary returns the forecast data."""
        forecast = {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "temperature": 75,
                        "temperatureUnit": "F",
                        "shortForecast": "Sunny"
                    }
                ]
            }
        }
        
        result = _get_summary(forecast)
        assert result == forecast
    
    def test_handles_empty_forecast(self):
        """Test _get_summary with empty forecast."""
        forecast = {}
        result = _get_summary(forecast)
        assert result == {}
    
    def test_handles_none_forecast(self):
        """Test _get_summary with None."""
        forecast = None
        result = _get_summary(forecast)
        assert result is None


class TestGetWeatherForecast:
    """Test suite for get_weather_forecast tool function."""
    
    @patch('tools.weather_api.requests.get')
    def test_returns_summarized_forecast_by_default(self, mock_get):
        """Test that get_weather_forecast returns summarized data by default."""
        # Mock the points API call
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
            }
        }
        
        # Mock the forecast API call
        mock_forecast_response = Mock()
        forecast_data = {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "temperature": 75,
                        "temperatureUnit": "F",
                        "shortForecast": "Sunny"
                    }
                ]
            }
        }
        mock_forecast_response.json.return_value = forecast_data
        
        # Configure mock to return different responses for different calls
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        result = get_weather_forecast.invoke({
            "latitude": 39.7456,
            "longitude": -97.0892
        })
        
        # Verify both API calls were made
        assert mock_get.call_count == 2
        
        # Verify the result is the forecast data (summarized)
        assert result == forecast_data
    
    @patch('tools.weather_api.requests.get')
    def test_returns_full_forecast_when_summarize_false(self, mock_get):
        """Test that get_weather_forecast returns full data when summarize=False."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
            }
        }
        
        mock_forecast_response = Mock()
        forecast_data = {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "temperature": 75,
                        "temperatureUnit": "F",
                        "detailedForecast": "Sunny with clear skies"
                    }
                ]
            },
            "metadata": {"extra": "data"}
        }
        mock_forecast_response.json.return_value = forecast_data
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        result = get_weather_forecast.invoke({
            "latitude": 39.7456,
            "longitude": -97.0892,
            "summarize": False
        })
        
        assert mock_get.call_count == 2
        assert result == forecast_data
    
    @patch('tools.weather_api.requests.get')
    def test_handles_different_locations(self, mock_get):
        """Test get_weather_forecast with different locations."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/LOX/123,456/forecast"
            }
        }
        
        mock_forecast_response = Mock()
        forecast_data = {"properties": {"periods": []}}
        mock_forecast_response.json.return_value = forecast_data
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        result = get_weather_forecast.invoke({
            "latitude": 34.0522,
            "longitude": -118.2437
        })
        
        # Verify the points API was called with correct coordinates
        points_call = mock_get.call_args_list[0]
        assert "34.0522,-118.2437" in points_call[0][0]
    
    @patch('tools.weather_api.requests.get')
    def test_handles_multiple_forecast_periods(self, mock_get):
        """Test get_weather_forecast with multiple forecast periods."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
            }
        }
        
        mock_forecast_response = Mock()
        forecast_data = {
            "properties": {
                "periods": [
                    {
                        "name": "Today",
                        "temperature": 75,
                        "temperatureUnit": "F",
                        "shortForecast": "Sunny"
                    },
                    {
                        "name": "Tonight",
                        "temperature": 55,
                        "temperatureUnit": "F",
                        "shortForecast": "Clear"
                    },
                    {
                        "name": "Tomorrow",
                        "temperature": 78,
                        "temperatureUnit": "F",
                        "shortForecast": "Partly Cloudy"
                    }
                ]
            }
        }
        mock_forecast_response.json.return_value = forecast_data
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        result = get_weather_forecast.invoke({
            "latitude": 39.7456,
            "longitude": -97.0892,
            "summarize": True
        })
        
        assert result == forecast_data
        assert len(result["properties"]["periods"]) == 3
    
    @patch('tools.weather_api.requests.get')
    def test_handles_api_error_in_points_call(self, mock_get):
        """Test get_weather_forecast handles errors in the points API call."""
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            get_weather_forecast.invoke({
                "latitude": 39.7456,
                "longitude": -97.0892
            })
    
    @patch('tools.weather_api.requests.get')
    def test_handles_api_error_in_forecast_call(self, mock_get):
        """Test get_weather_forecast handles errors in the forecast API call."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
            }
        }
        
        # First call succeeds, second call fails
        mock_get.side_effect = [mock_points_response, Exception("Forecast API Error")]
        
        with pytest.raises(Exception, match="Forecast API Error"):
            get_weather_forecast.invoke({
                "latitude": 39.7456,
                "longitude": -97.0892
            })
    
    @patch('tools.weather_api.requests.get')
    def test_handles_malformed_json_in_forecast(self, mock_get):
        """Test get_weather_forecast handles malformed JSON in forecast response."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
            }
        }
        
        mock_forecast_response = Mock()
        mock_forecast_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            get_weather_forecast.invoke({
                "latitude": 39.7456,
                "longitude": -97.0892
            })
    
    @patch('tools.weather_api.requests.get')
    def test_forecast_url_construction(self, mock_get):
        """Test that the correct forecast URL is called."""
        mock_points_response = Mock()
        expected_forecast_url = "https://api.weather.gov/gridpoints/TOP/31,80/forecast"
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": expected_forecast_url
            }
        }
        
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {"properties": {"periods": []}}
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        get_weather_forecast.invoke({
            "latitude": 39.7456,
            "longitude": -97.0892
        })
        
        # Verify the forecast URL was called correctly
        forecast_call = mock_get.call_args_list[1]
        assert forecast_call[0][0] == expected_forecast_url
    
    @patch('tools.weather_api.requests.get')
    def test_with_zero_coordinates(self, mock_get):
        """Test get_weather_forecast with zero latitude and longitude."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/TEST/0,0/forecast"
            }
        }
        
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {"properties": {"periods": []}}
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        result = get_weather_forecast.invoke({
            "latitude": 0.0,
            "longitude": 0.0
        })
        
        assert result is not None
        points_call = mock_get.call_args_list[0]
        assert "0.0,0.0" in points_call[0][0]
    
    def test_tool_has_description(self):
        """Test that the tool has a description for LangChain."""
        assert get_weather_forecast.description is not None
        assert len(get_weather_forecast.description) > 0
    
    def test_tool_has_args_schema(self):
        """Test that the tool has an args schema for LangChain."""
        assert get_weather_forecast.args_schema is not None
    
    @pytest.mark.parametrize("lat,lon", [
        (39.7456, -97.0892),  # Kansas
        (34.0522, -118.2437),  # Los Angeles
        (40.7128, -74.0060),   # New York
        (25.7617, -80.1918),   # Miami
        (47.6062, -122.3321),  # Seattle
    ])
    @patch('tools.weather_api.requests.get')
    def test_various_us_locations(self, mock_get, lat, lon):
        """Test get_weather_forecast with various US locations."""
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            "properties": {
                "forecast": f"https://api.weather.gov/gridpoints/TEST/1,2/forecast"
            }
        }
        
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {
            "properties": {
                "periods": [{"name": "Today", "temperature": 70}]
            }
        }
        
        mock_get.side_effect = [mock_points_response, mock_forecast_response]
        
        result = get_weather_forecast.invoke({
            "latitude": lat,
            "longitude": lon
        })
        
        assert result is not None
        assert "properties" in result

