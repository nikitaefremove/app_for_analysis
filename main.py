import pandas as pd
import numpy as np

df = pd.read_csv('Испытательное.csv')


def make_col(month: int, year: int, code: str, segment: bool = False) -> pd.Series:
    if segment:
        condition_month = ((df['Месяц'] >= 1) & (df['Месяц'] <= month))
    else:
        condition_month = (df['Месяц'] == month)
    condition_year = (df['Год'] == year)
    condition_code = (df['Код ОКПД-2'] == code)

    all_sum = pd.Series(df[condition_month & condition_year & condition_code] \
                        .count()['Значение'], index=['Российская федерация'])

    if all_sum.iloc[0] == 0:
        idx = ['Российская федерация', 'ДВФО', 'ПФО', 'СЗФО', 'СКФО', 'СФО', 'УФО', 'ЦФО', 'ЮФО']
        col = pd.Series(np.zeros(len(idx), dtype=int), index=idx)
        return col

    group_sum = df[condition_month & condition_year & condition_code] \
        .groupby('Округ') \
        .count()['Значение'].sort_values(ascending=False)

    col = pd.concat([all_sum, group_sum], axis=0)

    return col


def make_df(month: int, year: int, code: str, current: bool = True) -> pd.DataFrame:
    months = ['Jan', 'Feb', 'Mar', 'Apr',
              'May', 'Jun', 'Jul', 'Avg',
              'Sep', 'Oct', 'Nov', 'Dec']
    if current:
        col = make_col(month=month, year=year, code=code)

    else:
        col = make_col(month=month, year=year - 1, code=code)

    output_df = pd.DataFrame(col,
                             columns=[f'{months[month - 1]}_{year}'])
    output_df = output_df.reset_index().rename(columns={'index': 'Регионы РФ'})

    return output_df


def make_df_segment(month: int,
                    year: int,
                    code: str,
                    current: bool = True) -> pd.DataFrame:
    if current:
        col = make_col(month=month, year=year, code=code, segment=True)
        output_df = pd.DataFrame(col,
                                 columns=[f'С начала {year}'])

    else:
        col = make_col(month=month, year=year - 1, code=code, segment=True)

        output_df = pd.DataFrame(col,
                                 columns=[f'С начала {year - 1}'])

    output_df = output_df.reset_index().rename(columns={'index': 'Регионы РФ'})

    return output_df


def differences_df(main_df: pd.DataFrame, current: bool = True) -> pd.DataFrame:
    difference_values = np.where(main_df.iloc[:, 2] == 0, 100,
                                 round(((main_df.iloc[:, 1] - main_df.iloc[:, 2])
                                        / main_df.iloc[:, 2]) * 100, 1))

    difference_values_with_percentage = [str(val) + '%' for val in difference_values]

    if current:
        difference_df = pd.DataFrame(difference_values_with_percentage, columns=['Разница за месяц'])

    else:
        difference_df = pd.DataFrame(difference_values_with_percentage, columns=['Разница за год'])

    return difference_df


def merge_df(month: int, year: int, code: str) -> pd.DataFrame:
    main_df = make_df(month=month, year=year, code=code)

    if month == 1:
        prev_month = 12
        year = year - 1
        prev_year = year - 1
    else:
        prev_month = month - 1
        year = year
        prev_year = year - 1

    to_merge_df = make_df(month=prev_month, year=year, code=code)

    to_merge_df_last_year = make_df(month=prev_month, year=year - 1, code=code)

    main_df_last_year = main_df.merge(to_merge_df_last_year, on='Регионы РФ', how='left')

    main_df = main_df.merge(to_merge_df, on='Регионы РФ', how='left')

    difference_1 = differences_df(main_df)

    difference_2 = differences_df(main_df_last_year, current=False)

    result_1 = pd.concat([main_df, difference_1], axis=1)
    result_2 = pd.concat([main_df_last_year, difference_2], axis=1)

    return result_1.merge(result_2, on='Регионы РФ', how='left')


test = merge_df(month=6, year=2022, code='23.52.10.130')


def merge_df_segment(month: int, year: int, code: str) -> pd.DataFrame:
    main_df = make_df_segment(month=month, year=year, code=code, current=True)

    to_merge_df = make_df_segment(month=month, year=year, code=code, current=False)

    main_df = main_df.merge(to_merge_df, on='Регионы РФ', how='left')

    difference = differences_df(main_df, current=False)
    difference = difference.rename(columns={'Разница за год': 'Разница периодов'})

    result_1 = pd.concat([main_df, difference], axis=1)

    return result_1


def main_df(month: int, year: int, code: str) -> pd.DataFrame:
    first = merge_df(month=month, year=year, code=code)
    second = merge_df_segment(month=month, year=year, code=code)
    return first.merge(second, on='Регионы РФ', how='left')


test = main_df(month=4, year=2021, code='23.52.10.130')

print(test)
