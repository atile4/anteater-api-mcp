from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional


# Models
from anteater_api_mcp.client.models import Course

@mcp.tool()
def get_majors():
    """Retrieve all majors.

    Returns:
        A list of all majors with their department code and name.

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    try:
        data = client._get("majors", {})
    except AnteaterAPIError as e:
        return str(e)

    return data