import json
from datetime import date

from Logging.BaseLogger import BaseLogger
from SurveyLogic.SurveyResults.InflationSurveyRespond import InflationSurveyRespond
from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer
from openai import OpenAI
from dataclasses import fields

class BothubSurveyer(BaseSurveyer):
    def __init__(self, modelToUse: str, key: str, logger: BaseLogger):
        self.logger = logger
        self.modelToUse = modelToUse
        self.key=key
        self.baseUrl="https://openai.bothub.chat/v1"  # Or https://openai.bothub.chat/v1

        self.client=OpenAI(
            api_key=self.key,  # Replace with your actual BotHub key
            base_url=self.baseUrl
        )

    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str, surveyDate: date):

        try:
            response = self.client.chat.completions.create(
                model=self.modelToUse,  # Specify any model available on your BotHub account
                messages=[
                    {"role": "system", "content": systemPrompt},
                    {"role": "user", "content": prompt}
                ]
            )

            resp = response.choices[0].message.content
            resp_json = json.loads(resp)

            # Print the text response
            self.logger.logDebug(resp)

            valid_field_names = {f.name for f in fields(InflationSurveyRespond)}
            filtered_data = {k: v for k, v in resp_json.items() if k in valid_field_names}

            result = InflationSurveyRespond(**filtered_data)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")