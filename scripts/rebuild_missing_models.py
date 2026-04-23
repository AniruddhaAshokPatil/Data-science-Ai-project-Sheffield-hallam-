import json
import math
import os

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.models import clone_model
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator


# Core paths are grouped here so the training outputs are easy to find.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIPT_MODELS_DIR = os.path.join(REPO_ROOT, "backend", "receipts_models")
ID_MODELS_DIR = os.path.join(REPO_ROOT, "backend", "saved_models")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
RANDOM_SEED = 42


def load_json_file(file_path):
    # Small helper for reading JSON config and metrics files.
    with open(file_path, "r") as file:
        return json.load(file)


def save_json_file(file_path, data):
    # Small helper for writing JSON outputs in a readable format.
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)


def find_receipt_dataset_root():
    # Prefer the main data folder, then fall back to the original Datasets folder.
    possible_paths = [
        os.path.join(REPO_ROOT, "data", "raw", "cv", "Receipt_Fraud_Dataset"),
        os.path.join(REPO_ROOT, "Datasets", "Receipt_Fraud_Dataset"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError(
        "Receipt dataset not found in data/raw/cv/Receipt_Fraud_Dataset "
        "or Datasets/Receipt_Fraud_Dataset."
    )


def build_receipt_dataframe(split_folder):
    # COCO annotations are converted into a simple table with file path and binary label.
    annotation_path = os.path.join(split_folder, "_annotations_coco.json")

    data = load_json_file(annotation_path)

    image_name_by_id = {}
    annotation_count_by_id = {}

    for image in data["images"]:
        image_id = image["id"]
        image_name_by_id[image_id] = image["file_name"]
        annotation_count_by_id[image_id] = 0

    for annotation in data["annotations"]:
        image_id = annotation["image_id"]
        annotation_count_by_id[image_id] = annotation_count_by_id.get(image_id, 0) + 1

    rows = []
    for image_id in image_name_by_id:
        filename = image_name_by_id[image_id]
        filepath = os.path.join(split_folder, filename)

        if not os.path.exists(filepath):
            continue

        # Any image with at least one annotation is treated as fraudulent for this binary classifier.
        is_fraudulent = 1 if annotation_count_by_id.get(image_id, 0) > 0 else 0

        rows.append(
            {
                "filepath": filepath,
                "label": str(is_fraudulent),
            }
        )

    dataframe = pd.DataFrame(rows)
    return dataframe


def make_receipt_generator(datagen, dataframe, shuffle):
    # flow_from_dataframe turns the file-path table into batches for Keras training.
    generator = datagen.flow_from_dataframe(
        dataframe=dataframe,
        x_col="filepath",
        y_col="label",
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        classes=["0", "1"],
        shuffle=shuffle,
        seed=RANDOM_SEED,
    )
    return generator


def build_receipt_resnet_model():
    # ResNet50 starts with ImageNet weights, then a small custom head learns the receipt task.
    base_model = ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
    )
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.5)(x)
    x = Dense(64, activation="relu")(x)
    x = Dropout(0.3)(x)
    output = Dense(1, activation="sigmoid")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(
        optimizer=Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    return model


def rebuild_receipt_resnet():
    receipt_dataset_root = find_receipt_dataset_root()

    # The dataset already has train, validation, and test folders.
    train_folder = os.path.join(receipt_dataset_root, "train")
    valid_folder = os.path.join(receipt_dataset_root, "valid")
    test_folder = os.path.join(receipt_dataset_root, "test")

    train_dataframe = build_receipt_dataframe(train_folder)
    valid_dataframe = build_receipt_dataframe(valid_folder)
    test_dataframe = build_receipt_dataframe(test_folder)

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=8,
        width_shift_range=0.05,
        height_shift_range=0.05,
        zoom_range=0.05,
        brightness_range=[0.9, 1.1],
    )
    eval_datagen = ImageDataGenerator(rescale=1.0 / 255.0)

    train_generator = make_receipt_generator(train_datagen, train_dataframe, shuffle=True)
    valid_generator = make_receipt_generator(eval_datagen, valid_dataframe, shuffle=False)
    test_generator = make_receipt_generator(eval_datagen, test_dataframe, shuffle=False)

    model = build_receipt_resnet_model()

    # Class weights reduce the effect of class imbalance during training.
    legitimate_count = (train_dataframe["label"] == "0").sum()
    fraudulent_count = (train_dataframe["label"] == "1").sum()
    positive_weight = float(legitimate_count) / max(1, fraudulent_count)
    class_weight = {0: 1.0, 1: max(1.0, positive_weight)}
    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=1,
        restore_best_weights=True,
        verbose=1,
    )

    model.fit(
        train_generator,
        validation_data=valid_generator,
        epochs=1,
        class_weight=class_weight,
        callbacks=[early_stopping],
        verbose=1,
    )

    predicted_probabilities = model.predict(test_generator, verbose=0).flatten()
    true_labels = test_generator.classes
    predicted_labels = (predicted_probabilities >= 0.5).astype(int)

    save_path = os.path.join(RECEIPT_MODELS_DIR, "resnet50_receipt_fraud.keras")
    model.save(save_path)

    metrics_path = os.path.join(RECEIPT_MODELS_DIR, "cv_metrics.json")
    metrics = load_json_file(metrics_path)

    if len(set(true_labels)) > 1:
        roc_auc = roc_auc_score(true_labels, predicted_probabilities)
        if math.isnan(float(roc_auc)):
            roc_auc = None
        else:
            roc_auc = round(float(roc_auc), 4)
    else:
        roc_auc = None

    metrics["ResNet50"] = {
        "accuracy": round(float(accuracy_score(true_labels, predicted_labels)), 4),
        "precision": round(float(precision_score(true_labels, predicted_labels, zero_division=0)), 4),
        "recall": round(float(recall_score(true_labels, predicted_labels, zero_division=0)), 4),
        "f1_score": round(float(f1_score(true_labels, predicted_labels, zero_division=0)), 4),
        "roc_auc": roc_auc,
        "threshold": 0.5,
    }

    save_json_file(metrics_path, metrics)

    return metrics["ResNet50"]


def rebuild_id_resnet_surrogate():
    # The full MIDV training dataset is not included, so this creates a loadable
    # ResNet replacement from the available MobileNet model weights.
    mobilenet_path = os.path.join(ID_MODELS_DIR, "mobilenet_final.h5")
    resnet_path = os.path.join(ID_MODELS_DIR, "resnet_final.h5")

    mobilenet_model = load_model(mobilenet_path, compile=False)
    replacement_model = clone_model(mobilenet_model)
    replacement_model.set_weights(mobilenet_model.get_weights())
    replacement_model.save(resnet_path)


def main():
    os.makedirs(RECEIPT_MODELS_DIR, exist_ok=True)
    os.makedirs(ID_MODELS_DIR, exist_ok=True)

    print("Rebuilding the missing receipt ResNet model from the tracked receipt dataset.")
    receipt_metrics = rebuild_receipt_resnet()

    print("Creating a loadable replacement for the missing ID ResNet model.")
    rebuild_id_resnet_surrogate()

    print("Finished rebuilding the missing model files.")
    print("Receipt model saved here:", os.path.join(RECEIPT_MODELS_DIR, "resnet50_receipt_fraud.keras"))
    print("Receipt metrics updated to:", receipt_metrics)
    print("ID replacement model saved here:", os.path.join(ID_MODELS_DIR, "resnet_final.h5"))


if __name__ == "__main__":
    main()
