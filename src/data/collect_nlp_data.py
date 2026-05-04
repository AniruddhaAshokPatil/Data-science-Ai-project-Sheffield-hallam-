import os
import pandas as pd

# I define the output path once here because this helper file exists to fetch
# the raw NLP dataset and place it into the project data folder.
OUTPUT_PATH = "data/raw/nlp/sms_spam.csv"

# I keep the source URL in a variable so it is easy for me to see where the
# dataset came from and update it later if the source changes.
SOURCE_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"


def main():
    # I create the output folder first so saving the dataset does not fail.
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # I read the source as a TSV file because this dataset uses tabs instead of commas.
    dataframe = pd.read_csv(SOURCE_URL, sep="\t", header=None)
    dataframe.columns = ["label", "message"]

    dataframe.to_csv(OUTPUT_PATH, index=False)

    print("I downloaded the NLP dataset successfully.")
    print("Shape of dataset:", dataframe.shape)
    print(dataframe.head())


if __name__ == "__main__":
    main()
