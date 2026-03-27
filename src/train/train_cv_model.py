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
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.dataset import CVDataset

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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"I am using device: {device}")

# -------------------------------
# STEP 4: Transforms
# -------------------------------

# I am using stronger augmentation for training
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# I keep validation clean
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

    df = pd.read_csv(csv_path)

    if "split" in df.columns:
        train_df = df[df["split"] == "train"]
        val_df = df[df["split"].isin(["val", "test"])]

        train_dataset = CVDataset(train_df, transform=train_transform)
        val_dataset = CVDataset(val_df, transform=val_transform)

    else:
        full_dataset = CVDataset(df, transform=train_transform)

        val_size = max(1, int(len(full_dataset) * validation_split))
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
    I am using ResNet18 with transfer learning
    """

    model = models.resnet18(weights="DEFAULT")

    # Freeze backbone
    for param in model.parameters():
        param.requires_grad = False

    # Replace head for binary classification
    model.fc = nn.Linear(model.fc.in_features, 1)

    return model.to(device)

# -------------------------------
# STEP 7: Training Function
# -------------------------------

def train(csv_path, epochs=5, batch_size=16, lr=1e-3):

    train_dataset, val_dataset = load_dataset(csv_path)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    model = build_model()

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.fc.parameters(), lr=lr)

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

            train_loss += loss.item() * images.size(0)

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

                val_loss += loss.item() * images.size(0)

                probs = torch.sigmoid(logits)
                preds = (probs > 0.5).float()

                correct += (preds == labels).sum().item()
                total += labels.numel()

        val_loss /= len(val_loader.dataset)
        accuracy = correct / total if total else 0

        logging.info(
            f"Epoch {epoch+1} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Acc: {accuracy:.4f}"
        )

        # I save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "models/cv_model.pth")

    # -------------------------------
    # STEP 8: Save Metadata
    # -------------------------------

    metadata = {
        "input_size": (224, 224),
        "threshold": 0.5
    }

    with open("models/cv_metadata.pkl", "wb") as f:
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