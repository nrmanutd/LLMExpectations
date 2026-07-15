from datetime import date

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class CompositePromptBuilder(BasePromptBuilder):
    def __init__(self, builders: list[BasePromptBuilder], headers: list[str]):
        self.headers = headers
        self.builders = builders

    def buildPrompt(self, surveyDate: date, profile: ProfileData) -> str:

        prompts: list[str] = []
        for i in range(len(self.builders)):
            builder = self.builders[i]
            header = self.headers[i]

            curPrompt = builder.buildPrompt(surveyDate, profile)
            h = f'======================{header}======================'
            board = "=" * len(h)

            if i > 0:
                prompts.append(board)
                prompts.append(h)
                prompts.append(board)

            prompts.append(curPrompt)

        result = '\n'.join(prompts)

        return result
