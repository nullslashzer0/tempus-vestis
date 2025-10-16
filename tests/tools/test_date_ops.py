import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from tools.date_ops import get_current_date, calculate_future_date


class TestGetCurrentDate:
    """Test suite for get_current_date function."""
    
    def test_returns_string(self):
        """Test that get_current_date returns a string."""
        result = get_current_date.invoke({})
        assert isinstance(result, str)
    
    def test_date_format(self):
        """Test that get_current_date returns date in YYYY-MM-DD format."""
        result = get_current_date.invoke({})
        # Verify format by parsing
        datetime.strptime(result, "%Y-%m-%d")
        assert len(result) == 10
        assert result[4] == "-" and result[7] == "-"
    
    @patch('tools.date_ops.datetime')
    def test_returns_mocked_current_date(self, mock_datetime):
        """Test that get_current_date returns the correct date when mocked."""
        # Mock datetime.now() to return a specific date
        mock_now = datetime(2025, 10, 9, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        result = get_current_date.invoke({})
        assert result == "2025-10-09"
    
    def test_returns_actual_current_date(self):
        """Test that get_current_date returns today's actual date."""
        result = get_current_date.invoke({})
        expected = datetime.now().strftime("%Y-%m-%d")
        assert result == expected
    
    def test_tool_has_description(self):
        """Test that the tool has a description for LangChain."""
        assert get_current_date.description is not None
        assert len(get_current_date.description) > 0


class TestCalculateFutureDate:
    """Test suite for calculate_future_date function."""
    
    def test_returns_string(self):
        """Test that calculate_future_date returns a string."""
        result = calculate_future_date.invoke({"days": 5})
        assert isinstance(result, str)
    
    def test_date_format(self):
        """Test that calculate_future_date returns date in YYYY-MM-DD format."""
        result = calculate_future_date.invoke({"days": 10})
        # Verify format by parsing
        datetime.strptime(result, "%Y-%m-%d")
        assert len(result) == 10
        assert result[4] == "-" and result[7] == "-"
    
    @patch('tools.date_ops.datetime')
    def test_zero_days(self, mock_datetime):
        """Test calculate_future_date with 0 days returns current date."""
        mock_now = datetime(2025, 10, 9, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        result = calculate_future_date.invoke({"days": 0})
        assert result == "2025-10-09"
    
    @patch('tools.date_ops.datetime')
    def test_default_parameter(self, mock_datetime):
        """Test calculate_future_date with no days parameter (defaults to 0)."""
        mock_now = datetime(2025, 10, 9, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        result = calculate_future_date.invoke({})
        assert result == "2025-10-09"
    
    @patch('tools.date_ops.datetime')
    def test_positive_days(self, mock_datetime):
        """Test calculate_future_date with positive days."""
        mock_now = datetime(2025, 10, 9, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        # Test 7 days in the future
        result = calculate_future_date.invoke({"days": 7})
        assert result == "2025-10-16"
    
    @patch('tools.date_ops.datetime')
    def test_negative_days(self, mock_datetime):
        """Test calculate_future_date with negative days (past dates)."""
        mock_now = datetime(2025, 10, 9, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        # Test 5 days in the past
        result = calculate_future_date.invoke({"days": -5})
        assert result == "2025-10-04"
    
    @patch('tools.date_ops.datetime')
    def test_large_positive_days(self, mock_datetime):
        """Test calculate_future_date with large positive days."""
        mock_now = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Test 365 days in the future
        result = calculate_future_date.invoke({"days": 365})
        assert result == "2026-01-01"
    
    @patch('tools.date_ops.datetime')
    def test_large_negative_days(self, mock_datetime):
        """Test calculate_future_date with large negative days."""
        mock_now = datetime(2025, 12, 31, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Test 365 days in the past
        result = calculate_future_date.invoke({"days": -365})
        assert result == "2024-12-31"
    
    @pytest.mark.parametrize("days,expected_offset", [
        (0, 0),
        (1, 1),
        (7, 7),
        (30, 30),
        (-1, -1),
        (-7, -7),
        (-30, -30),
    ])
    def test_various_day_offsets(self, days, expected_offset):
        """Test calculate_future_date with various day offsets."""
        result = calculate_future_date.invoke({"days": days})
        expected = (datetime.now() + timedelta(days=expected_offset)).strftime("%Y-%m-%d")
        assert result == expected
    
    def test_month_boundary(self):
        """Test calculate_future_date crossing month boundaries."""
        with patch('tools.date_ops.datetime') as mock_datetime:
            # Set date to end of month
            mock_now = datetime(2025, 1, 31, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            # Add 1 day should go to next month
            result = calculate_future_date.invoke({"days": 1})
            assert result == "2025-02-01"
    
    def test_year_boundary(self):
        """Test calculate_future_date crossing year boundaries."""
        with patch('tools.date_ops.datetime') as mock_datetime:
            # Set date to end of year
            mock_now = datetime(2025, 12, 31, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            # Add 1 day should go to next year
            result = calculate_future_date.invoke({"days": 1})
            assert result == "2026-01-01"
    
    def test_tool_has_description(self):
        """Test that the tool has a description for LangChain."""
        assert calculate_future_date.description is not None
        assert len(calculate_future_date.description) > 0
    
    def test_tool_has_args_schema(self):
        """Test that the tool has an args schema for LangChain."""
        assert calculate_future_date.args_schema is not None

