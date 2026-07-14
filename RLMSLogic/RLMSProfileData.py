from dataclasses import dataclass


@dataclass
class RLMSProfileData:
    respondentId: str

    age: int
    sex: str
    education: str
    LocalityOfBirth: str
    currentLocality: str
    typeOfLocality: str
    currentStatus: str
    job: str
    jobSector: str
    familyStatus: str
    nationality: str

    hasSavings: bool
    hasCredit: bool

    economicsSourceOfKnowledge: str

    moneyStatusLastThreeYears: str
    salary: str
    lastMonthSalary: str
