import argparse
import csv
import random
from pathlib import Path

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def find_images(source_dir, max_images=None):
    # I discover images recursively because the source folder may contain many
    # nested directories of real document images.
    source_path = Path(source_dir)
    image_paths = []
    for path in source_path.rglob("*"):
        is_image_file = path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        if is_image_file:
            image_paths.append(path)
    image_paths.sort()
    if max_images is not None:
        image_paths = image_paths[:max_images]
    return image_paths


def assign_split(index, total, train_ratio, val_ratio):
    # I assign train, validation, and test splits by index so every generated
    # real/fake pair stays inside one consistent split.
    train_cutoff = int(total * train_ratio)
    val_cutoff = int(total * (train_ratio + val_ratio))
    if index < train_cutoff:
        return "train"
    if index < val_cutoff:
        return "val"
    return "test"


def add_noise(image, rng):
    # I add noise because fake or manipulated images often contain artefacts
    # that differ from clean originals.
    noise = rng.normal(0, 18, image.shape).astype(np.int16)
    image_as_int = image.astype(np.int16)
    noisy = np.clip(image_as_int + noise, 0, 255).astype(np.uint8)
    return noisy


def add_occlusion(image, rng):
    # I add occlusion because covering part of a document is a stronger fake-like
    # transformation than a tiny brightness or blur change.
    output = image.copy()
    height, width = output.shape[:2]
    occ_width = max(12, int(width * rng.uniform(0.12, 0.28)))
    occ_height = max(12, int(height * rng.uniform(0.12, 0.28)))
    x1 = int(rng.uniform(0, max(1, width - occ_width)))
    y1 = int(rng.uniform(0, max(1, height - occ_height)))
    color = tuple(int(v) for v in rng.integers(0, 255, size=3))
    cv2.rectangle(output, (x1, y1), (x1 + occ_width, y1 + occ_height), color, thickness=-1)
    return output


def warp_perspective(image, rng):
    # I warp perspective because document tampering often changes geometry,
    # alignment, or capture angle in a suspicious way.
    height, width = image.shape[:2]
    dx = width * 0.08
    dy = height * 0.08
    source = np.float32([[0, 0], [width - 1, 0], [0, height - 1], [width - 1, height - 1]])
    target = source + np.float32(
        [
            [rng.uniform(-dx, dx), rng.uniform(-dy, dy)],
            [rng.uniform(-dx, dx), rng.uniform(-dy, dy)],
            [rng.uniform(-dx, dx), rng.uniform(-dy, dy)],
            [rng.uniform(-dx, dx), rng.uniform(-dy, dy)],
        ]
    )
    matrix = cv2.getPerspectiveTransform(source, target)
    return cv2.warpPerspective(image, matrix, (width, height), borderMode=cv2.BORDER_REFLECT)


def apply_fake_transforms(image, seed):
    # I keep all fake transforms in one function so one input image can become
    # a varied synthetic fraud sample through several random manipulations.
    rng = np.random.default_rng(seed)
    output = image.copy()

    should_warp = rng.random() < 0.8
    if should_warp:
        output = warp_perspective(output, rng)
    should_add_noise = rng.random() < 0.8
    if should_add_noise:
        output = add_noise(output, rng)
    should_blur = rng.random() < 0.7
    if should_blur:
        output = cv2.GaussianBlur(output, (5, 5), sigmaX=1.2)
    should_adjust_brightness = rng.random() < 0.7
    if should_adjust_brightness:
        alpha = float(rng.uniform(0.65, 1.35))
        beta = int(rng.uniform(-30, 30))
        output = cv2.convertScaleAbs(output, alpha=alpha, beta=beta)
    should_occlude = rng.random() < 0.6
    if should_occlude:
        output = add_occlusion(output, rng)
    should_rotate = rng.random() < 0.4
    if should_rotate:
        output = cv2.rotate(output, cv2.ROTATE_180)

    return output


def build_binary_dataset(source_dir, output_dir, csv_path, max_images, train_ratio, val_ratio, seed, image_size):
    # I build the binary dataset here because the whole purpose of this script
    # is to create paired real and synthetic-fake training examples.
    images = find_images(source_dir, max_images=max_images)
    if not images:
        raise FileNotFoundError(f"No images found under: {source_dir}")

    # I shuffle with a seeded RNG so the dataset order is reproducible.
    rng = random.Random(seed)
    rng.shuffle(images)

    output_dir = Path(output_dir)
    real_dir = output_dir / "real"
    fake_dir = output_dir / "fake"
    real_dir.mkdir(parents=True, exist_ok=True)
    fake_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for index, source_path in enumerate(images):
        split = assign_split(index, len(images), train_ratio, val_ratio)
        # I load each source image because I need the real image first before
        # I can derive a fake version from it.
        image = cv2.imread(str(source_path))
        if image is None:
            continue
        image = cv2.resize(image, (image_size, image_size))

        rel_name = f"{index:05d}_{source_path.stem}.jpg"
        real_output = real_dir / rel_name
        fake_output = fake_dir / rel_name

        # I save both the real and fake outputs because the final dataset is
        # meant to train a binary classifier.
        cv2.imwrite(str(real_output), image)
        fake_image = apply_fake_transforms(image, seed + index)
        cv2.imwrite(str(fake_output), fake_image)

        real_row = {"image_path": str(real_output.resolve()), "label": 0, "split": split}
        fake_row = {"image_path": str(fake_output.resolve()), "label": 1, "split": split}
        rows.append(real_row)
        rows.append(fake_row)

    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["image_path", "label", "split"])
        writer.writeheader()
        writer.writerows(rows)

    return rows


def parse_args():
    # I use argparse so I can generate different binary datasets from the
    # command line without rewriting the script.
    parser = argparse.ArgumentParser(description="Generate a binary real/fake CV dataset from real document images.")
    parser.add_argument("source_dir", help="Source folder containing real images.")
    parser.add_argument("--output-dir", default="data/processed/cv/binary")
    parser.add_argument("--csv-path", default="data/processed/cv/binary_labels.csv")
    parser.add_argument("--max-images", type=int, default=3000)
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--image-size", type=int, default=224)
    return parser.parse_args()


def main():
    # I keep main small so the real dataset-building logic stays reusable.
    args = parse_args()
    rows = build_binary_dataset(
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        csv_path=args.csv_path,
        max_images=args.max_images,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
        image_size=args.image_size,
    )

    label_counts = {}
    split_counts = {}
    for row in rows:
        label_counts[row["label"]] = label_counts.get(row["label"], 0) + 1
        split_counts[row["split"]] = split_counts.get(row["split"], 0) + 1

    print(f"Saved binary dataset CSV to: {Path(args.csv_path).resolve()}")
    print(f"Rows written: {len(rows)}")
    print(f"Label counts: {label_counts}")
    print(f"Split counts: {split_counts}")


if __name__ == "__main__":
    main()
