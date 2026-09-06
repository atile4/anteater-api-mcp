from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional


# Models
from anteater_api_mcp.client.models import Major

@mcp.tool()
def get_majors() -> list[Major]:
    """Retrieve all majors.

    Returns:
        A list of all majors with their id, name, type, division, and specialization list.

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    try:
        data = client.get_majors()
    except AnteaterAPIError as e:
        return str(e)

    return data

# @TODO implement get_minors

@mcp.tool()
def get_major_course_requirements(id: str) -> list[dict]:
    """Given a major id, Retrieve course requirements for a specific major.

    Args:
        id: The ID of the major to retrieve course requirements for.
    """
    try:
        data = client.get_major_course_requirements(id = id)
    except AnteaterAPIError as e:
        return str(e)

    return data.get("requirements")