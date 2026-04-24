# src/data/preprocess_cv_data.py

import csv
import os
import random

import cv2
import numpy as np

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

# I define the raw CV input folder here because this whole file is responsible
# for turning the MIDV500 document images into a smaller training-ready dataset.
INPUT_FOLDER = "data/raw/cv/midv500_data/midv500"

# I keep one base output folder because train/test images and labels should all
# live under the same processed CV area of the project.
OUTPUT_BASE = "data/processed/cv"

# I define these processing settings at the top so I can control image size,
# dataset size, and split ratio without editing logic lower in the file.
IMAGE_SIZE = (224, 224)
MAX_IMAGES = 200
TRAIN_RATIO = 0.8

# I set random seeds because I want the same shuffled image sample and the same
# synthetic distortions when I rerun preprocessing for debugging or training.
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# I list valid image suffixes here so I can safely ignore unrelated files while
# scanning the raw CV dataset folders.
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}

# -----------------------------------------
# OUTPUT PATHS
# -----------------------------------------

TRAIN_ORIG = os.path.join(OUTPUT_BASE, "train", "original")
TRAIN_DIST = os.path.join(OUTPUT_BASE, "train", "distorted")
TEST_ORIG = os.path.join(OUTPUT_BASE, "test", "original")
TEST_DIST = os.path.join(OUTPUT_BASE, "test", "distorted")

LABELS_PATH = os.path.join(OUTPUT_BASE, "labels.csv")

for path in [TRAIN_ORIG, TRAIN_DIST, TEST_ORIG, TEST_DIST]:
    # I create the output folders up front so later save operations do not fail.
    os.makedirs(path, exist_ok=True)

# -----------------------------------------
# FRAUD DISTORTION FUNCTIONS
# -----------------------------------------

def apply_blur(image):
    # I use blur to simulate low-quality capture because poor image clarity can
    # be one sign that a document image is suspicious or manipulated.
    return cv2.GaussianBlur(image, (5, 5), 0)


