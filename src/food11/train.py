import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import resnet18, ResNet18_Weights


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        choices=["processed", "mini"],
        default="mini"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32
    )

    return parser.parse_args()


def create_dataloaders(dataset_name, batch_size):

    if dataset_name == "mini":
        data_root = Path("data/food11_processed_mini")
    else:
        data_root = Path("data/food11_processed")

    transform = transforms.Compose([
        transforms.ToTensor(),

        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    train_dataset = datasets.ImageFolder(
        data_root / "training",
        transform=transform
    )

    val_dataset = datasets.ImageFolder(
        data_root / "validation",
        transform=transform
    )

    test_dataset = datasets.ImageFolder(
        data_root / "evaluation",
        transform=transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, val_loader, test_loader


def create_model():

    weights = ResNet18_Weights.DEFAULT

    model = resnet18(weights=weights)

    # ResNet18 normally outputs 1000 ImageNet classes.
    # Food-11 has only 11 classes.
    model.fc = nn.Linear(
        model.fc.in_features,
        11
    )

    return model


def train_one_epoch(model, loader, criterion, optimizer, device):

    model.train()

    total_loss = 0.0

    for images, labels in loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(loader)


def evaluate(model, loader, criterion, device):

    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(outputs, labels)

            total_loss += loss.item()

            predictions = outputs.argmax(dim=1)

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

    average_loss = total_loss / len(loader)

    accuracy = correct / total

    return average_loss, accuracy


def main():

    args = parse_args()

    mlflow.set_tracking_uri(
        "http://127.0.0.1:5000"
    )

    mlflow.set_experiment("food11")

    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Using device: {device}")

    train_loader, val_loader, test_loader = create_dataloaders(
        args.dataset,
        args.batch_size
    )

    model = create_model()

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr
    )

    with mlflow.start_run():

        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
            "model": "resnet18"
        })

        for epoch in range(args.epochs):

            train_loss = train_one_epoch(
                model,
                train_loader,
                criterion,
                optimizer,
                device
            )

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} "
                f"- train_loss: {train_loss:.4f} "
                f"- val_loss: {val_loss:.4f} "
                f"- val_accuracy: {val_accuracy:.4f}"
            )

            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch
            )

        test_loss, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device
        )

        print(
            f"Final test accuracy: "
            f"{test_accuracy:.4f}"
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy
        )

        input_example = torch.randn(1, 3, 128, 128)

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy
        )

        mlflow.pytorch.log_model(
            model,
            name="model",
            serialization_format="pickle"
        )


if __name__ == "__main__":
    main()