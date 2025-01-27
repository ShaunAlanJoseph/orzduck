"""
api.py
Handles queries for the Codeforces API.
"""

from requests import get
from typing import Any, Dict, Optional, List, Tuple
from logging import error, debug

def query_api(url: str) -> Any:
    """
    Sends a GET request to a specified URL and returns the JSON response.
    """
    debug(f"Sending Query: {url}")
    response = get(url)
    if response.status_code != 200:
        error(f"Failed to query: {url}") 
        raise Exception(f"Failed to query: {url}")
    
    debug(f"Response: {response.json()}")
    return response.json()

class Problem:
    """
    Onject which stores information about a single codeforces Problem.
    """
    def __init__(self, data: Tuple[Dict[str, Any], Dict[str, Any]]):
        self.contestId: int = data[0].get("contestId", 0)
        self.problemsetName: Optional[str] = data[0].get("problemsetName", None)
        self.index: str = data[0]["index"]
        self.name: str = data[0]["name"]
        self.type = data[0]["type"]
        self.rating: Optional[int] = data[0].get("rating", None)
        self.tags: List[str] = data[0]["tags"]
        self.solvedCount: int = data[1]["solvedCount"]
    def print_pretty(self):
        print(self.contestId, self.index, self.name)

def get_problem_list() -> Any:
    """
    Returns a list of Problem objects of all problems in the Codeforces dataset.
    Note: Problems having null contestId will be ignored. 
    """
    url = "https://codeforces.com/api/problemset.problems"
    data = query_api(url)

    l: List[Problem] = []
    for prob, stat in zip(data["result"]["problems"], data["result"]["problemStatistics"]):
        p = Problem((prob, stat))
        if p.contestId != 0:
            l.append(p)
    return l

def get_user_data(user: str) -> Any:
    pass

def get_user_submissions(user: str) -> Any:
    pass