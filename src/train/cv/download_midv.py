# I am importing the dataset package
import midv500

# I define where dataset should be downloaded
dataset_dir = "data/raw/cv/midv500_data"

# I download actual dataset (not code repo)
midv500.download_dataset(dataset_dir, "midv500")

print("Download complete")