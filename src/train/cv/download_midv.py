# I import the MIDV500 helper package here because this script exists only to
# download the raw CV dataset into the project structure.
import midv500

# I keep the download location explicit so the later preprocessing scripts know
# exactly where to find the raw CV files.
dataset_dir = "data/raw/cv/midv500_data"
dataset_name = "midv500"

# I download the actual dataset files here, not just the package code.
midv500.download_dataset(dataset_dir, dataset_name)

print("Download complete")
