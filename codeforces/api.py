"""
api.py
Handles queries for the Codeforces API.
"""

from requests import get
from typing import Any
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

def get_problem_list() -> Any:
    pass

def get_user_submissions() -> Any:
    pass