def apply_rotation(image):
    # I rotate the image slightly because document misalignment is a simple way
    # to create a harder, more realistic CV fraud example.
    image_height, image_width = image.shape[:2]
    image_center = (image_width // 2, image_height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(image_center, 10, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image_width, image_height))
    return rotated_image


def apply_noise(image):
    # I add noise because compression artefacts and low-quality edits are common
    # distortions that a document fraud model may need to handle.
    noise = np.random.randint(0, 50, image.shape, dtype=np.uint8)
    return cv2.add(image, noise)


def apply_brightness(image):
    # I adjust brightness because lighting changes can hide or alter details
    # that matter in document verification.
    brightness_value = 40
    brightness_layer = np.full(image.shape, brightness_value, dtype=np.uint8)
    brightened_image = cv2.add(image, brightness_layer)
    return brightened_image


def apply_occlusion(image):
    # I create an occlusion because deliberate masking is a stronger fraud-like
    # distortion than a small blur or lighting change.
    output = image.copy()
    image_height, image_width, _ = output.shape
    x1 = int(image_width * 0.3)
    x2 = int(image_width * 0.7)
    y1 = int(image_height * 0.3)
    y2 = int(image_height * 0.7)
    output[y1:y2, x1:x2] = 0
    return output


DISTORTION_FUNCTIONS = {
    "blur": apply_blur,
    "rotation": apply_rotation,
    "noise": apply_noise,
    "brightness": apply_brightness,
    "occlusion": apply_occlusion,
}

# I keep rough severity weights here because some downstream scoring or analysis
# may want to know that certain distortions are more serious than others.
DISTORTION_SEVERITY = {
    "blur": 0.3,
    "rotation": 0.4,
    "noise": 0.5,
    "brightness": 0.6,
    "occlusion": 0.9,
}

# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------

def load_image_safe(path):
    # I load images through one helper so failed reads are handled consistently
    # instead of breaking the whole preprocessing loop.
    image = cv2.imread(str(path))
    if image is None:
        print(f"[WARNING] Failed to load image: {path}")
        return None
    resized_image = cv2.resize(image, IMAGE_SIZE)
    return resized_image


def extract_doc_type(path):
    # I infer document type from the folder name because MIDV500 organizes
    # different document groups by directory structure.
    for part in path.split(os.sep):
        if part.startswith(tuple(str(i).zfill(2) for i in range(100))):
            return part
    return "unknown"


# -----------------------------------------
# DISCOVER IMAGES (CONTROLLED + SAFE)
# -----------------------------------------

def discover_images(input_folder):
    images = []

    # I scan recursively because the raw CV dataset is nested across folders.
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            path = os.path.join(root, file_name)

            # I filter by extension so I only collect supported image file types.
            file_extension = os.path.splitext(path)[1].lower()
            if file_extension not in IMAGE_EXTENSIONS:
                continue

            # I check for the "images" folder name because that helps me avoid
            # unrelated files that may exist elsewhere in the dataset tree.
            if "images" not in path.split(os.sep):
                continue

            images.append(path)

    if not images:
        raise FileNotFoundError(f"No images found inside: {input_folder}")

    # I sort first so the starting order is deterministic before I shuffle.
    images.sort()

    # I shuffle to reduce any ordering bias from the raw folder structure.
    random.shuffle(images)

    # I cap the number of images so this preprocessing stage stays lightweight
    # enough for experimentation in an early project.
    return images[:MAX_IMAGES]


# -----------------------------------------
# MAIN PIPELINE
# -----------------------------------------

def process_dataset():
    # I discover the source images first because the rest of the pipeline
    # depends on having one controlled list of valid input files.
    image_paths = discover_images(INPUT_FOLDER)

    total_images = len(image_paths)
    print(f"[INFO] Found {total_images} valid images")

    # -----------------------------------------
    # TRUE RANDOM SPLIT (NO BIAS)
    # -----------------------------------------

    indices = list(range(total_images))
    # I shuffle indices here so train and test splits are not tied to the
    # original discovery order of the source images.
    random.shuffle(indices)

    train_cutoff = int(TRAIN_RATIO * total_images)
    train_indices = set(indices[:train_cutoff])

    # -----------------------------------------
    # CSV INITIALISATION
    # -----------------------------------------

    with open(LABELS_PATH, "w", newline="", encoding="utf-8") as csvfile:

        writer = csv.writer(csvfile)

        # I write a header row because the labels file is meant to be reused
        # later by dataset loaders and training scripts.
        header_row = [
            "image_path",
            "label",
            "split",
            "distortion_type",
            "doc_type",
            "severity",
        ]
        writer.writerow(header_row)

        processed_count = 0

        # -----------------------------------------
        # STREAMING PROCESS LOOP
        # -----------------------------------------

        for image_index, file_path in enumerate(image_paths):

            image = load_image_safe(file_path)
            if image is None:
                continue

            # -----------------------------------------
            # SPLIT ASSIGNMENT
            # -----------------------------------------

            # I choose train or test here so every saved image and label row
            # stays tied to one consistent dataset split.
            if image_index in train_indices:
                split = "train"
                orig_folder = TRAIN_ORIG
                dist_folder = TRAIN_DIST
            else:
                split = "test"
                orig_folder = TEST_ORIG
                dist_folder = TEST_DIST

            doc_type = extract_doc_type(file_path)

            base_name = f"img_{image_index:05d}"

            orig_path = os.path.join(orig_folder, f"{base_name}_orig.jpg")
            dist_path = os.path.join(dist_folder, f"{base_name}_dist.jpg")

            # -----------------------------------------
            # SAVE ORIGINAL
            # -----------------------------------------

            # I save the original image too because the model needs examples of
            # both genuine-looking documents and distorted ones.
            cv2.imwrite(str(orig_path), image)

            if not os.path.exists(orig_path):
                print(f"[ERROR] Failed saving original: {orig_path}")
                continue

            original_row = [
                str(orig_path),
                0,
                split,
                "none",
                doc_type,
                0.0,
            ]
            writer.writerow(original_row)

            # -----------------------------------------
            # APPLY FRAUD DISTORTION
            # -----------------------------------------

            # I choose one distortion at random so the synthetic fraud samples
            # are more varied than if I always applied the same transformation.
            distortion_name = random.choice(list(DISTORTION_FUNCTIONS.keys()))
            distortion_fn = DISTORTION_FUNCTIONS[distortion_name]

            distorted = distortion_fn(image.copy())

            cv2.imwrite(str(dist_path), distorted)

            if not os.path.exists(dist_path):
                print(f"[ERROR] Failed saving distorted: {dist_path}")
                continue

            severity = DISTORTION_SEVERITY[distortion_name]

            distorted_row = [
                str(dist_path),
                1,
                split,
                distortion_name,
                doc_type,
                severity,
            ]
            writer.writerow(distorted_row)

            processed_count += 1

    print(f"[SUCCESS] Processed {processed_count} source images")
    print(f"[SUCCESS] Labels saved to: {LABELS_PATH}")


# -----------------------------------------
# ENTRY POINT
# -----------------------------------------

if __name__ == "__main__":
    # I keep the entry point tiny because the main logic already lives in
    # process_dataset(), which is easier to reuse and test.
    process_dataset()
