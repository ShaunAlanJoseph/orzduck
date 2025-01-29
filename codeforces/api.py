"""
api.py
Handles queries for the Codeforces API.
"""

from logging import debug, error
from typing import Any, List

from requests import get

from codeforces.models import CFProblem, CFSubmission, CFUser

CODEFORCES_API_BASE = "https://codeforces.com/api/"
PROBLEMSET_URL = f"{CODEFORCES_API_BASE}problemset.problems"
USER_INFO_URL = f"{CODEFORCES_API_BASE}user.info"
USER_STATUS_URL = f"{CODEFORCES_API_BASE}user.status"


class APIQueryException(Exception):
    """Custom exception for failed API queries."""

    pass


def query_api(url: str) -> Any:
    """
    Sends a GET request to a specified URL and returns the JSON response.
    """
    debug(f"Sending Query: {url}")
    response = get(url)
    if response.status_code != 200:
        error(f"Failed to query: {url}")
        raise APIQueryException(f"Failed to query: {url}")

    debug(f"Response: {response.json()}")
    return response.json()


def get_problem_list() -> List[CFProblem]:
    """
    Returns a list of CFProblem objects of all problems in the Codeforces dataset.
    Note: CFProblems having null contestId will be ignored.
    """
    data = query_api(PROBLEMSET_URL)
    problems: List[CFProblem] = []
    for prob, stat in zip(
        data["result"]["problems"], data["result"]["problemStatistics"]
    ):
        p = CFProblem.create((prob, stat))  # type: ignore
        if p.contestId != -1:
            problems.append(p)
    return problems


def get_users_info(handles: List[str]) -> List[CFUser]:
    """
    Accepts a list of user handles and returns a list of dicts with user info from the Codeforces API.
    Returned CFUser Information is specified at https://codeforces.com/apiHelp/objects#CFUser.
    """
    if len(handles) == 0:
        return []
    url = f"{USER_INFO_URL}?handles={';'.join(handles)}"
    return [CFUser.create(x) for x in query_api(url)["result"]]


def get_user_info(handle: str) -> CFUser:
    """
    Returns information about a single user.
    """
    return get_users_info([handle])[0]


# def get_user_submissions(handle: str, count: int = 10000) -> list[CFSubmission]:
def get_user_submissions(handle: str, count: int = 10000) -> list[CFSubmission]:
    """
    Returns a list of specified user's submissions.
    """
    data = query_api(f"{USER_STATUS_URL}?handle={handle}&count={count}")
    return [CFSubmission.create(x) for x in data["result"]]
