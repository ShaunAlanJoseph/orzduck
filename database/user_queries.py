from typing import List, Dict, Any, Optional, TYPE_CHECKING

from database.db import DB

if TYPE_CHECKING:
    from orz_modules.user import User


async def get_users_info(user_ids: Optional[List[int]]) -> List[Dict[str, Any]]:
    if user_ids is None:
        query = "SELECT * FROM user_data"
        result = await DB.execute_query(query)
    else:
        query = f"SELECT * FROM user_data WHERE user_id IN ({','.join(['?' for _ in user_ids])})"
        result = await DB.execute_query(query, *user_ids)
    return result


async def get_user_info(user_id: int) -> Dict[str, Any]:
    """
    :raises IndexError: If user_id is not found in the database
    """
    result = await get_users_info([user_id])
    return result[0]


async def save_user(user: "User"):
    query = (
        "INSERT INTO user_data (user_id, fullname, join_time, cf_handle, college_mail, roll_number) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    )
    await DB.execute_query(
        query,
        user.user_id,
        user.fullname,
        user.join_time,
        user.cf_handle,
        user.college_mail,
        user.roll_number,
    )


async def check_duplicate_cf_handle(cf_handle: str) -> bool:
    query = "SELECT * FROM user_data WHERE cf_handle = ?"
    result = await DB.execute_query(query, cf_handle)
    return bool(result)


async def check_duplicate_college_mail(college_mail: str) -> bool:
    query = "SELECT * FROM user_data WHERE college_mail = ?"
    result = await DB.execute_query(query, college_mail)
    return bool(result)


async def check_duplicate_roll_number(roll_number: str) -> bool:
    query = "SELECT * FROM user_data WHERE roll_number = ?"
    result = await DB.execute_query(query, roll_number)
    return bool(result)
