# SpamShield AI — End-to-End Spam Detection Web App

An end-to-end machine learning web application that classifies text messages as spam or legitimate using TF-IDF, Multinomial Naive Bayes, and Flask.

## Link

https://spamshield-ai-zir7.onrender.com/

## Features

- Interactive, responsive web interface
- Machine learning spam classification
- Estimated spam probability
- JSON prediction API
- Input validation
- Model evaluation and saved metrics
- Automated API tests

## Technologies

Python, Pandas, Scikit-learn, Flask, HTML, CSS, JavaScript, Joblib, Pytest.

## Dataset

**SMS Spam Collection — UCI Machine Learning Repository**

https://archive.ics.uci.edu/dataset/228/sms+spam+collection

The dataset contains 5,574 labeled SMS messages. The source file is `SMSSpamCollection`, a tab-separated text file without a header.

Download the official dataset, place the source file in `data/`, and convert it to a CSV with two columns:

- `label`: `ham` or `spam`
- `message`: SMS text

The dataset is excluded from Git to keep the repository lightweight. See the original source for its attribution and license.

## Project Structure

```text
01-Spam-Detection-Web-App/
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── data/
│   └── spam.csv
├── models/
│   ├── spam_pipeline.joblib
│   └── metrics.json
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── tests/
    └── test_app.py
```

## Installation

From the `Advanced-AI-ML-Projects` repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\01-Spam-Detection-Web-App\requirements.txt
```

## Train the Model

After preparing `data/spam.csv`:

```powershell
python .\01-Spam-Detection-Web-App\train_model.py
```

The script trains the TF-IDF + Naive Bayes pipeline, evaluates it on a held-out test split, and saves the model and evaluation metrics.

## Run the Website

```powershell
python .\01-Spam-Detection-Web-App\app.py
```

Open `http://127.0.0.1:5000`.

## Run Automated Tests

```powershell
python -m pytest .\01-Spam-Detection-Web-App\tests -v
```

## API

`POST /api/predict`

Example request:

```json
{
  "message": "Congratulations! You won a free prize!"
}
```

Example response structure:

```json
{
  "prediction": "Spam",
  "is_spam": true,
  "spam_probability": 94.2,
  "confidence": 94.2
}
```

The values above are illustrative and will depend on the trained model.

## Limitations

- Trained on historical English SMS messages, not a modern email corpus.
- Predictions may be incorrect.
- Model probabilities are not guaranteed to be calibrated.
- The application does not automatically block or filter messages.
- The included Flask development server is for local testing, not production deployment.

## Future Improvements

- Deploy the application online
- Add a Docker configuration
- Add CI testing with GitHub Actions
- Evaluate on more recent spam datasets
- Add model monitoring and performance comparisons
- Improve probability calibration

## Learning Outcomes

- Building reproducible ML training pipelines
- Evaluating classification models
- Saving and loading trained models
- Serving predictions through a Flask API
- Connecting JavaScript to a Python backend
- Writing automated tests
- Preparing an ML application for deployment

## Status

Local implementation ready for training, testing, and deployment.
