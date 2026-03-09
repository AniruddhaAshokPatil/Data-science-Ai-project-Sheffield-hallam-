import pandas as pd

def find_my_outliers(file_path, column_name, dataset_nickname):

    print(f"--- Analyzing {dataset_nickname} ---")

    try:
        df = pd.read_csv(file_path, nrows=10000)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return

    average = df[column_name].mean()
    variation = df[column_name].std()

    upper_limit = average + (3 * variation)
    lower_limit = average - (3 * variation)

    my_outliers = df[(df[column_name] > upper_limit) |(df[column_name] < lower_limit)]

    print(f"Column checked: {column_name}")
    print(f"Average: {average:.2f}")
    print(f"Upper limit: {upper_limit:.2f}")
    print(f"Outliers detected: {len(my_outliers)}")

    if len(my_outliers) > 0:
        print(my_outliers.head(3))

    return my_outliers

