import numpy as np
import pandas as pd
import re

def safe_filename(respondent_id: str) -> str:
    """Очищает идентификатор для использования в имени файла."""
    return re.sub(r'[^\w\-]', '_', str(respondent_id))

def norm(x):
    """Преобразует pandas-значение в стандартный Python-тип, заменяя NaN на None."""
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer, np.floating)):
        return x.item()
    return x


def value_to_label(var: str, value, meta):
    """Возвращает текстовую метку для закодированного значения переменной."""
    value = norm(value)
    if value is None:
        return None
    labels = meta.variable_value_labels.get(var, {})
    if not labels:
        return value
    if value in labels:
        return labels[value]
    if isinstance(value, float) and value.is_integer() and int(value) in labels:
        return labels[int(value)]
    return value


