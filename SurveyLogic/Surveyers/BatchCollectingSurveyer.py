from datetime import date

from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer


class BatchCollectingSurveyer(BaseSurveyer):
    def __init__(self, modelName:str):
        self.modelName = modelName

    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str, surveyDate: date):
        customId = f'{surveyDate.strftime('%d.%m.%Y')}_{respondentId}'
        return self.build_batch_line(customId, systemPrompt, prompt, self.modelName)

    def build_batch_line(self, custom_id, system_prompt:str, user_prompt:str, model:str):
        """
        Формирует словарь для одной строки batch-запроса.

        Параметры:
            custom_id (str): уникальный идентификатор задачи.
            user_prompt (str): текст пользовательского запроса.
            system_prompt (str, optional): системный промпт. Если None — не включается.
            model (str): имя модели.
            max_tokens (int): максимальное число токенов в ответе.

        Возвращает:
            dict: готовый объект для сериализации в JSON.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": messages
            }
        }