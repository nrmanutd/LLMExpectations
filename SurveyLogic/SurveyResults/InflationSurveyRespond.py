from dataclasses import dataclass
from typing import Optional


@dataclass
class InflationSurveyRespond:
    respondent_id: str

    expected_inflation_12m_pct: Optional[float] = None
    expected_inflation_category: Optional[str] = None
    certainty_0_100: Optional[int] = None
    perceived_personal_price_pressure: Optional[str] = None
    attention_to_inflation: Optional[str] = None
    main_anchor: Optional[str] = None
    secondary_anchors: Optional[str] = None
    short_explanation: Optional[str] = None


