from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

# Models
from anteater_api_mcp.client.models import APExam

from typing import Optional

def remove_catalogue_name(item: dict) -> dict:
    """Removes the 'catalogueName' key from a single exam record."""
    item.pop("catalogueName", None)
    return item


@mcp.tool()
def get_ap_exams(names: Optional[list[str]] = None):
    """Retrieve AP exam credit info.

    Args:
        fullName: List of full AP exam names to look up, e.g.
            ["AP Calculus AB", "AP Microeconomics"]. If omitted or
            empty, every AP exam is returned.

    Returns:
        A list of AP exams, each with full name and reward tiers
        (acceptable scores, units/electives granted, courses granted, etc).

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    names = names or []

    try:
        if not names:
            data = client.get_ap_exam_list()
        else:
            data = []
            for name in names:
                data.extend(client.get_ap_exam(fullName=name))
    except AnteaterAPIError as e:
        return str(e)

    return [remove_catalogue_name(item) for item in data]