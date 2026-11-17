
const form = document.getElementById("prediction-form");
const messageInput = document.getElementById("message");
const analyzeButton = document.getElementById("analyze-btn");
const charCount = document.getElementById("char-count");

const result = document.getElementById("result");
const resultTitle = document.getElementById("result-title");
const resultDescription = document.getElementById("result-description");
const probabilityBar = document.getElementById("probability-bar");
const probabilityText = document.getElementById("probability-text");
const errorBox = document.getElementById("error");

messageInput.addEventListener("input", () => {
    charCount.textContent = `${messageInput.value.length} / 5000`;
    result.classList.add("hidden");
    errorBox.classList.add("hidden");
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";

    result.classList.add("hidden");
    errorBox.classList.add("hidden");

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Prediction request failed."
            );
        }

        result.className = data.is_spam
            ? "result spam"
            : "result ham";

        resultTitle.textContent = data.is_spam
            ? "⚠️ Potential Spam Detected"
            : "✅ Message Classified as Not Spam";

        resultDescription.textContent = data.is_spam
            ? "The model classified this message as spam."
            : "The model classified this message as legitimate.";

        probabilityBar.style.width =
            `${data.spam_probability}%`;

        probabilityText.textContent =
            `Estimated spam probability: ${data.spam_probability}%`;

    } catch (error) {
        errorBox.textContent = error.message;
        errorBox.classList.remove("hidden");

    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze Message";
    }
});
