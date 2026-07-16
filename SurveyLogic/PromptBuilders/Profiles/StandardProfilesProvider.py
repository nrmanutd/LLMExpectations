from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders.Profiles.BaseProfilesProvider import BaseProfilesProvider
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader


class StandardProfilesProvider(BaseProfilesProvider):
    def __init__(self, folder: Path, profilesLoader: ProfileDataLoader):
        self.folder = folder
        self.profilesLoader = profilesLoader

    def getProfiles(self, surveyDate: date):
        year = str(surveyDate.year)
        subfolders = [p for p in self.folder.iterdir() if p.is_dir()]

        leftDelta = 1000
        rightDelta = -1000

        closestLeftFolder = None
        closestRightFolder = None

        for folder in subfolders:
            if year == folder.name:
                return self.profilesLoader.loadProfiles(folder)

            curDelta = int(year) - int(folder.name)
            if 0 < curDelta < leftDelta:
                closestLeftFolder = folder
                continue

            if 0 > curDelta > rightDelta:
                closestRightFolder = folder
                continue

        if closestLeftFolder is not None:
            return self.profilesLoader.loadProfiles(closestLeftFolder)

        return self.profilesLoader.loadProfiles(closestRightFolder)