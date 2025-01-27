"""
api.py
Handles queries for the Codeforces API.
"""

from requests import get
from typing import Any, Dict, Optional, List, Tuple
from logging import error, debug

CODEFORCES_API_BASE = "https://codeforces.com/api/"
PROBLEMSET_URL = f"{CODEFORCES_API_BASE}problemset.problems"
USER_INFO_URL = f"{CODEFORCES_API_BASE}user.info"
USER_STATUS_URL = f"{CODEFORCES_API_BASE}user.status"

class APIQueryException(Exception):
    """Custom exception for failed API queries."""
    pass

class Problem:
    """
    Object which stores information about a single Codeforces Problem.
    """
    def __init__(self, data: Tuple[Dict[str, Any], Dict[str, Any]]):
        self.contestId: int = data[0].get("contestId", 0)
        self.problemsetName: Optional[str] = data[0].get("problemsetName", None)
        self.index: str = data[0]["index"]
        self.name: str = data[0]["name"]
        self.type: Optional[str] = data[0].get("type", None)
        self.rating: Optional[int] = data[0].get("rating", None)
        self.tags: Optional[List[str]] = data[0].get("tags", None)
        self.solvedCount: Optional[int] = data[1].get("solvedCount", None)
    
    def pretty_key(self) -> Tuple[int, str]:
        """
        Returns a tuple (contestId, index) for the given problem.
        """
        return (self.contestId, self.index)

class User:
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

class Submission:
    ...

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
    for prob, stat in zip(data["result"]["problems"], data["result"]["problemStatistics"]):
        p = Problem((prob, stat))
        if p.contestId != 0:
            problems.append(p)
    return problems

def get_users_info(handles: List[str]) -> List[User]:
    """
    Accepts a list of user handles and returns a list of dicts with user info from the Codeforces API.
    Returned User Information is specified at https://codeforces.com/apiHelp/objects#User. 
    """
    url = f"{USER_INFO_URL}?handles={';'.join(handles)}"
    return [User(x) for x in query_api(url)["result"]]

def get_user_submissions(handle: str, count: int = 10000, ac_only: bool = False) -> list[Submission]:
    """
    Returns a list of specified user's submissions.
    """
    ...
