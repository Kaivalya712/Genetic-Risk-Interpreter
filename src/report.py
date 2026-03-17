def format_report(result: dict) -> str:
    if result["Prediction"] == "Invalid input":
        return result["Recommendation"]

    return f"""
Prediction: {result['Prediction']}
Pathogenic Probability: {result['Probability_Pathogenic']}
Confidence: {result['Confidence']}
Difficulty Score: {result['Difficulty_Score']}
Recommendation: {result['Recommendation']}
""".strip()