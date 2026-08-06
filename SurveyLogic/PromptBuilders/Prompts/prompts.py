from pathlib import Path

promptsPath = 'SurveyLogic/PromptBuilders/Prompts'
inflationPath = 'data/Inflation'
politicsPath = 'data/Politics'

systemPrompt = Path(f'{promptsPath}/systemPromptTemplate_v1.txt').read_text(encoding="utf-8")
respondentPrompt = Path(f'{promptsPath}/commonRespondentPromptTemplate.txt').read_text(encoding="utf-8")
taskPrompt = Path(f'{promptsPath}/taskPromptTemplate.txt').read_text(encoding="utf-8")

stateCommonPoliticalPrompt=Path(f'{promptsPath}/stateCommonPoliticalPrompt_0625.txt').read_text(encoding="utf-8")

stateInflationPrompt=Path(f'{promptsPath}/stateCommonInflationPrompt.txt').read_text(encoding="utf-8")
regionInflationPrompt=Path(f'{promptsPath}/regionCommonInflationPrompt.txt').read_text(encoding="utf-8")
househouldCommonPrompt=Path(f'{promptsPath}/householdCommonPrompt.txt').read_text(encoding="utf-8")

expensesPrompt=Path(f'{promptsPath}/expensesPromptTemplate.txt').read_text(encoding="utf-8")
stateWeeklyExpensesPrompt=Path(f'{promptsPath}/stateExpensesPromptTemplate.txt').read_text(encoding="utf-8")