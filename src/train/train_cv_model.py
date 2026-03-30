# src/train/train_cv_model.py

import os
import sys
import logging
import pickle
import numpy as np
import pandas as pd
from pathlib import Path

import torch
from torch import nn, optim
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, models

# -------------------------------
# STEP 0: Project Path Setup
# -------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# I add the project root to sys.path so this training script can import the
# shared dataset class even when I run the file directly from the terminal.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.dataset import CVDataset
from src.models.simple_cnn import SimpleCNN
from src.train.model_paths import CV_CNN_MODEL

# -------------------------------
# STEP 1: Reproducibility
# -------------------------------

torch.manual_seed(42)
np.random.seed(42)

# -------------------------------
# STEP 2: Logging
# -------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------
# STEP 3: Device
# -------------------------------

# I choose GPU when available because CV training is heavier than many tabular
# tasks, but I still want the script to work on CPU-only machines too.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"I am using device: {device}")

# -------------------------------
# STEP 4: Transforms
# -------------------------------

# I use stronger augmentation for training because CV models usually generalize
# better when they see small random variations of the images.
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# I keep validation cleaner because I want evaluation to measure model quality
# on stable inputs rather than adding extra randomness during validation.
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# -------------------------------
# STEP 5: Dataset Loader
# -------------------------------

def load_dataset(csv_path, validation_split=0.2):
    """
    I handle both:
    - CSV with split column
    - CSV without split column
    """

    # I read the labels CSV here because it defines the image paths, labels,
    # and sometimes the train/test split for the CV dataset.
    df = pd.read_csv(csv_path)

    if "split" in df.columns:
        train_df = df[df["split"] == "train"]
        validation_mask = df["split"].isin(["val", "test"])
        val_df = df[validation_mask]

        train_dataset = CVDataset(train_df, transform=train_transform)
        val_dataset = CVDataset(val_df, transform=val_transform)

    else:
        # I create one full dataset first when no split column exists, then I
        # let PyTorch divide it into train and validation subsets.
        full_dataset = CVDataset(df, transform=train_transform)

        dataset_size = len(full_dataset)
        val_size = max(1, int(dataset_size * validation_split))
        train_size = len(full_dataset) - val_size

        train_dataset, val_dataset = random_split(
            full_dataset,
            [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )

    return train_dataset, val_dataset

# -------------------------------
# STEP 6: Model
# -------------------------------

def build_model():
    """
    I use the shared SimpleCNN architecture here because the API loader expects
    the same model shape when it later restores the saved CV weights.
    """
    model = SimpleCNN()
    return model.to(device)

# -------------------------------
# STEP 7: Training Function
# -------------------------------

def train(csv_path, epochs=5, batch_size=16, lr=1e-3):

    # I separate dataset loading from training so this function can focus on
    # optimization logic after the images are prepared.
    train_dataset, val_dataset = load_dataset(csv_path)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    model = build_model()

    # I use BCEWithLogitsLoss because this is a binary classification problem
    # and the model returns one raw logit for each image.
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_val_loss = float("inf")

    for epoch in range(epochs):

        # ---------------- TRAIN ----------------
        model.train()
        train_loss = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.float().unsqueeze(1).to(device)

            logits = model(images)
            loss = criterion(logits, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            batch_size_now = images.size(0)
            train_loss += loss.item() * batch_size_now

        train_loss /= len(train_loader.dataset)

        # ---------------- VALIDATION ----------------
        model.eval()
        val_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.float().unsqueeze(1).to(device)

                logits = model(images)
                loss = criterion(logits, labels)

                batch_size_now = images.size(0)
                val_loss += loss.item() * batch_size_now

                probs = torch.sigmoid(logits)
                preds = (probs > 0.5).float()

                batch_correct = (preds == labels).sum().item()
                correct += batch_correct
                total += labels.numel()

        val_loss /= len(val_loader.dataset)
        accuracy = correct / total if total else 0

        epoch_number = epoch + 1
        logging.info(
            f"Epoch {epoch_number} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Acc: {accuracy:.4f}"
        )

        # I save only the best checkpoint so the final artifact represents the
        # strongest validation result seen during training.
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            CV_CNN_MODEL.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), CV_CNN_MODEL)

    # -------------------------------
    # STEP 8: Save Metadata
    # -------------------------------

    # I save simple metadata too because inference code may need the expected
    # image size and threshold alongside the model weights.
    metadata = {
        "input_size": (224, 224),
        "threshold": 0.5
    }

    metadata_path = CV_CNN_MODEL.with_suffix(".metadata.pkl")
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    logging.info("I have saved the best CV model and metadata.")

# -------------------------------
# STEP 9: CLI
# -------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=16)

    args = parser.parse_args()

    train(args.csv_path, args.epochs, args.batch_size)
