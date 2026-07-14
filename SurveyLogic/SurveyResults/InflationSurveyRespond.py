from dataclasses import dataclass

@dataclass
class InflationSurveyRespond:
    respondentId: str
    inflation1Y: float
