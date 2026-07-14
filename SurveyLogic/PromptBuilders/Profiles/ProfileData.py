from dataclasses import dataclass

@dataclass
class ProfileData:
    respondentId: str

    age: int
    sex: str
    education: str
    LocalityOfBirth: str
    currentLocality: str
    typeOfLocality: str
    job: str
    jobSector: str
    currentStatus: str
    salary: str
    hasSavings: bool
    hasCredit: bool
    familyStatus: str
    nationality: str

    economicsSourceOfKnowledge: str

    nonDurableGoods: list[str]
    newsSources: list[str]
