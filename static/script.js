let currentVariant = "";

function setExample(text) {
    document.getElementById("variantInput").value = text;
}

async function analyzeVariant() {
    const variant = document.getElementById("variantInput").value.trim();
    currentVariant = variant;

    const analyzeBtn = document.querySelector(".analyze-btn");
    analyzeBtn.textContent = "Analyzing...";
    analyzeBtn.disabled = true;

    const response = await fetch("/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ variant: variant })
    });

    const data = await response.json();
    const result = data.result;
    const explanation = data.explanation;

    analyzeBtn.textContent = "Analyze Variant";
    analyzeBtn.disabled = false;

    const resultCard = document.getElementById("resultCard");
    const explanationCard = document.getElementById("explanationCard");
    const feedbackCard = document.getElementById("feedbackCard");
    const recommendationBox = document.getElementById("recommendationBox");

    resultCard.classList.remove("hidden");
    explanationCard.classList.remove("hidden");

    document.getElementById("prediction").textContent =
        result.Prediction ?? "-";
    document.getElementById("probability").textContent =
        result.Probability_Pathogenic ?? "-";
    document.getElementById("confidence").textContent =
        result.Confidence ?? "-";
    document.getElementById("difficulty").textContent =
        result.Difficulty_Score ?? "-";

    recommendationBox.textContent = result.Recommendation || "";
    recommendationBox.className = "recommendation";

    if (result.Prediction === "Pathogenic") {
        recommendationBox.classList.add("pathogenic");
    } else if (result.Prediction === "Benign") {
        recommendationBox.classList.add("benign");
    } else if (result.Prediction === "Uncertain") {
        recommendationBox.classList.add("uncertain");
    } else {
        recommendationBox.classList.add("invalid");
    }

    const confidenceFill = document.getElementById("confidenceFill");
    confidenceFill.style.width = ((result.Confidence || 0) * 100) + "%";

    const explanationList = document.getElementById("explanationList");
    explanationList.innerHTML = "";

    if (explanation.length === 0) {
        explanationList.innerHTML = "<li>No explanation available.</li>";
    } else {
        explanation.forEach(item => {
            const li = document.createElement("li");
            li.textContent = `${item.feature}: contribution ${item.contribution}`;
            explanationList.appendChild(li);
        });
    }

    if (result.Prediction === "Uncertain") {
        feedbackCard.classList.remove("hidden");
    } else {
        feedbackCard.classList.add("hidden");
    }

    document.getElementById("bufferCount").textContent = data.buffer_size;
}

async function submitFeedback(label) {
    const response = await fetch("/feedback", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            variant: currentVariant,
            label: label
        })
    });

    const data = await response.json();
    document.getElementById("statusMessage").textContent = data.message;
    document.getElementById("bufferCount").textContent = data.buffer_size;
}

async function retrainModel() {
    const response = await fetch("/retrain", {
        method: "POST"
    });

    const data = await response.json();
    document.getElementById("statusMessage").textContent = data.message;
    document.getElementById("bufferCount").textContent = data.buffer_size;
}

async function loadStatus() {
    const response = await fetch("/status");
    const data = await response.json();
    document.getElementById("bufferCount").textContent = data.buffer_size;
}

window.onload = loadStatus;