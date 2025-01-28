from random import sample
from enum import Enum
from typing import Any, Dict, List, Set, Tuple

from codeforces.api import get_user_submissions, get_users_info
from codeforces.models import CFProblem, CFSubmission, CFUser
from database.cf_queries import get_problems_list


class Verdict(Enum):
    FAILED = "FAILED"
    OK = "OK"
    PARTIAL = "PARTIAL"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    IDLENESS_LIMIT_EXCEEDED = "IDLENESS_LIMIT_EXCEEDED"
    SECURITY_VIOLATED = "SECURITY_VIOLATED"
    CRASHED = "CRASHED"
    INPUT_PREPARATION_CRASHED = "INPUT_PREPARATION_CRASHED"
    CHALLENGED = "CHALLENGED"
    SKIPPED = "SKIPPED"
    TESTING = "TESTING"


async def get_handle_verification_problem() -> CFProblem:
    """
    Get a problem for handle verification.
    """
    all_problems = await _fetch_all_problems(max_rating=800)
    problem_set = _filter_problems(problems=all_problems, users=[])
    return sample(problem_set, 1)[0]


def get_user_problem_status(
    handle: str, problem: CFProblem, time: int, after: bool = True
) -> List[Tuple[int, str]]:
    return (get_user_problems_status(handle, [problem], time, after))[problem]


def get_user_problems_status(
    handle: str, problems: List[CFProblem], time: int, after: bool = True
) -> Dict[CFProblem, List[Tuple[int, str]]]:
    """
    Get the status of a user's submissions for a list of problems.
    """
    user_submissions = get_user_submissions(handle)

    # Create a dictionary to store the submissions of each problem in a {CFProblem : [(CFSubmission time, CFSubmission verdict)]} format
    problem_based_submission: Dict[CFProblem, List[Tuple[int, str]]] = {}
    for problem in problems:
        problem_based_submission[problem] = []

    # Filter the submissions based on the time
    for submission in user_submissions:
        if (
            submission.creationTimeSeconds >= time
            if after
            else submission.creationTimeSeconds <= time
        ):
            if submission.problem in list(problem_based_submission.keys()):
                problem_based_submission[submission.problem].append(
                    (submission.creationTimeSeconds, submission.verdict)
                )

    # Sorting the submissions based on the time
    for problem in problem_based_submission:
        problem_based_submission[problem].sort(key=lambda x: x[0])

    # @TODO - @ShaunAlanJoseph
    # Felt it would be better if we did {CFProblem : [CFSubmission]} instead of {CFProblem : [(CFSubmission time, CFSubmission verdict)]}

    return problem_based_submission


async def get_duel_problems(
    handle_1: str, handle_2: str, min_rating: int, max_rating: int, problem_count: int
) -> List[CFProblem]:
    """
    Get a list of problems for a duel between two users with the given ratings.
    """
    user_1, user_2 = get_users_info([handle_1, handle_2])

    all_problems = await _fetch_all_problems(
        min_rating=min_rating, max_rating=max_rating
    )
    problem_set = _filter_problems(problems=all_problems, users=[user_1, user_2])

    return sample(problem_set, problem_count)


async def _fetch_all_problems(
    min_rating: int = 0, max_rating: int = 3500
) -> List[CFProblem]:
    """
    Fetch all problems from the database.
    """
    return _create_problem_list(
        await get_problems_list(min_rating=min_rating, max_rating=max_rating)
    )


def _create_problem_list(problems: List[Dict[str, Any]]) -> List[CFProblem]:
    """
    Create a list of CFProblem objects from a list of dictionaries.
    """
    return [CFProblem(**prob) for prob in problems]


def _filter_problems(problems: List[CFProblem], users: List[CFUser]) -> List[CFProblem]:
    """
    Filter out problems solved by both users.
    """
    global_user_solved: Set[CFProblem] = set()

    for i in users:
        user_submissions: List[CFSubmission] = get_user_submissions(i.handle)
        user_solved = {sub.problem for sub in user_submissions if sub.verdict == Verdict.OK}
        global_user_solved |= user_solved

    return [prob for prob in problems if prob not in global_user_solved]
