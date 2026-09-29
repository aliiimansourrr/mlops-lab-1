from pathlib import Path
from PIL import Image
import shutil


# Root folders
RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")

IMAGE_SIZE = (128, 128)
MINI_LIMIT = 100


# Food-11 class names
CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


def prepare_output_folders():
    # Remove old processed folders if they already exist
    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)

    if MINI_DIR.exists():
        shutil.rmtree(MINI_DIR)

    # Create folders for every split and class
    for split in ["training", "evaluation", "validation"]:
        for class_name in CLASSES:
            (PROCESSED_DIR / split / class_name).mkdir(
                parents=True,
                exist_ok=True
            )

            (MINI_DIR / split / class_name).mkdir(
                parents=True,
                exist_ok=True
            )


def process_split(split):
    source_folder = RAW_DIR / split

    class_counts = {i: 0 for i in range(len(CLASSES))}

    for image_path in source_folder.iterdir():

        if not image_path.is_file():
            continue

        # Food-11 filenames start with the class number
        # Example: 0_123.jpg -> class 0 -> Bread
        class_id = int(image_path.stem.split("_")[0])

        class_name = CLASSES[class_id]

        output_path = (
            PROCESSED_DIR
            / split
            / class_name
            / image_path.name
        )

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image = image.resize(IMAGE_SIZE)
            image.save(output_path)

            # Add only the first 100 images of each class to mini
            if class_counts[class_id] < MINI_LIMIT:
                mini_path = (
                    MINI_DIR
                    / split
                    / class_name
                    / image_path.name
                )

                image.save(mini_path)

                class_counts[class_id] += 1


def main():
    prepare_output_folders()

    for split in ["training", "evaluation", "validation"]:
        print(f"Processing {split}...")
        process_split(split)

    print("Done.")


if __name__ == "__main__":
    main()