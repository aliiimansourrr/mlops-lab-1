import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

client = MlflowClient()

# Retrieve the current champion model.
current = client.get_model_version_by_alias("food11", "champion")

print("Original version:", current.version)
print("Original source:", current.source)

# Register the same artifacts as a new model version.
new_version = client.create_model_version(
    name="food11",
    source=current.source,
    run_id=current.run_id
)

print("New model version:", new_version.version)
print("New model source:", new_version.source)

# Check that champion still points to the original version.
champion = client.get_model_version_by_alias("food11", "champion")
print("Current champion:", champion.version)
