# src/models/simple_cnn.py

import torch
import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self, num_classes=1):
        super().__init__()

        # I define convolution layers
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        # This makes the classifier independent from the input image size.
        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        # I define fully connected layers
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.pool(x)
        x = self.fc(x)
        return x
