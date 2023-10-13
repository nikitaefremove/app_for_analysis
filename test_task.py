# Import necessary libraries
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('Испытательное.csv')


# Function to create a column for the dataset
def make_col(month: int,
             year: int,
             code: str,
             segment: bool = False) -> pd.Series:
    # Condition to check if data should be segmented by months or a single month
    if segment:
        month_condition = (df['Месяц'] >= 1) & (df['Месяц'] <= month)
    else:
        month_condition = df['Месяц'] == month

    # Condition to filter dataframe by month, year and code
    condition = (month_condition & (df['Год'] == year)
                 & (df['Код ОКПД-2'] == code))

    # Calculate total count of 'Значение' for the condition
    total = pd.Series(df[condition].count()['Значение'],
                      index=['Российская федерация'])

    # Return default series if total count is 0
    if total.iloc[0] == 0:
        idx = ['Российская федерация', 'ДВФО',
               'ПФО', 'СЗФО', 'СКФО', 'СФО',
               'УФО', 'ЦФО', 'ЮФО']
        return pd.Series(np.zeros(len(idx), dtype=int), index=idx)

    # Group the dataframe by 'Округ' and count 'Значение'
    grouped = df[condition].groupby('Округ') \
        .count()['Значение'] \
        .sort_values(ascending=False)

    return pd.concat([total, grouped], axis=0)


# Function to create a dataframe
def make_dataframe(month: int,
                   year: int,
                   code: str,
                   segment: bool = False,
                   current_year: bool = True) -> pd.DataFrame:
    adjusted_year = year if current_year else year - 1
    col = make_col(month, adjusted_year, code, segment)

    # Convert month number to month name
    month_name = ['Jan', 'Feb', 'Mar',
                  'Apr', 'May', 'Jun',
                  'Jul', 'Avg', 'Sep',
                  'Oct', 'Nov', 'Dec'][month - 1]
    column_name = f'{month_name}_{adjusted_year}' \
        if not segment else f'С начала {adjusted_year}'

    # Construct dataframe
    result_df = pd.DataFrame(col, columns=[column_name]) \
        .reset_index() \
        .rename(columns={'index': 'Регионы РФ'})
    return result_df


# Function to calculate difference
def calculate_difference(main_data: pd.DataFrame,
                         current: bool = True) -> pd.DataFrame:
    col_name = 'Разница за месяц' if current else 'Разница за год'
    difference = np.where(main_data.iloc[:, 2] == 0, 100,
                          round((main_data.iloc[:, 1] - main_data.iloc[:, 2])
                                / main_data.iloc[:, 2] * 100, 1))
    return pd.DataFrame([f"{val}%" for val in difference],
                        columns=[col_name])


# Main function to generate the required dataframe
def main_df(month: int,
            year: int,
            code: str) -> pd.DataFrame:
    base_df = make_dataframe(month, year, code)

    # Determine previous month and year
    prev_month, prev_year = (12, year - 1) if month == 1 else (month - 1, year)

    month_comparison_df = make_dataframe(prev_month, prev_year, code)
    year_comparison_df = make_dataframe(prev_month,
                                        prev_year - 1,
                                        code)

    merged_year = base_df.merge(year_comparison_df,
                                on='Регионы РФ',
                                how='left')

    base_df = base_df.merge(month_comparison_df,
                            on='Регионы РФ',
                            how='left')

    difference_current = calculate_difference(base_df)
    difference_year = calculate_difference(merged_year,
                                           current=False)

    result_df = pd.concat([base_df, difference_current], axis=1)
    result_year_df = pd.concat([merged_year, difference_year], axis=1)

    final_df = result_df.merge(result_year_df,
                               on='Регионы РФ',
                               how='left')

    segment_df = make_dataframe(month, year, code,
                                segment=True)
    segment_comparison_df = make_dataframe(month, year, code,
                                           segment=True,
                                           current_year=False)

    segment_df = segment_df.merge(segment_comparison_df,
                                  on='Регионы РФ',
                                  how='left')

    segment_difference = calculate_difference(segment_df,
                                              current=False).rename(
        columns={'Разница за год': 'Разница периодов'})
    segment_final = pd.concat([segment_df, segment_difference], axis=1)

    return final_df.merge(segment_final,
                          on='Регионы РФ',
                          how='left')


# Test the main function
test_result = main_df(4, 2022, '23.52.10.130')
print(test_result)
