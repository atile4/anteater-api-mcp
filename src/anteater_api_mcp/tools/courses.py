from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from typing import Optional

# Models
from anteater_api_mcp.client.models import CourseSearchResult

# Constants
from anteater_api_mcp.constants.courses import BASE_COURSE_COLUMNS, OPTIONAL_COURSE_COLUMNS

# utils
from anteater_api_mcp.utils import normalize_course_code

#@TODO: implement aliases so that an agent can translate a course into an id
#@TODO: include field for typical offerings (derived from terms if chosen to be included, only include past 5 years)
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
) -> CourseSearchResult:
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
        A CourseSearchResult with `data` (the found courses, using the
        requested filter columns) and `warnings` (non-empty only if some
        requested `ids` weren't found — the batch endpoint returns 200 ok
        with those silently dropped rather than erroring).

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
        try:
            data = client.get_courses_batch(ids=ids)
        except AnteaterAPIError as e:
            raise AnteaterAPIError(f"Failed to fetch courses by IDs {ids}: {e}") from e

        requested = {normalize_course_code(i) for i in ids}
        returned = {normalize_course_code(row["id"]) for row in data if row.get("id")}
        missing = requested - returned

        courses = [{k: v for k, v in row.items() if k in keep_columns} for row in data]
        warnings = [f"No course found for ID(s): {', '.join(sorted(missing))}"] if missing else []

        return CourseSearchResult(data=courses, warnings=warnings)

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

    courses = [{k: v for k, v in row.items() if k in keep_columns} for row in data]
    return CourseSearchResult(data=courses, warnings=[])