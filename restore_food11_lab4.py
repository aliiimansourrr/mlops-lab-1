import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

model_uri = "runs:/21b6204f61914c499999121a79c24785/food11_model"

registered = mlflow.register_model(
    model_uri=model_uri,
    name="food11"
)

client = MlflowClient()

client.set_registered_model_alias(
    name="food11",
    alias="champion",
    version=registered.version
)

champion = client.get_model_version_by_alias(
    "food11",
    "champion"
)

print("Registered model:", registered.name)
print("Registered version:", registered.version)
print("Champion version:", champion.version)
print("Artifact source:", champion.source)
