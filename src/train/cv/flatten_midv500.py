# ============================================
# MIDV-500 IMAGE FLATTENER (STEP-BY-STEP SAFE)
# ============================================

# I am importing libraries to work with file system
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

# I am creating destination folder if it does not exist
os.makedirs(DEST_DIR, exist_ok=True)

# I use a counter so the flattened images get clean, consistent file names.
image_counter = 0

# I am walking through all folders in dataset
for root, dirs, files in os.walk(SOURCE_DIR):

    # I am checking every file inside each folder
    for file in files:

        # I am selecting only image files
        is_image_file = file.lower().endswith((".jpg", ".jpeg", ".png"))
        if is_image_file:

            # I stop if I reach max limit
            if image_counter >= MAX_IMAGES:
                break

            # I am building full file path
            source_path = os.path.join(root, file)

            # I create a new sequential filename so later scripts do not depend
            # on the original nested folder names.
            new_filename = f"img_{image_counter:05d}.jpg"
            dest_path = os.path.join(DEST_DIR, new_filename)

            # I am copying image into flat folder
            shutil.copy(source_path, dest_path)

            # I increment counter
            image_counter += 1

    # I break outer loop as well when limit reached
    if image_counter >= MAX_IMAGES:
        break

# I print total images copied
print(f"Done. Total images copied: {image_counter}")
