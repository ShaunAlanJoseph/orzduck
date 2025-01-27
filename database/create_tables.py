from database.db import DB


async def create_tables():
    await DB.establish_connection()

    print("Creating user_data table.")
    query = (
        "CREATE TABLE IF NOT EXISTS user_data ("
        "user_id BIGINT PRIMARY KEY,"
        "fullname TEXT NOT NULL,"
        "join_time BIGINT NOT NULL,"
        "cf_handle TEXT,"
        "college_mail TEXT,"
        "roll_number TEXT"
        ")"
    )
    await DB.execute_query(query)

    print("Creating duels_tictac table.")
    query = (
        "CREATE TABLE IF NOT EXISTS duels_tictac ("
        "duel_id BIGINT PRIMARY KEY,"
        "player1 BIGINT NOT NULL,"
        "player2 BIGINT NOT NULL,"
        "start_time BIGINT NOT NULL,"
        "end_time BIGINT,"
        "status TEXT NOT NULL,"
        "winner BIGINT,"
        "problems TEXT[] NOT NULL,"
        "progress TEXT[] NOT NULL,"
        "tournament_id BIGINT"
        ")"
    )
    await DB.execute_query(query)

    print("Creating duels_mini table.")
    query = (
        "CREATE TABLE IF NOT EXISTS duels_mini ("
        "duel_id BIGINT PRIMARY KEY,"
        "player1 BIGINT NOT NULL,"
        "player2 BIGINT NOT NULL,"
        "start_time BIGINT NOT NULL,"
        "end_time BIGINT,"
        "status TEXT NOT NULL,"
        "winner BIGINT,"
        "problems TEXT[] NOT NULL,"
        "progress TEXT[] NOT NULL,"
        "tournament_id BIGINT"
        ")"
    )
    await DB.execute_query(query)

    print("Creating duels_classic table.")
    query = (
        "CREATE TABLE IF NOT EXISTS duels_classic ("
        "duel_id BIGINT PRIMARY KEY,"
        "player1 BIGINT NOT NULL,"
        "player2 BIGINT NOT NULL,"
        "start_time BIGINT NOT NULL,"
        "end_time BIGINT,"
        "status TEXT NOT NULL,"
        "winner BIGINT,"
        "problem TEXT NOT NULL,"
        "progress TEXT NOT NULL,"
        "tournament_id BIGINT"
        ")"
    )
    await DB.execute_query(query)

    print("Creating cf_user table.")
    query = (
        "CREATE TABLE IF NOT EXISTS cf_user ("
        "handle TEXT PRIMARY KEY,"
        "email TEXT,"
        "vkId TEXT,"
        "openId TEXT,"
        "firstName TEXT,"
        "lastName TEXT,"
        "country TEXT,"
        "city TEXT,"
        "organization TEXT,"
        "contribution INT NOT NULL,"
        "rank TEXT NOT NULL,"
        "rating INT NOT NULL,"
        "maxRank TEXT NOT NULL,"
        "maxRating INT NOT NULL,"
        "lastOnlineTimeSeconds BIGINT NOT NULL,"
        "registrationTimeSeconds BIGINT NOT NULL,"
        "friendOfCount INT NOT NULL,"
        "avatar TEXT NOT NULL,"
        "titlePhoto TEXT NOT NULL"
        ")"
    )
    await DB.execute_query(query)

    print("Creating cf_problem table.")
    query = (
        "CREATE TABLE IF NOT EXISTS cf_problem ("
        "contestId INT NOT NULL,"
        "problemsetName TEXT,"
        "index TEXT NOT NULL,"
        "name TEXT NOT NULL,"
        "PRIMARY KEY (contestId, index, name), "
        "type TEXT NOT NULL,"
        "points FLOAT,"
        "rating INT,"
        "tags TEXT[] NOT NULL,"
        "solvedCount INT NOT NULL"
        ")"
    )
    await DB.execute_query(query)

    await DB.close_connection()
