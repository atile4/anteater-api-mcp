from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

# utils
from anteater_api_mcp.utils import normalize_course_code


def _describe_leaf(leaf: dict) -> str:
    """Human-readable label for a leaf node, used in blocked_by messages."""
    if leaf.get("prereqType") == "course":
        return normalize_course_code(leaf.get("courseId", "?"))
    if leaf.get("prereqType") == "exam":
        return leaf.get("examName", "?")
    return "unknown requirement"


def _evaluate_leaf(leaf: dict, satisfied: set[str], ap_scores: dict[str, int]) -> dict:
    """Evaluate a single {"prereqType": "course"|"exam", ...} leaf.

    KNOWN LIMITATION: course leaves carry a "minGrade" (e.g. "C", "D-"), but
    `satisfied` only knows *whether* a course was completed, not what grade
    was earned -- completed_courses is just a list of IDs. So a course leaf
    is treated as met purely on completion, ignoring minGrade. If you later
    want to check this properly, completed_courses would need to become
    {course_id: grade} instead of a flat list, and this function would
    compare grades using UCI's letter-grade ordering.
    """
    if leaf.get("prereqType") == "course":
        code = normalize_course_code(leaf.get("courseId", ""))
        met = code in satisfied
        return {"met": met, "missing": [] if met else [code], "blocked_by": []}

    if leaf.get("prereqType") == "exam":
        exam_name = leaf.get("examName")
        min_score = leaf.get("minGrade")
        if exam_name not in ap_scores:
            # No score provided for this exam -- can't confirm or deny.
            return {"met": None, "missing": [], "blocked_by": []}
        try:
            have, need = int(ap_scores[exam_name]), int(min_score)
        except (TypeError, ValueError):
            return {"met": None, "missing": [], "blocked_by": []}
        met = have >= need
        label = f"{exam_name} score >= {need}"
        return {"met": met, "missing": [] if met else [label], "blocked_by": []}

    # Unrecognized leaf shape -- don't guess.
    return {"met": None, "missing": [], "blocked_by": []}


def _evaluate_prereq_node(node, satisfied: set[str], ap_scores: dict[str, int]) -> dict:
    """Recursively evaluate a prerequisiteTree node (AND / OR / NOT / leaf).

    Returns {"met": bool | None, "missing": list[str], "blocked_by": list[str]}
      - met=True:  branch satisfied.
      - met=False: branch not satisfied. "missing" lists courses/exam scores
        that would close the gap; "blocked_by" lists already-completed
        courses that are disqualifying (from a NOT branch).
      - met=None:  couldn't be determined (e.g. an exam leaf with no score
        provided). Same "don't guess" philosophy as evaluate_node's
        handling of unknown requirement types in degree_progress.py.
    """
    if not node:
        return {"met": True, "missing": [], "blocked_by": []}

    if isinstance(node, dict) and "prereqType" in node:
        return _evaluate_leaf(node, satisfied, ap_scores)

    if isinstance(node, dict) and "AND" in node:
        results = [_evaluate_prereq_node(c, satisfied, ap_scores) for c in node["AND"]]
        false_results = [r for r in results if r["met"] is False]
        if false_results:
            # AND fails the moment one child fails, regardless of any
            # unresolved (None) siblings -- their status can't save it.
            return {
                "met": False,
                "missing": [m for r in false_results for m in r["missing"]],
                "blocked_by": [b for r in false_results for b in r["blocked_by"]],
            }
        if any(r["met"] is None for r in results):
            return {"met": None, "missing": [], "blocked_by": []}
        return {"met": True, "missing": [], "blocked_by": []}

    if isinstance(node, dict) and "OR" in node:
        results = [_evaluate_prereq_node(c, satisfied, ap_scores) for c in node["OR"]]
        if any(r["met"] for r in results):
            return {"met": True, "missing": [], "blocked_by": []}
        if any(r["met"] is None for r in results):
            # No branch is confirmed True, but an unresolved branch could
            # still turn out True -- we can't call this False yet.
            return {"met": None, "missing": [], "blocked_by": []}
        # Every branch is definitively False: report the cheapest path.
        best = min(results, key=lambda r: len(r["missing"]) + len(r["blocked_by"]))
        return {"met": False, "missing": best["missing"], "blocked_by": best["blocked_by"]}

    if isinstance(node, dict) and "NOT" in node:
        items = node["NOT"]
        results = [_evaluate_prereq_node(c, satisfied, ap_scores) for c in items]
        violated = [_describe_leaf(item) for item, r in zip(items, results) if r["met"]]
        if violated:
            return {"met": False, "missing": [], "blocked_by": violated}
        if any(r["met"] is None for r in results):
            return {"met": None, "missing": [], "blocked_by": []}
        return {"met": True, "missing": [], "blocked_by": []}

    return {"met": None, "missing": [], "blocked_by": []}


