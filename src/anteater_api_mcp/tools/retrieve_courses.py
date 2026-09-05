from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional

# Models
from anteater_api_mcp.client.models import Course


BASE_COURSE_COLUMNS = [
    "department",
    "courseNumber",
    "school",
    "courseLevel",
    "title",
    "description",
]
OPTIONAL_COURSE_COLUMNS = {
    "instructors": "instructors",
    "prerequisites": "prerequisites",
}

@mcp.tool()
def fetch_course_by_id(id: str,
                       instructors: bool = False,
                       prerequisites: bool = False) -> Course:
    """Retrieve a course by its ID.
    Args:
        id: course id
        instructors(bool): Whether to include instructors in the response.
        prerequisites(bool): Whether to include prerequisites in the response.
    Returns:
        A course's information
    
    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    selected_options = {
        "instructors": instructors,
        "prerequisites": prerequisites,
    }
    keep_columns = BASE_COURSE_COLUMNS.copy()
    for option, column in OPTIONAL_COURSE_COLUMNS.items():
        if selected_options[option]:
            keep_columns.append(column)

    try:
        data = client.fetch_course_by_id(id=id)
    except AnteaterAPIError as e:
        print(str(e))
        return str(e)

    return {k: v for k, v in data.items() if k in keep_columns}

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
        {k: v for k, v in row.items() if k in BASE_COURSE_COLUMNS}
        for row in data
    ]

#@TODO retrieve courses that have this course as a prereq
