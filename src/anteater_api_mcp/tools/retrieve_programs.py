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

@mcp.tool()
def get_spec_course_requirements(
    programId: str,
    catalogYear: Optional[str] = None
) -> list[dict]:
    """
    Given a specialization id (programId) and an optional catalog year, 
    retrieve course requirements for the specialization of that catalog year.
    Args:
        programId: The ID of the specialization to retrieve course requirements for.
        catalogYear: The catalog year to retrieve course requirements for. If not provided, the latest catalog year will be used.
    Returns:
        A list of course requirements for the specialization of the specified catalog year.
    """
    try:
        data = client.get_spec_course_requirements(programId=programId, catalogYear=catalogYear)
    except AnteaterAPIError as e:
        return str(e)

    return data.get("requirements")


@mcp.tool()
def get_undergrad_requirements(id: str, 
                               catalogYear: Optional[str] = None, 
                               include_ids: bool = False
    ) -> dict:
    """Retrieve requirements external to major/minor/specializations,
      that are required for all undergraduate degrees.

    Args:
        id: The type of requirement
            - "UC" for University of California requirements
            - "GE" for general education requirements
            - "CHC2": for Campuswide Honors Collegium 2 year requirements
            - "CHC4": for Campuswide Honors Collegium 4 year requirements
        include_ids: If True, keep internal requirementId fields in the
            output. Defaults to False since these IDs are opaque and not
            useful for explaining requirements or building a course plan.

    Returns:
        A list of all requirements with their type, catalog year, and
        course requirements list. Internal IDs and null/unused fields are
        stripped by default to keep the payload lean for planning tasks.

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    def _clean(node):
        if isinstance(node, dict):
            cleaned = {}
            for k, v in node.items():
                if k == "requirementId" and not include_ids:
                    continue
                if v is None:
                    continue
                cleaned[k] = _clean(v)
            return cleaned
        elif isinstance(node, list):
            return [_clean(item) for item in node]
        return node

    try:
        data = client.get_undergrad_requirements(id = id, catalogYear = catalogYear)
    except AnteaterAPIError as e:
        return str(e)

    return _clean(data)




