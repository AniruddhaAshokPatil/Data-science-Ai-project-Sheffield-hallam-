"""I train the computer-vision fraud model in this file."""

import argparse
import logging
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import transforms


# I add the project root to `sys.path` so I can run this file directly and
# still import the shared dataset and model classes.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.dataset import CVDataset  # noqa: E402
from src.models.simple_cnn import SimpleCNN  # noqa: E402
from src.train.model_paths import CV_CNN_MODEL  # noqa: E402


torch.manual_seed(42)
np.random.seed(42)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

DEFAULT_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _build_train_transform(image_size):
    # I use slightly stronger augmentation in training because small image
    # changes can help the model generalize better.
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225],
            ),
        ]
    )


def _build_validation_transform(image_size):
    # I keep validation preprocessing simpler because I want evaluation to be
    # stable and easy to interpret.
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225],
            ),
        ]
    )


def load_dataset(csv_path, validation_split=0.2, image_size=224):
    """I build training and validation datasets from the labels CSV."""
    dataframe = pd.read_csv(csv_path)
    train_transform = _build_train_transform(image_size)
    validation_transform = _build_validation_transform(image_size)

    if "split" in dataframe.columns:
        # I respect the saved split column when the dataset already tells me
        # which rows belong to training or validation.
        train_dataframe = dataframe[dataframe["split"] == "train"]
        validation_dataframe = dataframe[dataframe["split"].isin(["val", "test"])]
        train_dataset = CVDataset(train_dataframe, transform=train_transform)
        validation_dataset = CVDataset(validation_dataframe, transform=validation_transform)
        return train_dataset, validation_dataset

    # I create one dataset first when the CSV has no split column, then I let
    # PyTorch divide it in a reproducible way.
    shuffled_dataframe = dataframe.sample(frac=1, random_state=42).reset_index(drop=True)
    validation_size = max(1, int(len(shuffled_dataframe) * validation_split))
    validation_dataframe = shuffled_dataframe.iloc[:validation_size].reset_index(drop=True)
    train_dataframe = shuffled_dataframe.iloc[validation_size:].reset_index(drop=True)

    train_dataset = CVDataset(train_dataframe, transform=train_transform)
    validation_dataset = CVDataset(validation_dataframe, transform=validation_transform)
    return train_dataset, validation_dataset


def build_model(device=DEFAULT_DEVICE):
    """I rebuild the shared SimpleCNN model and move it onto the device."""
    model = SimpleCNN()
    return model.to(device)


def train_cv_model(
    csv_path,
    epochs=5,
    batch_size=16,
    learning_rate=1e-3,
    validation_split=0.2,
    model_path=CV_CNN_MODEL,
    image_size=224,
):
    """I train the CV model and save the best checkpoint plus metadata."""
    train_dataset, validation_dataset = load_dataset(
        csv_path=csv_path,
        validation_split=validation_split,
        image_size=image_size,
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=batch_size)

    model = build_model()
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    best_validation_loss = float("inf")
    model_path = Path(model_path)

    for epoch_index in range(epochs):
        # I keep training and validation as separate blocks because that makes
        # the learning loop easier to explain step by step.
        model.train()
        total_train_loss = 0.0

        for images, labels in train_loader:
            images = images.to(DEFAULT_DEVICE)
            labels = labels.float().unsqueeze(1).to(DEFAULT_DEVICE)

            logits = model(images)
            loss = criterion(logits, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item() * images.size(0)

        average_train_loss = total_train_loss / len(train_loader.dataset)

        model.eval()
        total_validation_loss = 0.0
        correct_predictions = 0
        total_labels = 0

        with torch.no_grad():
            for images, labels in validation_loader:
                images = images.to(DEFAULT_DEVICE)
                labels = labels.float().unsqueeze(1).to(DEFAULT_DEVICE)

                logits = model(images)
                loss = criterion(logits, labels)
                probabilities = torch.sigmoid(logits)
                predictions = (probabilities > 0.5).float()

                total_validation_loss += loss.item() * images.size(0)
                correct_predictions += (predictions == labels).sum().item()
                total_labels += labels.numel()

        average_validation_loss = total_validation_loss / len(validation_loader.dataset)
        validation_accuracy = correct_predictions / total_labels if total_labels else 0.0

        logging.info(
            "I finished epoch %s with train loss %.4f, validation loss %.4f, and validation accuracy %.4f.",
            epoch_index + 1,
            average_train_loss,
            average_validation_loss,
            validation_accuracy,
        )

        if average_validation_loss < best_validation_loss:
            # I save only the best checkpoint so the final artifact represents
            # the strongest validation result I saw during training.
            best_validation_loss = average_validation_loss
            model_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), model_path)

    metadata = {
        "input_size": (image_size, image_size),
        "threshold": 0.5,
    }
    metadata_path = model_path.with_suffix(".metadata.pkl")
    with metadata_path.open("wb") as metadata_file:
        pickle.dump(metadata, metadata_file)

    logging.info("I saved the best CV model to %s.", model_path)
    logging.info("I saved the CV metadata to %s.", metadata_path)


def parse_args():
    # I expose the main settings here so I can retrain without editing code.
    parser = argparse.ArgumentParser(description="Train the CV fraud model.")
    parser.add_argument("csv_path")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=1e-3)
    parser.add_argument("--validation_split", type=float, default=0.2)
    parser.add_argument("--model_path", default=str(CV_CNN_MODEL))
    parser.add_argument("--image_size", type=int, default=224)
    return parser.parse_args()


def main():
    args = parse_args()
    train_cv_model(
        csv_path=args.csv_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        validation_split=args.validation_split,
        model_path=args.model_path,
        image_size=args.image_size,
    )


if __name__ == "__main__":
    main()
