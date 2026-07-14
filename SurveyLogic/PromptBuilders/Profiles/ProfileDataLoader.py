import glob
import json
import os
from dataclasses import fields

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class ProfileDataLoader:

    def loadProfile(self, filePath) -> ProfileData:
        with open(filePath, 'r', encoding='utf-8') as ff:
            profile = json.load(ff)

        valid_field_names = {f.name for f in fields(ProfileData)}
        filtered_data = {k: v for k, v in profile.items() if k in valid_field_names}

        profile = ProfileData(**filtered_data)

        return profile

    def loadProfiles(self, folderPath) -> list[ProfileData]:
        pattern = os.path.join(folderPath, "*.json")
        json_files = glob.glob(pattern)

        resultProfiles = []

        for f in json_files:
            resultProfiles.append(self.loadProfile(f))

        return resultProfiles
