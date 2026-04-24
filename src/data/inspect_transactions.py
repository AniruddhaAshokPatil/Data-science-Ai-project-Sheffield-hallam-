import pandas as pd

# I load the raw transaction and identity files here because this helper is
# meant to give me a quick first look at the original fraud data sources.
TRANS_PATH = "data/raw/transactions/train_transaction.csv"
ID_PATH = "data/raw/transactions/train_identity.csv"


def main():
    dataframe_transactions = pd.read_csv(TRANS_PATH)
    dataframe_identity = pd.read_csv(ID_PATH)

    # I print shapes and columns first because understanding the size and layout
    # of the raw data helps me decide what cleaning and modeling steps come next.
    print("Transaction shape:", dataframe_transactions.shape)
    print("Identity shape:", dataframe_identity.shape)

    print("\nTransaction columns:")
    print(dataframe_transactions.columns)

    print("\nIdentity columns:")
    print(dataframe_identity.columns)

    # I inspect the fraud label distribution because class imbalance is one of the
    # most important things to know before building a fraud model.
    print("\nFraud distribution:")
    print(dataframe_transactions["isFraud"].value_counts(normalize=True))

    # I check missing values because fraud datasets often contain many sparse
    # columns, and that strongly affects later cleaning choices.
    print("\nTop missing values (transaction):")
    print(dataframe_transactions.isnull().sum().sort_values(ascending=False).head(10))

    # I print a small sample at the end because raw tables are easier to understand
    # when I can actually see a few example rows, not only summaries.
    print("\nSample data:")
    print(dataframe_transactions.head())


if __name__ == "__main__":
    main()
