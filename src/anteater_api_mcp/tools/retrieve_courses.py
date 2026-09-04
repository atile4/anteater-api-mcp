from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional

# Models
from anteater_api_mcp.client.models import Course

sample_department = "I%26C%20SCI"

KEEP_COLUMNS = ["department", "courseNumber", "school", "courseLevel", "title", "description"]
# @TODO: number of courses to retrieve. 
@mcp.tool()
def get_courses(
    department: Optional[str] = None,
    school: Optional[str] = None,
    course_level: Optional[int] = None,
    ge_category: Optional[str] = None,
    take: Optional[int] = 10
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
    take = take or 10
    try:
        data = client.get_courses(
            department=department,
            school=school,
            course_level=course_level,
            ge_category=ge_category,
            take=take,
        )
    except AnteaterAPIError as e:
        return str(e)

    return [
        {k: v for k, v in row.items() if k in KEEP_COLUMNS}
        for row in data
    ]

#@TODO retrieve prerequisites for a course

#@TODO retrieve corequisites for a course

#@TODO retrieve courses that have this course as a prereq
