from src.validator import looks_like_variant
import numpy as np

LOW_CONFIDENCE_THRESHOLD = 0.4


def predict_variant(input_text: str, model, vectorizer):
    input_text = input_text.strip()

    # if not looks_like_variant(input_text):
    #     return {
    #         "Prediction": "Invalid input",
    #         "Probability_Pathogenic": None,
    #         "Confidence": None,
    #         "Difficulty_Score": None,
    #         "Recommendation": "Enter a variant like BRCA1 c.5266dupC"
    #     }

    vec = vectorizer.transform([input_text])
    prob = float(model.predict_proba(vec)[0][1])
    label = 1 if prob >= 0.5 else 0
    confidence = abs(prob - 0.5) * 2
    difficulty = 1 - confidence

    if confidence < LOW_CONFIDENCE_THRESHOLD:
        decision = "Uncertain"
        recommendation = "Recommend expert review"
    else:
        decision = "Pathogenic" if label == 1 else "Benign"
        recommendation = "Model is confident enough to classify this variant"

    return {
        "Prediction": decision,
        "Probability_Pathogenic": round(prob, 4),
        "Confidence": round(confidence, 4),
        "Difficulty_Score": round(difficulty, 4),
        "Recommendation": recommendation
    }


def explain_variant(input_text: str, model, vectorizer, top_k=8):
    """
    Lightweight explanation for Logistic Regression + TF-IDF.
    Shows the most influential tokens present in the input.
    """
    input_text = input_text.strip()

    if not looks_like_variant(input_text):
        return []

    vec = vectorizer.transform([input_text])
    feature_names = vectorizer.get_feature_names_out()

    # works for logistic regression
    coef = model.coef_[0]

    present_indices = vec.nonzero()[1]
    explanations = []

    for idx in present_indices:
        contribution = float(vec[0, idx] * coef[idx])
        explanations.append({
            "feature": feature_names[idx],
            "contribution": round(contribution, 4)
        })

    explanations.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    return explanations[:top_k]