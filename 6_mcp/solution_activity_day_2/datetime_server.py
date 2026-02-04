"""
MCP Server for Date and Time Tools
Provides utilities for getting current date, time, and timezone information.
"""

from datetime import datetime
import pytz
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("datetime-server")


@mcp.tool()
def get_current_date() -> str:
    """
    Get the current date in YYYY-MM-DD format.
    
    Returns:
        Current date as a string (e.g., '2026-02-04')
    """
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
def get_current_time() -> str:
    """
    Get the current time in HH:MM:SS format.
    
    Returns:
        Current time as a string (e.g., '14:30:45')
    """
    return datetime.now().strftime("%H:%M:%S")


@mcp.tool()
def get_current_datetime() -> str:
    """
    Get the current date and time in a human-readable format.
    
    Returns:
        Current datetime as a string (e.g., 'Tuesday, February 04, 2026 at 14:30:45')
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %H:%M:%S")


@mcp.tool()
def get_timestamp() -> str:
    """
    Get the current Unix timestamp.
    
    Returns:
        Unix timestamp as a string (seconds since epoch)
    """
    return str(int(datetime.now().timestamp()))


@mcp.tool()
def get_datetime_in_timezone(timezone: str) -> str:
    """
    Get the current date and time in a specific timezone.
    
    Args:
        timezone: Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')
    
    Returns:
        Current datetime in the specified timezone
    
    Examples:
        get_datetime_in_timezone('America/New_York') -> '2026-02-04 09:30:45 EST'
        get_datetime_in_timezone('Europe/London') -> '2026-02-04 14:30:45 GMT'
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error: Invalid timezone '{timezone}'. Use format like 'America/New_York'"


@mcp.tool()
def get_day_of_week() -> str:
    """
    Get the current day of the week.
    
    Returns:
        Day name (e.g., 'Monday', 'Tuesday', etc.)
    """
    return datetime.now().strftime("%A")


@mcp.tool()
def get_iso_datetime() -> str:
    """
    Get the current datetime in ISO 8601 format.
    
    Returns:
        ISO formatted datetime (e.g., '2026-02-04T14:30:45.123456')
    """
    return datetime.now().isoformat()


# Resource to get timezone list (optional advanced feature)
@mcp.resource("timezones://list")
def get_timezone_list() -> str:
    """
    Get a list of all available timezone names.
    
    Returns:
        JSON list of timezone names
    """
    import json
    common_timezones = [
        "America/New_York",
        "America/Los_Angeles",
        "America/Chicago",
        "Europe/London",
        "Europe/Paris",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Australia/Sydney",
        "UTC"
    ]
    return json.dumps(common_timezones, indent=2)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
