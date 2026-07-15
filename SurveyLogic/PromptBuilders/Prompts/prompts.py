from pathlib import Path

promptsPath = 'SurveyLogic/PromptBuilders/Prompts'

systemPrompt = Path(f'{promptsPath}/systemPromptTemplate_v1.txt').read_text(encoding="utf-8")
respondentPrompt = Path(f'{promptsPath}/commonRespondentPromptTemplate.txt').read_text(encoding="utf-8")
taskPrompt = Path(f'{promptsPath}/taskPromptTemplate.txt').read_text(encoding="utf-8")

stateEconomyPrompt=Path(f'{promptsPath}/stateCommonEconomyPrompt_0625.txt').read_text(encoding="utf-8")
stateCommonPoliticalPrompt=Path(f'{promptsPath}/stateCommonPoliticalPrompt_0625.txt').read_text(encoding="utf-8")