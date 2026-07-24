from RLMSLogic.RLMSProfileData import RLMSProfileData
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class SimpleRLMSProfileConverter:
    def convert(self, profile: RLMSProfileData) -> ProfileData:
        salary = profile.salary
        if salary == "99999997.0":
            salary = "Не указано"

        return ProfileData(
            respondentId=profile.respondentId,
            age=profile.age,
            sex=profile.sex,
            education=profile.education,
            LocalityOfBirth=profile.LocalityOfBirth,
            currentLocality=profile.currentLocality,
            typeOfLocality=profile.typeOfLocality,
            job=profile.job,
            jobSector=profile.jobSector,
            currentStatus=profile.currentStatus,
            nationality=profile.nationality,
            familyStatus=profile.familyStatus,
            economicsSourceOfKnowledge=profile.economicsSourceOfKnowledge,
            salary=salary,
            hasCredit=profile.hasCredit,
            hasSavings=profile.hasSavings,

            newsSources=[],
            nonDurableGoods=[]
        )