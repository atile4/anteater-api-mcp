from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional

# Models
from anteater_api_mcp.client.models import Course

# Constants
from anteater_api_mcp.constants.courses import BASE_COURSE_COLUMNS, OPTIONAL_COURSE_COLUMNS

#@TODO: implement aliases so that an agent can translate a course into an id
@mcp.tool()
def get_course_by_id(id: str,
                       include_instructors: bool = False,
                       include_prerequisites: bool = False,
                       include_geList: bool = False,
                       include_terms: bool = False) -> Course:
    """Retrieve a course by its ID.
    Args:
        id: course id
        include_instructors(bool): Whether to include instructors in the response.
        include_prerequisites(bool): Whether to include prerequisites in the response.
        include_geList(bool): Whether to include general education list in the response.
        include_terms(bool): Whether to include terms in the response.
    Returns:
        A course's details such as department, number, school, level, title, description, 
        and optionally instructors, prerequisites, general education list, and terms.
    
    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    selected_options = {
        "include_instructors": include_instructors,
        "include_prerequisites": include_prerequisites,
        "include_geList": include_geList,
        "include_terms": include_terms,
    }
    keep_columns = BASE_COURSE_COLUMNS.copy()
    for option, column in OPTIONAL_COURSE_COLUMNS.items():
        if selected_options.get(option, False):
            keep_columns.append(column)

    try:
        data = client.get_course_by_id(id=id)
    except AnteaterAPIError as e:
        raise AnteaterAPIError(f"Failed to fetch course by ID {id}: {e}") from e

    return {k: v for k, v in data.items() if k in keep_columns}

@mcp.tool()
def get_courses_by_ids(id: list[str],
                       include_instructors: bool = False,
                       include_prerequisites: bool = False,
                       include_geList: bool = False,
                       include_terms: bool = False) -> list[Course]:
    """Retrieve multiple courses from a list of IDs.
    Args:
        id: list of course ids to fetch
        include_instructors(bool): Whether to include instructors in the response.
        include_prerequisites(bool): Whether to include prerequisites in the response.
        include_geList(bool): Whether to include general education list in the response.
        include_terms(bool): Whether to include terms in the response.
    Returns:
        A list of courses with details such as department, number, school, level, title,
        description, and optionally instructors, prerequisites, general education list,
        and terms.
    
    Raises:
        AnteaterAPIError: If the Anteater API request fails.
    """
    selected_options = {
        "include_instructors": include_instructors,
        "include_prerequisites": include_prerequisites,
        "include_geList": include_geList,
        "include_terms": include_terms,
    }
    keep_columns = BASE_COURSE_COLUMNS.copy()
    for option, column in OPTIONAL_COURSE_COLUMNS.items():
        if selected_options.get(option, False):
            keep_columns.append(column)

    courses = []
    for course_id in id:
        try:
            data = client.get_course_by_id(id=course_id)
        except AnteaterAPIError as e:
            raise AnteaterAPIError(
                f"Failed to fetch course by ID {course_id}: {e}"
            ) from e

        courses.append({k: v for k, v in data.items() if k in keep_columns})

    return courses

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
