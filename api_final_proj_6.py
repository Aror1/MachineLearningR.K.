from flask import Flask, request
from flask_restful import Resource, Api
import pandas as pd
import joblib
import os
import numpy as np
from flask_cors import CORS
import logging
import joblib

app = Flask(__name__)
api = Api(app)
CORS(app, resources={r"/*": {"origins": "*"}}) 

logging.basicConfig(level=logging.DEBUG)

data_path = os.path.join(os.path.dirname(__file__), "output_tokenized.csv")



df = pd.read_csv(data_path)
cluster_names = df[['text_tokenize', 'topic']].drop_duplicates().set_index('text_tokenize')['topic'].to_dict()

def load_model(model_path: str):
    try:
        return joblib.load(model_path)
    except Exception:
        return None

def safe_predict(model, vectorizer, text: str):
    try:
        vectorized = vectorizer.transform([text])
        prediction = model.predict(vectorized)[0]
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(vectorized)[0]
            confidence = np.max(proba)
            probabilities = {f"Cluster {i}": float(p) for i, p in enumerate(proba)}
        else:
            confidence = 0.7
            probabilities = {f"Cluster {prediction}": 1.0}
        return {
            "cluster": int(prediction),
            "confidence": float(confidence),
            "probabilities": probabilities,
            "error": None
        }
    except Exception as e:
        return {
            "cluster": -1,
            "confidence": 0.0,
            "probabilities": {},
            "error": str(e)
        }

models_dir = '/Users/aror/Documents/proj/ml/models'
vectorizer = load_model(os.path.join(models_dir, "vectorizer.joblib"))

models = {
    "sgd_classifier_model": load_model(os.path.join(models_dir, "sgd_classifier_model.joblib")),
    "linearsvc_classifier_model": load_model(os.path.join(models_dir, "linearsvc_classifier_model.joblib")),
    "LogisticRegression_model": load_model(os.path.join(models_dir, "LogisticRegression_classifier_model.joblib"))
}

models = {k: v for k, v in models.items() if v is not None}

class PredictResource(Resource):
    def post(self):
        data = request.get_json()
        description = data.get("description")

        if not description or not isinstance(description, str):
            return {"error": "Текст не может быть пустым"}, 400

        if not vectorizer:
            return {"error": "Векторизатор не загружен"}, 500

        if not models:
            return {"error": "Нет доступных моделей для предсказания"}, 500

        processed_text = description.lower().strip()
        predictions = []

        for model_name, model in models.items():
            result = safe_predict(model, vectorizer, processed_text)
            if result["error"]:
                continue
            predictions.append({
                **result,
                "model_name": model_name
            })

        if not predictions:
            return {
                "cluster": -1,
                "cluster_name": "Unknown",
                "description": description,
                "model_used": "none",
                "error": "All models failed to predict",
                "warning": "No working models available"
            }, 500

        best_prediction = max(predictions, key=lambda x: x["confidence"])

        response = {
            "cluster": best_prediction["cluster"],
            "cluster_name": cluster_names.get(best_prediction["topic"], "Unknown"),
            "description": description,
            "model_used": best_prediction["model_name"],
            "confidence": best_prediction["confidence"],
            "probabilities": best_prediction["probabilities"]
        }

        if best_prediction["confidence"] < 0.5:
            response["warning"] = "Low confidence prediction"

        return response


class HealthResource(Resource):
    def get(self):
        return {
            "status": "OK" if models else "ERROR",
            "models_loaded": list(models.keys()),
            "vectorizer_loaded": vectorizer is not None
        }


api.add_resource(PredictResource, "/pred")
api.add_resource(HealthResource, "/health")

if __name__ == "__main__":
    app.run(port=6006, debug=True)