from typing import List, TYPE_CHECKING

from database.db import DB

if TYPE_CHECKING:
    from codeforces.api import CFProblem, CFUser


async def dump_problem(problem: "CFProblem"):
    query = (
        "INSERT INTO cf_problem (contestId, problemsetName, index, name, type, points, rating, tags, solvedCount) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    await DB.execute_query(
        query,
        problem.contestId,
        problem.problemsetName,
        problem.index,
        problem.name,
        problem.type,
        problem.points,
        problem.rating,
        problem.tags,
        problem.solvedCount,
    )


async def dump_problems(problems: List["CFProblem"]):
    for i, problem in enumerate(problems):
        if (i + 1) % 1000 == 0 or i == len(problems) - 1:
            print(f"Dumping problem {i + 1}/{len(problems)}")
        await dump_problem(problem)


async def clear_problems():
    query = "TRUNCATE TABLE cf_problem"
    await DB.execute_query(query)


async def dump_user(user: "CFUser"):
    query = (
        "INSERT INTO cf_user (handle, email, vkId, openId, firstName, lastName, country, city, organization, contribution, rank, rating, maxRank, maxRating, lastOnlineTimeSeconds, registrationTimeSeconds, friendOfCount, avatar, titlePhoto) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    await DB.execute_query(
        query,
        user.handle,
        user.email,
        user.vkId,
        user.openId,
        user.firstName,
        user.lastName,
        user.country,
        user.city,
        user.organization,
        user.contribution,
        user.rank,
        user.rating,
        user.maxRank,
        user.maxRating,
        user.lastOnlineTimeSeconds,
        user.registrationTimeSeconds,
        user.friendOfCount,
        user.avatar,
        user.titlePhoto,
    )


async def dump_users(users: List["CFUser"]):
    for i, user in enumerate(users):
        if (i + 1) % 10 == 0 or i == len(users) - 1:
            print(f"Dumping user {i + 1}/{len(users)}")
        await dump_user(user)


async def clear_users():
    query = "TRUNCATE TABLE cf_user"
    await DB.execute_query(query)
from typing import Any, Dict, List

from db import DB


async def get_problems_list(min_rating: int, max_rating: int) -> List[Dict[Any, Any]]:
    """
    Get a list of problems with the given ratings.
    """
    query = f"SELECT * FROM cf_problem WHERE rating >= {min_rating} AND rating <= {max_rating}"
    return await DB.execute_query(query)
