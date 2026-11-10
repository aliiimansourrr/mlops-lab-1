import mlflow
import mlflow.pyfunc

mlflow.set_tracking_uri("http://127.0.0.1:5000")

model_uri = "models:/food11@champion"

print("Loading model:", model_uri)

model = mlflow.pyfunc.load_model(model_uri)

print("SUCCESS: Food-11 model loaded!")
print("Model type:", type(model))
