# src/models/simple_cnn.py

import torch
import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self, num_classes=1):
        # I call super().__init__() because this class extends nn.Module, and
        # PyTorch needs the parent module setup to happen first.
        super().__init__()

        # I keep the convolution block together because these layers extract
        # visual patterns like edges, shapes, and textures from the image.
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        # I use adaptive pooling so the classifier head can stay simpler and
        # less sensitive to small input-size differences.
        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        # I keep the fully connected block separate because this is the part
        # that turns learned image features into the final fraud logit.
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        # I define the forward pass step by step so it is clear how the image
        # moves from feature extraction into the final classifier output.
        x = self.conv(x)
        x = self.pool(x)
        x = self.fc(x)
        return x
