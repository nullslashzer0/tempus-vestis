from datetime import datetime, timedelta
from langchain_core.tools import tool

@tool
def get_current_date() -> str:
    """
    Get the current date.
    """
    return datetime.now().strftime("%Y-%m-%d")


@tool
def calculate_future_date(days: int = 0) -> str:
    """
    Generate a future date based on a number of days.

    Args:
        days: The number of days to add to the current date.
        
    Returns:
        A future date based on the number of days.
    """
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

