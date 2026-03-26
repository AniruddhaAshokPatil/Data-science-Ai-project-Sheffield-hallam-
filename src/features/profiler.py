import pandas as pd

# 1. SETTING MY FILE PATHS
# I am saving your specific paths here so I can find my files easily
card_data_path = '/Users/productguru/Documents/GitHub/Data-science-Ai-project-Sheffield-hallam-/data/card_transdata.csv'
financial_data_path = '/Users/productguru/Documents/GitHub/Data-science-Ai-project-Sheffield-hallam-/data/financial_fraud_detection_dataset 2.csv'

# 2. MY OUTLIER DISCOVERY FUNCTION
# I wrote this function so I can reuse it for any column in any dataset
def find_my_outliers(file_path, column_name, dataset_nickname):
    print(f"--- I am now analyzing the {dataset_nickname} ---")
    
    # I am loading 10,000 rows to keep my testing fast and stable
    try:
        df = pd.read_csv(file_path, nrows=10000)
    except FileNotFoundError:
        print(f"I couldn't find the file at: {file_path}. Please check the path!")
        return

    # I need to find the average (mean) and the typical 'variation' (std)
    average = df[column_name].mean()
    variation = df[column_name].std()

    # I am setting my "Danger Zone" boundaries (3 standard deviations away)
    upper_limit = average + (3 * variation)
    lower_limit = average - (3 * variation)

    # I am creating a sub-list of only the transactions that crossed my limits
    my_outliers = df[(df[column_name] > upper_limit) | (df[column_name] < lower_limit)]

    # 3. PRINTING MY RESULTS
    print(f"I'm checking the column: '{column_name}'")
    print(f"The average is {average:.2f}. Anything above {upper_limit:.2f} is an outlier.")
    print(f"I detected {len(my_outliers)} outliers in this sample.")
    
    # If I found any outliers, I want to see the first 3 rows to study them
    if len(my_outliers) > 0:
        print("A quick look at my flagged transactions:")
        print(my_outliers.head(3))
    
    print("-" * 50)

if __name__ == "__main__":
    # FIRST: I'll check my Card Data for price anomalies
    # I'm using 'ratio_to_median_purchase_price' because it's a classic fraud signal
    find_my_outliers(card_data_path, 'ratio_to_median_purchase_price', "Card Transaction Data")

    # SECOND: I'll check my Financial Data for spending anomalies
    # I'm using 'spending_deviation_score' because it shows when someone changes their habits
    find_my_outliers(financial_data_path, 'spending_deviation_score', "Financial Fraud Data")
