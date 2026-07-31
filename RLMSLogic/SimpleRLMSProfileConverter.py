from RLMSLogic.RLMSProfileData import RLMSProfileData
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class SimpleRLMSProfileConverter:
    def convert(self, profile: RLMSProfileData) -> ProfileData:


        age = int(profile.age)

        return ProfileData(
            respondentId=profile.respondentId,
            age=age,
            sex=profile.sex,
            education=profile.education,
            LocalityOfBirth=profile.LocalityOfBirth,
            currentLocality=profile.currentLocality,
            currentLocalityRegion=profile.currentLocalityRegion,
            typeOfLocality=profile.typeOfLocality,
            job=profile.job,
            jobSector=profile.jobSector,
            currentStatus=profile.currentStatus,
            nationality=profile.nationality,
            familyStatus=profile.familyStatus,
            economicsSourceOfKnowledge=profile.economicsSourceOfKnowledge,
            salary=profile.salary,
            hasCredit=profile.hasCredit,
            hasSavings=profile.hasSavings,

            newsSources=[],
            nonDurableGoods=[]
        )