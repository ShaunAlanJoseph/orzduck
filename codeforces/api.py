"""
api.py
Handles queries for the Codeforces API.
"""

from logging import debug, error
from typing import Any, List

from models import CFProblem, CFSubmission, CFUser
from requests import get

CODEFORCES_API_BASE = "https://codeforces.com/api/"
PROBLEMSET_URL = f"{CODEFORCES_API_BASE}problemset.problems"
USER_INFO_URL = f"{CODEFORCES_API_BASE}user.info"
USER_STATUS_URL = f"{CODEFORCES_API_BASE}user.status"


class APIQueryException(Exception):
    """Custom exception for failed API queries."""

    pass

class CFProblem:
    """
    Object which stores information about a single Codeforces Problem.
    """
    def __init__(self, data: Tuple[Dict[str, Any], Dict[str, Any]]):
        self.contestId: int = data[0].get("contestId", 0)
        self.problemsetName: Optional[str] = data[0].get("problemsetName", None)
        self.index: str = data[0]["index"]
        self.name: str = data[0]["name"]
        self.type: Optional[str] = data[0].get("type", None)
        self.points: Optional[float] = data[0].get("points", None)
        self.rating: Optional[int] = data[0].get("rating", None)
        self.tags: Optional[List[str]] = data[0].get("tags", None)
        self.solvedCount: Optional[int] = data[1].get("solvedCount", None)
    
    @classmethod
    def only_problem(cls, data: Dict[str, Any]):
        """
        Alternative constructor for when only Problem object is available, and not ProblemStatistics.
        """
        return cls((data, {}))


    def pretty_key(self) -> Tuple[int, str]:
        """
        Returns a tuple (contestId, index) for the given problem.
        """
        return (self.contestId, self.index)

class CFUser:
    """
    Object which stores information about a single Codeforces user.
    """
    def __init__(self, data: Dict[str, Any]):
        self.handle: str = data["handle"]
        self.email: Optional[str] = data.get("email", None)
        self.vkId: Optional[str] = data.get("vkId", None)
        self.openId: Optional[str] = data.get("openId", None)
        self.firstName: Optional[str] = data.get("firstName", None)
        self.lastName: Optional[str] = data.get("lastName", None)
        self.country: Optional[str] = data.get("country", None)
        self.city: Optional[str] = data.get("city", None)
        self.organization: Optional[str] = data.get("organization", None)
        self.contribution: Optional[int] = data.get("contribution", None)
        self.rank: Optional[str] = data.get("rank", None)
        self.rating: Optional[int] = data.get("rating", None)
        self.maxRank: Optional[str] = data.get("maxRank", None)
        self.maxRating: Optional[int] = data.get("maxRating", None)
        self.lastOnlineTimeSeconds: Optional[int] = data.get("lastOnlineTimeSeconds", None)
        self.registrationTimeSeconds: Optional[int] = data.get("registrationTimeSeconds", None)
        self.friendOfCount: Optional[int] = data.get("friendOfCount", None)
        self.avatar: Optional[int] = data.get("avatar", None)
        self.titlePhoto: Optional[int] = data.get("titlePhoto", None)

class CFSubmission:
    """
    Object which stores information about a single Codeforces submission.
    """
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data["id"]
        self.contestId: Optional[int] = data.get("contestId", None)
        self.creationTimeSeconds: Optional[int] = data.get("creationTimeSeconds", None)
        self.relativeTimeSeconds: Optional[int] = data.get("relativeTimeSeconds", None)
        self.problem: CFProblem = CFProblem.only_problem(data["problem"])
        self.author: Optional[Dict[str, Any]] = data.get("author", None)
        self.programmingLanguage: Optional[str] = data.get("programmingLanguage", None)
        self.verdict: Optional[str] = data.get("verdict", None)
        self.testset: Optional[str] = data.get("testset", None)
        self.passedTestCount: Optional[int] = data.get("passedTestCount", None)
        self.timeConsumedMillis: Optional[int] = data.get("timeConsumedMillis", None)
        self.memoryConsumedBytes: Optional[int] = data.get("memoryConsumedBytes", None)
        self.points: Optional[float] = data.get("points", None)

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
    for prob, stat in zip(data["result"]["problems"], data["result"]["problemStatistics"]):
        p = CFProblem((prob, stat))
        if p.contestId != 0:
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
    return [CFCFUser.create(x) for x in query_api(url)["result"]]

def get_user_info(handle: str) -> CFUser:
    """
    Returns information about a single user.
    """
    return get_users_info([handle])[0]


def get_user_submissions(handle: str, count: int = 10000) -> list[CFSubmission]:
    """
    Returns a list of specified user's submissions.
    """
    data = query_api(f"{USER_STATUS_URL}?handle={handle}&count={count}")
    return [CFSubmission(x) for x in data["result"]]