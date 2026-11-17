import pandas as pd

fileName = '../data/LLMSurveys_Configurations.xlsx'

df = pd.read_excel(fileName, header=0)
print(df)

# Список нужных строк (часть есть в df, части нет)
row_list = ['QWEN 3.6 (без RLMS, -7d от Инфом)', 'QWEN 3.8 (news + RLMS pass -IE + ключ, -7d от Инфом)', 'row3', 'rowY']

# 1) Убедимся, что index — это названия строк
#    (если первая колонка ещё не index, сделаем её index)
df = df.set_index(df.columns[0]) if df.columns[0] != 'name' else df
# Проще и надёжнее так:
# df = df.set_index(df.columns[0])

# 2) Реиндексируем по нужному списку строк.
#    Для отсутствующих строк pandas подставит NaN.
result = df.reindex(row_list)

# 3) Заполняем NaN прочерками
result = result.fillna('—')

print(result)