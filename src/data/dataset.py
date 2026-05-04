import cv2
import pandas as pd

try:
    import torch
    from torch.utils.data import Dataset
except ModuleNotFoundError:
    torch = None

    class Dataset:  # type: ignore[override]
        """I keep a fallback base here so the module can still import cleanly without PyTorch."""

        pass


class CVDataset(Dataset):
    def __init__(self, csv_file, split=None, image_size=(224, 224), transform=None):
        # I raise this error early because this dataset class is only useful
        # when PyTorch is installed for model training or inference.
        if torch is None:
            raise ModuleNotFoundError(
                "PyTorch is required for CVDataset. Install it with: pip install torch"
            )

        # I accept either a CSV path or a prepared DataFrame here because
        # some training flows split the labels table before building datasets.
        if isinstance(csv_file, str):
            self.data = pd.read_csv(csv_file)
        else:
            self.data = pd.DataFrame(csv_file).copy()
        if split is not None:
            if "split" not in self.data.columns:
                raise ValueError("CSV file does not contain a 'split' column.")
            self.data = self.data[self.data["split"] == split].reset_index(drop=True)

        # I store image size on the object because every sample should be
        # resized consistently before it is sent to the model.
        self.image_size = tuple(image_size)
        self.transform = transform

    def __len__(self):
        # I return the total number of samples because PyTorch asks the dataset
        # for its size before it builds batches.
        return len(self.data)

    def __getitem__(self, index):
        # I get one row of data
        row = self.data.iloc[index]

        image_path = row["image_path"]
        label_value = row["label"]

        # I load the image here because each dataset item should return the
        # real image data, not just the path string from the CSV.
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image at: {image_path}")

        # I convert BGR to RGB because OpenCV loads in BGR order, while most
        # deep learning workflows expect standard RGB channel order.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if self.transform is not None:
            # I hand the raw RGB image to the transform pipeline because the
            # training script may want augmentation and normalization there.
            image_tensor = self.transform(image)
        else:
            image = cv2.resize(image, self.image_size)
            # I convert the image into a tensor and scale it to 0-1 because neural
            # networks work with numeric tensors rather than raw image arrays.
            image_tensor = torch.tensor(image).permute(2, 0, 1).float() / 255.0

        # I convert the label to a tensor too so training code can use the
        # image and label in the same PyTorch pipeline.
        label_tensor = torch.tensor(label_value).float()

        return image_tensor, label_tensor


if __name__ == "__main__":
    print("I use this file to define the CVDataset class.")
    print("I do not normally run this file by itself.")
    if torch is None:
        print("PyTorch is not installed. Install it with: pip install torch")
