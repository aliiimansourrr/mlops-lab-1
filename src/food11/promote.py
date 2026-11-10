
import argparse
import math
import os

from mlflow.tracking import MlflowClient

MODEL_NAME = "food11"
METRIC_NAME = "test_accuracy"


def get_accuracy(client, model_version):
    """Read the test accuracy of a registered model version."""
    if not model_version.run_id:
        raise ValueError(
            f"Model version {model_version.version} has no run ID"
        )

    run = client.get_run(model_version.run_id)
    accuracy = run.data.metrics.get(METRIC_NAME)

    if accuracy is None:
        raise ValueError(
            f"Run {model_version.run_id} is missing {METRIC_NAME}"
        )

    accuracy = float(accuracy)

    if not 0.0 <= accuracy <= 1.0:
        raise ValueError("Accuracy must be between 0 and 1")

    return accuracy


def main():
    parser = argparse.ArgumentParser(
        description="Promote a Food-11 model using an accuracy gate"
    )

    parser.add_argument(
        "--version",
        type=int,
        required=True,
        help="Candidate model version",
    )

    parser.add_argument(
        "--n",
        type=int,
        default=1096,
        help="Number of evaluation images",
    )

    args = parser.parse_args()

    if args.n <= 0:
        parser.error("--n must be greater than zero")

    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000",
    )

    client = MlflowClient(tracking_uri=tracking_uri)

    champion = client.get_model_version_by_alias(
        MODEL_NAME,
        "champion",
    )

    candidate = client.get_model_version(
        MODEL_NAME,
        str(args.version),
    )

    if candidate.version == champion.version:
        raise ValueError(
            "Candidate is already champion; select another version"
        )

    champion_acc = get_accuracy(client, champion)
    candidate_acc = get_accuracy(client, candidate)

    se = math.sqrt(
        champion_acc * (1 - champion_acc) / args.n
    )

    threshold = champion_acc + 2 * se

    print("Current champion:", champion.version)
    print("Candidate version:", candidate.version)
    print(f"Champion accuracy: {champion_acc:.6f}")
    print(f"Candidate accuracy: {candidate_acc:.6f}")
    print(f"Standard error: {se:.6f}")
    print(f"Promotion threshold: {threshold:.6f}")

    if candidate_acc >= threshold:
        decision = "PROMOTED"

        client.set_registered_model_alias(
            MODEL_NAME,
            "champion",
            candidate.version,
        )
    else:
        decision = "REJECTED"

        client.set_registered_model_alias(
            MODEL_NAME,
            "challenger",
            candidate.version,
        )

    # Save the quality-gate decision on the model version.
    tags = {
        "promotion_decision": decision,
        "candidate_accuracy": str(candidate_acc),
        "champion_accuracy": str(champion_acc),
        "promotion_threshold": str(threshold),
        "standard_error": str(se),
        "evaluation_images": str(args.n),
    }

    for key, value in tags.items():
        client.set_model_version_tag(
            MODEL_NAME,
            candidate.version,
            key,
            value,
        )

    print("Decision:", decision)

    current = client.get_model_version_by_alias(
        MODEL_NAME,
        "champion",
    )

    print("Champion after decision:", current.version)


if __name__ == "__main__":
    main()
