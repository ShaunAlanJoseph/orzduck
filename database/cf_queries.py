from typing import Any, Dict, List

from db import DB


async def get_problems_list(min_rating: int, max_rating: int) -> List[Dict[Any, Any]]:
    """
    Get a list of problems with the given ratings.
    """
    query = f"SELECT * FROM cf_problem WHERE rating >= {min_rating} AND rating <= {max_rating}"
    return await DB.execute_query(query)
