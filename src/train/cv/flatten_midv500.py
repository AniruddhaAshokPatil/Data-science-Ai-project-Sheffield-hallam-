"""I flatten the MIDV500 image folders into one simpler training folder."""

import os
import shutil

# I define the raw dataset folder here because this script flattens a deeply
# nested MIDV500 structure into one simpler image folder.
SOURCE_DIR = "data/raw/cv/midv500"

# I keep a separate destination because I want a simpler training-friendly copy
# without changing the original raw dataset.
DEST_DIR = "data/raw/cv/midv500/images"

# I cap the number of images so this helper can create a manageable subset for
# experiments instead of trying to copy everything at once.
MAX_IMAGES = 3000

def flatten_images():
    # I create the destination folder first because the copy step needs a
    # place to put the flattened image files.
    os.makedirs(DEST_DIR, exist_ok=True)

    image_counter = 0

    # I walk through every folder under the raw dataset so I can find images
    # even when they are deeply nested.
    for root, _, files in os.walk(SOURCE_DIR):
        for file_name in files:
            is_image_file = file_name.lower().endswith((".jpg", ".jpeg", ".png"))
            if not is_image_file:
                continue

            if image_counter >= MAX_IMAGES:
                break

            source_path = os.path.join(root, file_name)
            new_filename = f"img_{image_counter:05d}.jpg"
            destination_path = os.path.join(DEST_DIR, new_filename)

            # I copy the file instead of moving it because I want to keep the
            # original dataset untouched.
            shutil.copy(source_path, destination_path)
            image_counter += 1

        if image_counter >= MAX_IMAGES:
            break

    return image_counter


def main():
    # I keep the terminal entry point small so the script is easier to explain.
    image_counter = flatten_images()
    print(f"Done. Total images copied: {image_counter}")


if __name__ == "__main__":
    main()
