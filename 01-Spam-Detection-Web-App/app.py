
from pathlib import Path

import joblib
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "spam_pipeline.joblib"

app = Flask(__name__)

# Load only model files you created or trust.
model = None


def get_model():
    global model

    if model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Trained model not found. Run train_model.py first."
            )
        model = joblib.load(MODEL_PATH)

    return model


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/predict")
def predict():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send a JSON object."
        }), 400

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "error": "Please enter a valid message."
        }), 400

    if len(message) > 5000:
        return jsonify({
            "error": "Message is too long (maximum 5000 characters)."
        }), 400

    classifier = get_model()
    text = message.strip()

    prediction = int(classifier.predict([text])[0])
    probabilities = classifier.predict_proba([text])[0]

    classes = list(classifier.classes_)
    spam_index = classes.index(1)

    spam_probability = float(probabilities[spam_index])

    return jsonify({
        "prediction": "Spam" if prediction == 1 else "Not Spam",
        "is_spam": bool(prediction),
        "spam_probability": round(spam_probability * 100, 2),
        "confidence": round(
            max(spam_probability, 1 - spam_probability) * 100,
            2,
        ),
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
