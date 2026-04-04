import argparse
import csv
import random
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
# I keep positive and negative folder-name clues here because this script can
# infer labels from directory names when a dataset is organized that way.
POSITIVE_FOLDER_NAMES = {"1", "true", "yes", "positive", "fraud", "fake", "forged", "tampered"}
NEGATIVE_FOLDER_NAMES = {"0", "false", "no", "negative", "safe", "real", "genuine", "authentic"}


def find_images(source_dir):
    # I collect images recursively because CV datasets are often nested across
    # multiple folders rather than stored in one flat directory.
    source_path = Path(source_dir)
    image_paths = []
    for path in source_path.rglob("*"):
        is_image_file = path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        if is_image_file:
            image_paths.append(path)
    image_paths.sort()
    return image_paths


def infer_label_from_parent(image_path):
    # I infer labels from the parent folder name because some image datasets
    # encode class information directly in the directory structure.
    parent_name = image_path.parent.name.strip().lower()

    if parent_name in POSITIVE_FOLDER_NAMES:
        return 1
    if parent_name in NEGATIVE_FOLDER_NAMES:
        return 0

    raise ValueError(
        f"Could not infer label from parent folder '{image_path.parent.name}'. "
        "Use --label-mode constant or place images inside folders like real/0 and fake/1."
    )


def assign_split(index, total, train_ratio, val_ratio):
    # I assign split by index so the CSV can include train, val, and test rows
    # without needing a separate split file.
    if total == 0:
        return "train"

    train_cutoff = int(total * train_ratio)
    val_cutoff = int(total * (train_ratio + val_ratio))

    if index < train_cutoff:
        return "train"
    if index < val_cutoff:
        return "val"
    return "test"


def build_rows(images, label_mode, constant_label, train_ratio, val_ratio, shuffle, seed):
    # I build rows in one helper so discovery, labeling, and splitting stay
    # grouped together before I write the final CSV.
    images = list(images)
    if shuffle:
        random.Random(seed).shuffle(images)

    rows = []
    for index, image_path in enumerate(images):
        if label_mode == "constant":
            label = constant_label
        else:
            label = infer_label_from_parent(image_path)
        split = assign_split(index, len(images), train_ratio, val_ratio)
        row = {
            "image_path": str(image_path.resolve()),
            "label": int(label),
            "split": split,
        }
        rows.append(row)

    return rows


def write_csv(rows, output_path):
    # I write the CSV in one place because later training code depends on a
    # simple, predictable labels file with these exact columns.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["image_path", "label", "split"])
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    # I use argparse here so I can build CV dataset indexes from different
    # image folders without editing the script by hand each time.
    parser = argparse.ArgumentParser(description="Build a CSV index for CV training data.")
    parser.add_argument("source_dir", help="Folder containing images or class subfolders.")
    parser.add_argument(
        "--output",
        default="data/processed/cv/labels.csv",
        help="Where to write the generated CSV.",
    )
    parser.add_argument(
        "--label-mode",
        choices=["constant", "parent_name"],
        default="constant",
        help="How labels should be assigned.",
    )
    parser.add_argument(
        "--label",
        type=int,
        default=1,
        help="Label value to use when --label-mode constant is selected.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--no-shuffle",
        action="store_true",
        help="Keep the discovered file order instead of shuffling before splitting.",
    )
    return parser.parse_args()


def main():
    # I keep main small so the real work stays in reusable helpers.
    args = parse_args()

    if args.train_ratio < 0 or args.val_ratio < 0 or args.train_ratio + args.val_ratio > 1:
        raise ValueError("train_ratio and val_ratio must be non-negative and sum to 1 or less.")

    images = find_images(args.source_dir)
    if not images:
        raise FileNotFoundError(f"No images found under: {args.source_dir}")

    rows = build_rows(
        images=images,
        label_mode=args.label_mode,
        constant_label=args.label,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        shuffle=not args.no_shuffle,
        seed=args.seed,
    )
    write_csv(rows, args.output)

    label_counts = {}
    for row in rows:
        label_counts[row["label"]] = label_counts.get(row["label"], 0) + 1

    split_counts = {}
    for row in rows:
        split_counts[row["split"]] = split_counts.get(row["split"], 0) + 1

    print(f"Saved dataset CSV to: {Path(args.output).resolve()}")
    print(f"Images indexed: {len(rows)}")
    print(f"Label counts: {label_counts}")
    print(f"Split counts: {split_counts}")


if __name__ == "__main__":
    main()
