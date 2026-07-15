from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer
from openai import OpenAI


class BothubSurveyer(BaseSurveyer):
    def __init__(self, modelToUse: str, key: str):
        self.modelToUse = modelToUse
        self.key=key
        self.baseUrl="https://openai.bothub.chat/v1"  # Or https://openai.bothub.chat/v1

        self.client=OpenAI(
            api_key=self.key,  # Replace with your actual BotHub key
            base_url=self.baseUrl
        )

    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str):
        try:
            response = self.client.chat.completions.create(
                model=self.modelToUse,  # Specify any model available on your BotHub account
                messages=[
                    {"role": "system", "content": systemPrompt},
                    {"role": "user", "content": prompt}
                ]
            )

            # Print the text response
            print(response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")