"""
api.py
Handles queries for the Codeforces API.
"""

from logging import debug, error
from typing import Any, List

from models import Problem, Submission, User
from requests import get

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


def get_problem_list() -> List[Problem]:
    """
    Returns a list of Problem objects of all problems in the Codeforces dataset.
    Note: Problems having null contestId will be ignored.
    """
    data = query_api(PROBLEMSET_URL)
    problems: List[Problem] = []
    for prob, stat in zip(
        data["result"]["problems"], data["result"]["problemStatistics"]
    ):
        p = Problem.create((prob, stat))
        if p.contestId != 0:
            problems.append(p)
    return problems


def get_users_info(handles: List[str]) -> List[User]:
    """
    Accepts a list of user handles and returns a list of dicts with user info from the Codeforces API.
    Returned User Information is specified at https://codeforces.com/apiHelp/objects#User.
    """
    url = f"{USER_INFO_URL}?handles={';'.join(handles)}"
    return [User.create(x) for x in query_api(url)["result"]]


def get_user_submissions(handle: str, count: int = 10000) -> list[Submission]:
    """
    Returns a list of specified user's submissions.
    """
    data = query_api(f"{USER_STATUS_URL}?handle={handle}&count={count}")
    return [Submission(x) for x in data["result"]]
