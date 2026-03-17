from flask import Flask, render_template, request, jsonify
from scipy.sparse import vstack
from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np
from scipy import sparse

from src.loader import load_artifacts
from src.predictor import predict_variant, explain_variant

app = Flask(__name__)

model, vectorizer = load_artifacts()
X_train_vec = sparse.load_npz("X_train_vec.npz")
y_train = np.load("y_train.npy")

# keep original training data available for retraining
# load these from files if you saved them, or regenerate if needed
X_train_vec = None
y_train = None

# in-memory learning buffer
learning_buffer = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    variant_text = data.get("variant", "")

    result = predict_variant(variant_text, model, vectorizer)
    explanation = explain_variant(variant_text, model, vectorizer)

    return jsonify({
        "result": result,
        "explanation": explanation,
        "buffer_size": len(learning_buffer)
    })


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    variant_text = data.get("variant", "").strip()
    label = data.get("label", None)

    if variant_text and label in [0, 1]:
        learning_buffer.append((variant_text, int(label)))
        return jsonify({
            "success": True,
            "message": "Expert feedback stored successfully.",
            "buffer_size": len(learning_buffer)
        })

    return jsonify({
        "success": False,
        "message": "Invalid feedback payload.",
        "buffer_size": len(learning_buffer)
    }), 400


@app.route("/retrain", methods=["POST"])
def retrain():
    global model

    if len(learning_buffer) == 0:
        return jsonify({
            "success": False,
            "message": "No new feedback available for retraining.",
            "buffer_size": 0
        })

    # IMPORTANT:
    # You should ideally save/load X_train_vec and y_train from disk.
    # For now this assumes they exist as .npz/.npy or are recreated elsewhere.
    if X_train_vec is None or y_train is None:
        return jsonify({
            "success": False,
            "message": "Training data not loaded in backend. Save and load X_train_vec / y_train for retraining.",
            "buffer_size": len(learning_buffer)
        }), 500

    new_texts = [x[0] for x in learning_buffer]
    new_labels = [x[1] for x in learning_buffer]

    X_new = vectorizer.transform(new_texts)
    X_combined = vstack([X_train_vec, X_new])
    y_combined = np.concatenate([np.array(y_train), np.array(new_labels)])

    model = LogisticRegression(max_iter=100000)
    model.fit(X_combined, y_combined)

    # save updated model
    joblib.dump(model, "model.pkl")

    learned_count = len(learning_buffer)
    learning_buffer.clear()

    return jsonify({
        "success": True,
        "message": f"Model retrained successfully using {learned_count} new examples.",
        "buffer_size": 0
    })


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "buffer_size": len(learning_buffer)
    })


if __name__ == "__main__":
    app.run(debug=True)