from SurveyLogic.surveyHelpers import extractDatesFromFile

dates = extractDatesFromFile('../data/ExpectedInflationSurveysDates.xlsx')
print(dates)