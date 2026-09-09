from anteater_api_mcp.app import mcp
from anteater_api_mcp.client.client import client, AnteaterAPIError

from rapidfuzz import process, fuzz

# Models
from typing import Optional
from anteater_api_mcp.client.models import APExam

@mcp.tool()
def search_ap_exams(query: list[str], limit: int = 5, score_cutoff: float = 60.0):
    """Fuzzy search for AP exam names when you don't know the exact official name.

    Args:
        query: List of search strings to match, e.g. ["AP Calc AB", "Comp Sci Principles"].
        limit: Max number of candidate matches to return per query. Defaults to 5.
        score_cutoff: Minimum similarity score (0-100) for a match to be included.
            Defaults to 60. Lower this if you're getting no results; raise it if
            you're getting too many loose matches.

    Returns:
        A dict with "data" mapping each input query to a list of candidate
        matches, each with "fullName" and a "score" (0-100, higher = closer
        match). Does NOT return exam reward details. Once you know the exact
        fullName you want, call get_ap_exams([exact_name]) to get rewards.

    Scoring note:
        Uses rapidfuzz's token_set_ratio, not token_sort_ratio. token_sort_ratio
        penalizes short queries against long official names purely for length
        (e.g. "AP Physics" scored *lower* against "AP Physics C: Mechanics"
        than against the unrelated "AP Statistics", since it compares whole
        strings symmetrically). token_set_ratio fixes that by scoring based on
        shared tokens, so a query whose words are a subset of the target's
        words (e.g. "AP Physics" vs "AP Physics 1: Algebra-Based") scores 100
        regardless of extra qualifying words in the target.

        Tradeoff: token_set_ratio also raises the score floor for *unrelated*
        exams that only share the literal word "AP" with the query, since that
        alone counts as a token match. This hasn't produced false positives at
        the default score_cutoff=60, but if score_cutoff is ever lowered, this
        floor has less margin before unrelated matches start leaking in than
        token_sort_ratio did. Re-verify against the full exam list if that
        cutoff changes.
    """
    try:
        all_exams = client.get_ap_exam_list()
    except AnteaterAPIError as e:
        return {"data": {}, "warnings": [f"Failed to fetch AP exam list: {e}"]}

    exam_names = [exam["fullName"] for exam in all_exams]

    results = {}
    for q in query:
        matches = process.extract(
            q,
            exam_names,
            scorer=fuzz.token_set_ratio,
            limit=limit,
            score_cutoff=score_cutoff,
        )
        results[q] = [
            {"fullName": name, "score": round(score, 1)}
            for name, score, _ in matches
        ]

    return {"data": results}

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