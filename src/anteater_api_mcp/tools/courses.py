from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional

# Models
from anteater_api_mcp.client.models import Course

# Constants
from anteater_api_mcp.constants.courses import BASE_COURSE_COLUMNS, OPTIONAL_COURSE_COLUMNS

#@TODO: implement aliases so that an agent can translate a course into an id
#@TODO: include field for typical offerings (derived from terms if chosen to be included, only include past 5 years)
# @TODO: number of courses to retrieve with defaults. 
@mcp.tool()
def get_courses(
    ids: Optional[list[str]] = None,
    department: Optional[str] = None,
    school: Optional[str] = None,
    course_level: Optional[int] = None,
    ge_category: Optional[str] = None,
    take: Optional[int] = 10,
    include_instructors: bool = False,
    include_prerequisites: bool = False,
    include_geList: bool = False,
    include_terms: bool = False,
) -> list[Course]:
    """Retrieve courses, either by specific IDs or by filter.

    If `ids` is provided, fetches exactly those courses (one lookup per ID).
    If `ids` is omitted or empty, retrieves courses matching the supplied
    filters instead, up to `take` results.

    Args:
        ids: Specific course IDs to fetch, e.g. ``["I&CSCI31", "MATH2A"]``.
            When provided, department/school/course_level/ge_category/take
            are ignored.
        department: Department code to filter by, such as ``I&C SCI``, ``AFAM``.
            Only used when `ids` is not provided.
        school: School name to filter by. Only used when `ids` is not provided.
        course_level: Course level to filter by, such as ``100`` or ``200``.
            Only used when `ids` is not provided.
        ge_category: General Education category to filter by. Only used
            when `ids` is not provided.
        take: Max number of results to return when filtering. Only used
            when `ids` is not provided. Defaults to 10.
        include_instructors: Whether to include instructors in the response.
        include_prerequisites: Whether to include course prerequisites in
            the response.
        include_geList: Whether to include general education list in the
            response.
        include_terms: Whether to include historic terms (such as 2024 Fall,
            2026 Winter) in the response.

    Returns:
        A list of courses with department, number, school, level, title,
        description, and optionally instructors, prerequisites, general
        education list, and terms.

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
    if include_prerequisites:
        keep_columns.append("prerequisiteText")

    if ids:
        courses = []
        for course_id in ids:
            try:
                data = client.get_course_by_id(id=course_id)
            except AnteaterAPIError as e:
                raise AnteaterAPIError(
                    f"Failed to fetch course by ID {course_id}: {e}"
                ) from e
            courses.append({k: v for k, v in data.items() if k in keep_columns})
        return courses

    try:
        data = client.get_courses(
            department=department or None,
            school=school or None,
            course_level=course_level or None,
            ge_category=ge_category or None,
            take=take or 10,
        )
    except AnteaterAPIError as e:
        raise AnteaterAPIError(f"Failed to fetch courses: {e}") from e

    return [{k: v for k, v in row.items() if k in keep_columns} for row in data]