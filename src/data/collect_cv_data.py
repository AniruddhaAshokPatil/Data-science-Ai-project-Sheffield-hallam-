import os

# I keep the expected dataset path at the top because this helper is only
# meant to confirm whether the MIDV500 CV dataset is present locally.
DATASET_PATH = "data/raw/cv/midv500_data/midv500"


def count_files_in_dataset(dataset_path):
    # I count files so I can quickly tell whether the dataset looks complete.
    file_count = 0

    for _, _, files in os.walk(dataset_path):
        file_count += len(files)

    return file_count


def print_example_folder(dataset_path):
    # I print one folder example because it helps me see how the dataset is organised.
    for folder_name, _, files in os.walk(dataset_path):
        print("\nExample folder path:", folder_name)
        print("Number of files in this folder:", len(files))
        break


def main():
    # I check that the folder exists first because the rest of the CV work
    # depends on these raw files being in the expected place.
    if os.path.exists(DATASET_PATH):
        print("I found the dataset folder.")
        print("Total number of files in dataset:", count_files_in_dataset(DATASET_PATH))
        print_example_folder(DATASET_PATH)
    else:
        print("I could not find the dataset.")
        print("I need to download MIDV-500 and place it in:")
        print("   data/raw/cv/midv500/")


if __name__ == "__main__":
    main()
