from SurveyLogic.SurveyResults.InflationSurveyRespond import InflationSurveyRespond
from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer


class StubSurveyer(BaseSurveyer):
    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str):
        print("============================")
        print(respondentId)
        print(systemPrompt)
        print(prompt)
        print("============================")

        return InflationSurveyRespond(respondent_id="1", expected_inflation_12m_pct=0.15)
