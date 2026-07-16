from pyreadstat import pyreadstat

pathToIndivisuals = 'RLMS waves\\r33i_os_84.dta'

df, meta = pyreadstat.read_dta(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

print(df['ccj597_1'][0])
print(meta.variable_value_labels['ccj597_1'])

idxes = [0, 1, 2, 3, 4, 5]

for i in idxes:
    print(f'{df['idind'][i]}: {int(df['cch7_1'][i])}.{int(df['cch7_2'][i])}.{int(df['cc_int_y'][i])}')

print(df['cc_int_y'][0])