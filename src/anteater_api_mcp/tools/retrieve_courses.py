import requests
from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional


# Models
from anteater_api_mcp.client.models import Course

sample_department = "I%26C%20SCI"
sample_take = 10
BASE_URL = "https://anteaterapi.com/v2/rest/"


# What courses are offered; filtered by department, school, course level, has dependencies

KEEP_COLUMNS = ["department", "courseNumber", "school", "courseLevel", "title", "description"]
@mcp.tool()
def get_courses(
    department: Optional[str] = None,
    school: Optional[str] = None,
    course_level: Optional[int] = None,
    ge_category: Optional[str] = None,
) -> list[Course]:
    """Retrieve courses matching the supplied filters.

    Args:
        department: Department code to filter by, such as ``I&C SCI``, ``AFAM``.
        school: School name to filter by.
        course_level: Course level to filter by, such as ``100`` or ``200``.
        ge_category: General Education category to filter by.

    Returns:
        Up to 10 matching courses with their department, number, school,
        level, title, and description.

    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    department = department or None
    school = school or None
    course_level = course_level or None
    ge_category = ge_category or None
    try:
        data = client.get_courses(
            department=department,
            school=school,
            course_level=course_level,
            ge_category=ge_category,
            take=sample_take,
        )
    except AnteaterAPIError as e:
        return str(e)

    return [
        {k: v for k, v in row.items() if k in KEEP_COLUMNS}
        for row in data
    ]