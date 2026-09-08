from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError


def normalize_course_code(code: str) -> str:
    """API course codes look like 'I&CSCI31' with no spaces. User input might
    come in as 'I&C SCI 31' or lowercase, so we normalize both sides the same way."""
    return code.upper().replace(" ", "")


def extract_courses_from_boolean_tree(node) -> set[str]:
    """Flattens an AND/OR coursesGranted tree into a flat set of course codes.
    NOTE: this intentionally does not distinguish AND vs OR — see caveat above."""
    if isinstance(node, str):
        return {normalize_course_code(node)}
    if isinstance(node, dict):
        courses = set()
        for key in ("AND", "OR"):
            for child in node.get(key, []):
                courses |= extract_courses_from_boolean_tree(child)
        return courses
    return set()


def _resolve_ap_credit(ap_scores: list[str]) -> tuple[set[str], list[str]]:
    """Parses entries formatted as 'Exam Full Name:Score', e.g.
    'AP Computer Science A:5'. Entries that don't match this format are
    skipped with a warning rather than guessed, since assuming a score
    could silently over-credit a degree audit."""
    credited = set()
    warnings = []

    for entry in ap_scores:
        if ":" not in entry:
            warnings.append(
                f"Skipped '{entry}': expected format 'Exam Full Name:Score'."
            )
            continue

        name, _, score_str = entry.rpartition(":")
        name = name.strip()
        try:
            score = int(score_str.strip())
        except ValueError:
            warnings.append(f"Skipped '{entry}': score is not a number.")
            continue

        try:
            exam_records = client.get_ap_exam(fullName=name)
        except AnteaterAPIError as e:
            warnings.append(f"Could not fetch AP exam '{name}': {e}")
            continue

        for exam in exam_records:
            for reward in exam.get("rewards", []):
                if score in reward.get("acceptableScores", []):
                    credited |= extract_courses_from_boolean_tree(
                        reward.get("coursesGranted", {})
                    )

    return credited, warnings


def evaluate_node(node: dict, satisfied: set[str]) -> dict:
    """Recursively checks a single requirement node against a set of
    normalized, satisfied course codes."""
    label = node.get("label")
    rtype = node.get("requirementType")

    if rtype == "Course":
        courses = node.get("courses", [])
        needed = node.get("courseCount", len(courses))
        have = [c for c in courses if normalize_course_code(c) in satisfied]
        satisfied_flag = len(have) >= needed
        return {
            "label": label,
            "type": rtype,
            "satisfied": satisfied_flag,
            "needed": needed,
            "courses": courses,
            "completed_courses": have,
        }

    if rtype == "Group":
        children = node.get("requirements", [])
        needed = node.get("requirementCount", len(children))
        child_results = [evaluate_node(c, satisfied) for c in children]
        satisfied_children = [c for c in child_results if c["satisfied"]]
        satisfied_flag = len(satisfied_children) >= needed
        return {
            "label": label,
            "type": rtype,
            "satisfied": satisfied_flag,
            "needed": needed,
            "satisfied_count": len(satisfied_children),
            "completed_courses": [c for r in child_results for c in r["completed_courses"]],
            "children": child_results,
        }

    # Unknown requirement type (e.g. unit-based, GE-based) — don't guess, flag it.
    return {
        "label": label,
        "type": rtype,
        "satisfied": None,
        "completed_courses": [],
        "note": "Requirement type not auto-verifiable; review manually.",
    }


def evaluate_requirements(nodes: list[dict], satisfied: set[str]) -> dict:
    results = [evaluate_node(n, satisfied) for n in nodes]
    return {
        "satisfied": all(r["satisfied"] for r in results if r["satisfied"] is not None),
        "completed_courses": [c for r in results for c in r["completed_courses"]],
        "details": results,
    }


@mcp.tool()
def simulate_undergrad_degree_progress(
    majorId: str,
    specializationId: str | None = None,
    minorId: str | None = None,
    catalogYear: str | None = None,
    ap_scores: list[str] | None = None,
    completed_courses: list[str] | None = None,
) -> dict:
    """Simulate progress toward an undergraduate degree.

    Args:
        majorId: The major ID to check requirements for.
        specializationId: The specialization/program ID to check requirements for.
        minorId: Optional minor ID to check requirements for.
        catalogYear: Catalog year to use; defaults to the API's most recent.
        ap_scores: AP credit, formatted as ["Exam Full Name:Score", ...],
            e.g. ["AP Computer Science A:5", "AP Calculus BC:4"].
        completed_courses: Courses already taken, e.g. ["I&C SCI 31", "MATH 2A"].

    Returns:
        A dict with "major", "specialization", and (if given) "minor" keys,
        each containing satisfied courses and a per-requirement
        breakdown. A top-level "warnings" key lists anything that couldn't
        be resolved (unparseable AP entries, failed fetches, etc).
    """
    warnings: list[str] = []
    satisfied = {normalize_course_code(c) for c in (completed_courses or [])}

    ap_credit, ap_warnings = _resolve_ap_credit(ap_scores or [])
    satisfied |= ap_credit
    warnings.extend(ap_warnings)

    progress: dict = {}

    try:
        major_data = client.get_major_course_requirements(id=majorId, catalogYear=catalogYear)
        progress["major"] = evaluate_requirements(major_data.get("requirements", []), satisfied)
    except AnteaterAPIError as e:
        return {"error": f"Failed to fetch major requirements: {e}"}

    try:
        spec_data = client.get_spec_course_requirements(programId=specializationId, catalogYear=catalogYear)
        progress["specialization"] = evaluate_requirements(spec_data.get("requirements", []), satisfied)
    except AnteaterAPIError as e:
        warnings.append(f"Failed to fetch specialization requirements: {e}")

    if minorId:
        try:
            minor_data = client.get_minor_course_requirements(id=minorId, catalogYear=catalogYear)
            progress["minor"] = evaluate_requirements(minor_data.get("requirements", []), satisfied)
        except AnteaterAPIError as e:
            warnings.append(f"Failed to fetch minor requirements: {e}")

    if warnings:
        progress["warnings"] = warnings

    return progress