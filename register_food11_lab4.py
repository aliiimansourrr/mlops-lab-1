import mlflow
from mlflow.tracking import MlflowClient

mlflow.set_tracking_uri("http://127.0.0.1:5000")

model_uri = "runs:/c46be5dbb1f642869bf1f1ad92a55b65/food11_model"

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

print("Registered model:", registered.name)
print("Model version:", registered.version)
print("Alias:", "champion")
print("Source:", registered.source)
