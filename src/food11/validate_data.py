
import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError

try:
    from src.food11.data import CLASSES
except ModuleNotFoundError as exc:
    if exc.name not in {"src", "src.food11"}:
        raise
    from data import CLASSES


SPLITS = ("training", "validation", "evaluation")
IMAGE_SIZE = (128, 128)


def validate_dataset(root: Path, min_per_class: int, tau: float) -> bool:
    results = {}
    counts = {}
    hashes = {}

    # 1. Check class folders.
    folders_ok = True

    for split in SPLITS:
        split_dir = root / split

        if not split_dir.is_dir():
            folders_ok = False
            continue

        actual = {
            path.name
            for path in split_dir.iterdir()
            if path.is_dir()
        }

        if actual != set(CLASSES):
            folders_ok = False

    results["Class folders"] = folders_ok

    # 2–4. Check image properties, class counts and duplicates.
    images_ok = True
    counts_ok = True
    duplicates_ok = True

    for split in SPLITS:
        counts[split] = Counter()

        for class_name in CLASSES:
            folder = root / split / class_name

            if not folder.is_dir():
                counts_ok = False
                continue

            files = [p for p in folder.iterdir() if p.is_file()]
            counts[split][class_name] = len(files)

            if len(files) < min_per_class:
                counts_ok = False

            for path in files:
                try:
                    with Image.open(path) as image:
                        image.load()

                        if (
                            image.mode != "RGB"
                            or image.size != IMAGE_SIZE
                        ):
                            images_ok = False

                except (OSError, ValueError, UnidentifiedImageError):
                    images_ok = False

                digest = hashlib.md5(
                    path.read_bytes(),
                    usedforsecurity=False,
                ).hexdigest()

                if digest in hashes and hashes[digest] != split:
                    duplicates_ok = False

                hashes.setdefault(digest, split)

    results["Image format and dimensions"] = images_ok
    results["Minimum images per class"] = counts_ok
    results["No duplicates across splits"] = duplicates_ok

    # 5. Compare training/validation class proportions.
    distribution_ok = True

    training_total = sum(counts["training"].values())
    validation_total = sum(counts["validation"].values())

    if training_total == 0 or validation_total == 0:
        distribution_ok = False
    else:
        for class_name in CLASSES:
            p_train = counts["training"][class_name] / training_total
            p_val = counts["validation"][class_name] / validation_total

            if abs(p_train - p_val) > tau:
                distribution_ok = False

    results["Class distribution"] = distribution_ok

    # Print one result per check.
    print(f"Dataset: {root}")

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {name}")

    overall = all(results.values())
    print("OVERALL:", "PASS" if overall else "FAIL")

    return overall


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("dataset", type=Path)
    parser.add_argument(
        "--min-per-class",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--tau",
        type=float,
        default=0.05,
    )

    args = parser.parse_args()

    passed = validate_dataset(
        args.dataset,
        args.min_per_class,
        args.tau,
    )

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
