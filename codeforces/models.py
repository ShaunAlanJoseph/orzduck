from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class CFProblem:
    """
    Object which stores information about a single Codeforces Problem.
    """

    contestId: int = -1
    problemsetName: str = ""
    index: str = ""
    name: str = ""
    type: str = ""
    points: float = -1.0
    rating: int = -1
    tags: List[str] = field(default_factory=list)
    solvedCount: int = -1

    def __hash__(self) -> int:
        return hash(self.pretty_key())

    @classmethod
    def create(cls, data: Tuple[Dict[str, Any], Dict[str, Any]]):
        return cls(
            contestId=data[0].get("contestId", -1),
            problemsetName=data[0].get("problemsetName", ""),
            index=data[0].get("index", ""),
            name=data[0].get("name", ""),
            type=data[0].get("type", ""),
            points=data[0].get("points", -1.0),
            rating=data[0].get("rating", -1),
            tags=data[0].get("tags", []),
            solvedCount=data[1].get("solvedCount", -1),
        )

    @classmethod
    def only_problem(cls, data: Dict[str, Any]):
        return cls.create((data, {}))

    @property
    def link(self) -> str:
        return (
            f"https://codeforces.com/problemset/problem/{self.contestId}/{self.index}"
        )

    def pretty_key(self) -> Tuple[int, str]:
        return (self.contestId, self.index)


@dataclass
class CFUser:
    """
    Object which stores information about a single Codeforces user.
    """

    handle: str
    email: str = ""
    vkId: str = ""
    openId: str = ""
    firstName: str = ""
    lastName: str = ""
    country: str = ""
    city: str = ""
    organization: str = ""
    contribution: int = -1
    rank: str = ""
    rating: int = -1
    maxRank: str = ""
    maxRating: int = -1
    lastOnlineTimeSeconds: int = -1
    registrationTimeSeconds: int = -1
    friendOfCount: int = -1
    avatar: str = ""
    titlePhoto: str = ""

    @classmethod
    def create(cls, data: Dict[str, Any]):
        return cls(**{k: data.get(k, v) for k, v in cls.__annotations__.items()})


@dataclass
class CFSubmission:
    """
    Object which stores information about a single Codeforces submission.
    """

    id: int = -1
    contestId: int = -1
    creationTimeSeconds: int = -1
    relativeTimeSeconds: int = -1
    problem: CFProblem = field(default_factory=CFProblem)
    author: Dict[str, Any] = field(default_factory=dict)
    programmingLanguage: str = ""
    verdict: str = ""
    testset: str = ""
    passedTestCount: int = -1
    timeConsumedMillis: int = -1
    memoryConsumedBytes: int = -1
    points: float = -1.0

    def __hash__(self) -> int:
        return hash((self.id, self.contestId, self.creationTimeSeconds))

    @classmethod
    def create(cls, data: Dict[str, Any]):
        return cls(
            id=data.get("id", -1),
            contestId=data.get("contestId", -1),
            creationTimeSeconds=data.get("creationTimeSeconds", -1),
            relativeTimeSeconds=data.get("relativeTimeSeconds", -1),
            problem=CFProblem.only_problem(data.get("problem", {})),
            author=data.get("author", {}),
            programmingLanguage=data.get("programmingLanguage", ""),
            verdict=data.get("verdict", ""),
            testset=data.get("testset", ""),
            passedTestCount=data.get("passedTestCount", -1),
            timeConsumedMillis=data.get("timeConsumedMillis", -1),
            memoryConsumedBytes=data.get("memoryConsumedBytes", -1),
            points=data.get("points", -1.0),
        )
