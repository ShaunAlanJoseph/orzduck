from tortoise import BaseDBAsyncClient, Tortoise
from logging import info, error
from typing import Optional, List, Dict, Any

from config import TORTOISE_ORM


class DB:
    conn: Optional[BaseDBAsyncClient] = None

    @staticmethod
    async def establish_connection():
        await Tortoise.init(config=TORTOISE_ORM)
        DB.conn = Tortoise.get_connection("default")
        await DB.conn.execute_query_dict("SELECT 1")  # type: ignore
        info("Database connection established")
    
    @staticmethod
    async def close_connection():
        await Tortoise.close_connections()
        info("Database connection closed")
    
    @staticmethod
    def get_connection():
        if DB.conn is None:
            DB.conn = Tortoise.get_connection("default")
        return DB.conn
    
    @staticmethod
    def format_query(query: str):
        formatted_query = ""
        i = 0
        ctr = 1
        while i < len(query):
            if query[i] != "?":
                formatted_query += query[i]
            elif i < len(query) - 1 and query[i + 1] == "?":
                formatted_query += "?"
            else:
                formatted_query += f"${ctr}"
                ctr += 1
            i += 1
        return formatted_query
    
    @staticmethod
    async def execute_query(query: str, *args: Any):
        try:
            query = DB.format_query(query)
            conn = DB.get_connection()
            result: List[Dict[str, Any]] = await conn.execute_query_dict(query, args)  # type: ignore
            return result
        except Exception as exc:
            error(f"Error executing query: {exc}, query: {query}, args: {args}")
            raise exc
