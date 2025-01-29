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
    
    def __eq__(self, other: Any):
        if not isinstance(other, CFProblem):
            return False
        return self.pretty_key() == other.pretty_key()

    def __post_init__(self):
        self.link = (
            f"https://codeforces.com/problemset/problem/{self.contestId}/{self.index}"
        )

    @classmethod
    def create(cls, data: Tuple[Dict[str, Any], Dict[str, Any]]):
        contestid = data[0].get("contestId", -1)
        if contestid == -1:
            contestid = data[0].get("contestid", -1)
        problemsetName = data[0].get("problemsetName", "")
        if problemsetName == "":
            problemsetName = data[0].get("problemsetname", "")
        solvedCount = data[1].get("solvedCount", -1)
        if solvedCount == -1:
            solvedCount = data[0].get("solvedcount", -1)

        return cls(
            contestId=contestid,
            problemsetName=problemsetName,
            index=data[0].get("index", ""),
            name=data[0].get("name", ""),
            type=data[0].get("type", ""),
            points=data[0].get("points", -1.0),
            rating=data[0].get("rating", -1),
            tags=data[0].get("tags", []),
            solvedCount=solvedCount,
        )

    @classmethod
    def only_problem(cls, data: Dict[str, Any]):
        return cls.create((data, {}))

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
        vkId = data.get("vkId", "")
        if vkId == "":
            vkId = data.get("vkid", "")
        openId = data.get("openId", "")
        if openId == "":
            openId = data.get("openid", "")
        firstName = data.get("firstName", "")
        if firstName == "":
            firstName = data.get("firstname", "")
        lastName = data.get("lastName", "")
        if lastName == "":
            lastName = data.get("lastname", "")
        maxRank = data.get("maxRank", "")
        if maxRank == "":
            maxRank = data.get("maxrank", "")
        maxRating = data.get("maxRating", -1)
        if maxRating == -1:
            maxRating = data.get("maxrating", -1)
        lastOnlineTimeSeconds = data.get("lastOnlineTimeSeconds", -1)
        if lastOnlineTimeSeconds == -1:
            lastOnlineTimeSeconds = data.get("lastonlinetimeseconds", -1)
        registrationTimeSeconds = data.get("registrationTimeSeconds", -1)
        if registrationTimeSeconds == -1:
            registrationTimeSeconds = data.get("registrationtimeseconds", -1)
        friendOfCount = data.get("friendOfCount", -1)
        if friendOfCount == -1:
            friendOfCount = data.get("friendofcount", -1)
        titlePhoto = data.get("titlePhoto", "")
        if titlePhoto == "":
            titlePhoto = data.get("titlephoto", "")

        return cls(
            handle=data.get("handle", ""),
            email=data.get("email", ""),
            vkId=vkId,
            openId=openId,
            firstName=firstName,
            lastName=lastName,
            country=data.get("country", ""),
            city=data.get("city", ""),
            organization=data.get("organization", ""),
            contribution=data.get("contribution", -1),
            rank=data.get("rank", ""),
            rating=data.get("rating", -1),
            maxRank=maxRank,
            maxRating=maxRating,
            lastOnlineTimeSeconds=lastOnlineTimeSeconds,
            registrationTimeSeconds=registrationTimeSeconds,
            friendOfCount=friendOfCount,
            avatar=data.get("avatar", ""),
            titlePhoto=titlePhoto,
        )

        # return cls(**{k: data.get(k, v) for k, v in cls.__annotations__.items()})


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
