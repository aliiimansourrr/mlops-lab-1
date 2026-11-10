import mlflow
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copytree

mlflow.set_tracking_uri("http://127.0.0.1:5000")

source = Path(
    "mlruns/1/models/"
    "m-5eec62e9e4644b0695628592b2d080a8/"
    "artifacts"
)

assert (source / "MLmodel").is_file(), "MLmodel file missing"
assert (source / "data" / "model.pth").is_file(), "Weights missing"

with TemporaryDirectory() as temp:
    destination = Path(temp) / "food11_model"
    copytree(source, destination)

    # Remove registry metadata from the old server's copy.
    old_metadata = destination / "registered_model_meta"
    if old_metadata.exists():
        old_metadata.unlink()

    with mlflow.start_run(run_name="lab4-food11-migration") as run:
        mlflow.log_artifacts(str(destination), artifact_path="food11_model")

        model_uri = f"runs:/{run.info.run_id}/food11_model"
        print("Migration run ID:", run.info.run_id)
        print("New model artifact URI:", model_uri)

        artifacts = mlflow.artifacts.list_artifacts(
            run_id=run.info.run_id,
            artifact_path="food11_model"
        )
        print("Uploaded files:", [item.path for item in artifacts])
