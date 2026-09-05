from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional


# Models
from anteater_api_mcp.client.models import Major

@mcp.tool()
def get_majors() -> list[Major]:
    """Retrieve all majors.

    Returns:
        A list of all majors with their department code and name.

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    try:
        data = client._get("programs/majors", {})
    except AnteaterAPIError as e:
        return str(e)

    return data