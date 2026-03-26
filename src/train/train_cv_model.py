import argparse
import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, random_split

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.dataset import CVDataset
from src.models.simple_cnn import SimpleCNN
from src.train.model_paths import CV_CNN_MODEL


def train_cv_model(
    csv_path,
    epochs=5,
    batch_size=16,
    learning_rate=1e-3,
    validation_split=0.2,
    model_path=CV_CNN_MODEL,
    image_size=224,
):
    csv_columns = None
    split_series = None
    try:
        import pandas as pd

        csv_columns = pd.read_csv(csv_path, nrows=0).columns.tolist()
        if "split" in csv_columns:
            split_series = pd.read_csv(csv_path, usecols=["split"])["split"]
    except Exception:
        csv_columns = None
        split_series = None

    if split_series is not None:
        available_splits = set(split_series.dropna().astype(str).str.lower())
        eval_split = "val" if "val" in available_splits else "test" if "test" in available_splits else None

        if "train" not in available_splits or eval_split is None:
            raise ValueError("CSV split column exists, but usable train/val or train/test rows were not found.")

        train_dataset = CVDataset(csv_path, split="train", image_size=(image_size, image_size))
        validation_dataset = CVDataset(csv_path, split=eval_split, image_size=(image_size, image_size))

        if len(train_dataset) == 0 or len(validation_dataset) == 0:
            raise ValueError("CSV split column exists, but train or evaluation rows are empty.")
    else:
        dataset = CVDataset(csv_path, image_size=(image_size, image_size))
        if len(dataset) < 2:
            raise ValueError("The CV dataset must contain at least 2 samples.")

        validation_size = max(1, int(len(dataset) * validation_split))
        train_size = len(dataset) - validation_size
        if train_size == 0:
            train_size = len(dataset) - 1
            validation_size = 1

        train_dataset, validation_dataset = random_split(
            dataset,
            [train_size, validation_size],
            generator=torch.Generator().manual_seed(42),
        )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=batch_size, shuffle=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SimpleCNN().to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device).view(-1, 1)

            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

        train_loss = running_loss / len(train_loader.dataset)

        model.eval()
        validation_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in validation_loader:
                images = images.to(device)
                labels = labels.to(device).view(-1, 1)

                logits = model(images)
                loss = criterion(logits, labels)
                validation_loss += loss.item() * images.size(0)

                predictions = (torch.sigmoid(logits) >= 0.5).float()
                correct += (predictions == labels).sum().item()
                total += labels.numel()

        avg_validation_loss = validation_loss / len(validation_loader.dataset)
        validation_accuracy = correct / total if total else 0.0

        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"- train_loss: {train_loss:.4f} "
            f"- val_loss: {avg_validation_loss:.4f} "
            f"- val_acc: {validation_accuracy:.4f}"
        )

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)
    print(f"Saved CV model to: {model_path}")
    return model_path


def parse_args():
    parser = argparse.ArgumentParser(description="Train the SimpleCNN CV model.")
    parser.add_argument("csv_path", help="CSV file with image_path and label columns.")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--validation-split", type=float, default=0.2)
    parser.add_argument("--model-path", default=str(CV_CNN_MODEL))
    parser.add_argument("--image-size", type=int, default=224)
    return parser.parse_args()


if __name__ == "__main__":
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
