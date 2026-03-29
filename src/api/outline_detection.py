import pandas as pd


def find_my_outliers(file_path, column_name, dataset_nickname):
    # I use this helper to quickly inspect whether one numeric column contains
    # unusually extreme values that may deserve fraud investigation.

    print(f"--- Analyzing {dataset_nickname} ---")

    try:
        # I limit the number of rows here so a quick inspection stays fast.
        dataframe = pd.read_csv(file_path, nrows=10000)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    # I calculate the mean and standard deviation because this file uses the
    # classic "three standard deviations" beginner rule for outliers.
    average = dataframe[column_name].mean()
    variation = dataframe[column_name].std()

    upper_limit = average + (3 * variation)
    lower_limit = average - (3 * variation)

    # I filter values outside the lower and upper bounds so I can inspect the
    # unusual rows directly instead of only printing summary numbers.
    above_upper_limit = dataframe[column_name] > upper_limit
    below_lower_limit = dataframe[column_name] < lower_limit
    my_outliers = dataframe[above_upper_limit | below_lower_limit]

    print(f"Column checked: {column_name}")
    print(f"Average: {average:.2f}")
    print(f"Upper limit: {upper_limit:.2f}")
    print(f"Outliers detected: {len(my_outliers)}")

    if len(my_outliers) > 0:
        print(my_outliers.head(3))

    return my_outliers
