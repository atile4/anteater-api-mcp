from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

# Models
from anteater_api_mcp.client.models import APExam

def remove_catalogue_name(item: dict) -> dict:
    """Removes the 'catalogueName' key from a single exam record."""
    item.pop("catalogueName", None)
    return item


@mcp.tool()
def get_ap_exam_list() -> list[dict]:
    """Retrieve all AP exams.

    Returns:
        A list of all AP exams with their full name and list of rewards that
        includes acceptable scores, units granted, elective units granted,
        GE granted, and courses granted.

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    try:
        data = client.get_ap_exam_list()
    except AnteaterAPIError as e:
        return str(e)

    return [remove_catalogue_name(item) for item in data]


@mcp.tool()
def get_ap_exam(fullName: str) -> dict:
    """Retrieve AP exam credit info by exam name.

    Args:
        fullName: Full name of the AP exam, e.g. ``AP Calculus AB``,
            ``AP Microeconomics``.

    Returns:
        Matching AP exams with their full name and list of reward tiers
        (acceptable scores, units/electives granted, courses granted, etc).

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    try:
        data = client.get_ap_exam(fullName=fullName)
    except AnteaterAPIError as e:
        return str(e)

    return [remove_catalogue_name(item) for item in data]