def check_course_eligibility(
    course_ids: list[str],
    completed_course_ids: list[str],
    ap_scores: dict[str, int] | None = None,
) -> dict:
    """Split a list of course IDs into those whose prerequisites are already
    met by a student's completed/planned courses vs. those that aren't
    eligible yet. Plain function, not an MCP tool -- see
    check_course_eligibility_tool for the tool wrapper. Kept separate so
    other tools (e.g. simulate_undergrad_degree_progress in
    degree_progress.py) can reuse this without going through a tool call.

    Args:
        course_ids: Course IDs to check eligibility for. Accepts spaced
            ("COMPSCI 161") or unspaced ("COMPSCI161") formatting.
        completed_course_ids: Courses already taken or planned to be taken
            before enrollment, same ID format. "Planned" is treated the
            same as "completed" -- this answers "will prereqs be met", not
            "are they met as of today". Course-level minGrade requirements
            in the prerequisite tree are ignored (completion is treated as
            sufficient) since this list carries no grade information.
        ap_scores: Optional AP credit, e.g. {"AP CALCULUS BC": 4}. Keys must
            match the "examName" field exactly as it appears in a
            prerequisiteTree exam leaf (this is the catalogue-style short
            name, e.g. "AP COMP SCI A" -- NOT the fullName used elsewhere
            in this API, like "AP Computer Science A"). If an exam
            requirement's name isn't in this dict, that leaf is left
            unresolved rather than assumed unmet.

    Returns:
        A dict with:
          - "eligible": courses whose prerequisiteTree is fully satisfied.
          - "not_eligible": courses with unmet prereqs and/or a violated
            overlap restriction. Each entry may include "missing" (courses
            or exam scores that would close the gap) and/or "blocked_by"
            (already-completed courses that disqualify this course under a
            NOT restriction).
          - "needs_review": courses whose prerequisite structure couldn't
            be auto-evaluated (e.g. an exam leaf with no ap_scores entry).
            Check "prerequisiteText" manually for these.
          - "warnings": course_ids the API had no record of.
    """
    satisfied = {normalize_course_code(c) for c in completed_course_ids}
    ap_scores = ap_scores or {}

    try:
        data = client.get_courses_batch(ids=course_ids)
    except AnteaterAPIError as e:
        return {"error": f"Failed to fetch courses: {e}"}

    requested_ids = {normalize_course_code(c) for c in course_ids}
    returned_ids = {normalize_course_code(row["id"]) for row in data if row.get("id")}
    missing_from_api = requested_ids - returned_ids

    eligible = []
    not_eligible = []
    needs_review = []

    for course in data:
        tree = course.get("prerequisiteTree") or {}
        result = _evaluate_prereq_node(tree, satisfied, ap_scores)

        entry = {"id": course.get("id"), "title": course.get("title")}

        if result["met"] is None:
            entry["prerequisiteText"] = course.get("prerequisiteText")
            needs_review.append(entry)
        elif result["met"]:
            eligible.append(entry)
        else:
            if result["missing"]:
                entry["missing"] = result["missing"]
            if result["blocked_by"]:
                entry["blocked_by"] = result["blocked_by"]
            entry["prerequisiteText"] = course.get("prerequisiteText")
            not_eligible.append(entry)

    output = {
        "eligible": eligible,
        "not_eligible": not_eligible,
        "needs_review": needs_review,
    }
    if missing_from_api:
        output["warnings"] = [
            f"No course found for ID(s): {', '.join(sorted(missing_from_api))}"
        ]

    return output


@mcp.tool()
def check_course_eligibility_tool(
    course_ids: list[str],
    completed_course_ids: list[str],
    ap_scores: dict[str, int] | None = None,
) -> dict:
    """MCP-exposed wrapper around check_course_eligibility -- see that
    function's docstring for full parameter and return details. Use this
    for any course-list-vs-prerequisites check: electives, a major's
    required courses, a wishlist, a whole department -- not elective-only.
    """
    return check_course_eligibility(course_ids, completed_course_ids, ap_scores)