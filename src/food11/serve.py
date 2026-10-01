import os
from io import BytesIO

import mlflow
import mlflow.pyfunc
import numpy as np
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from torchvision import transforms


MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_URI = "models:/food11@champion"

model = mlflow.pyfunc.load_model(MODEL_URI)

app = FastAPI()


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


transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()

    image = Image.open(BytesIO(contents)).convert("RGB")

    tensor = transform(image).unsqueeze(0)

    predictions = model.predict(tensor.numpy())

    predictions = np.asarray(predictions)

    if predictions.ndim == 2:
        scores = predictions[0]
    else:
        scores = predictions

    exp_scores = np.exp(scores - np.max(scores))
    probabilities = exp_scores / exp_scores.sum()

    class_index = int(np.argmax(probabilities))
    confidence = float(probabilities[class_index])

    return {
        "category": CLASSES[class_index],
        "confidence": confidence,
    }