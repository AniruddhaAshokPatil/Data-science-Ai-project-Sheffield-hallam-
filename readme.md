#  Multimodal Fraud Detection System AI

I built this project as a Streamlit-based fraud detection app that brings together NLP and computer vision so I can look at phishing emails, suspicious receipts, and fake identity documents in one place.

I use the local `data/` folder in this repo as the main working data area for the project, so the raw and processed files live under paths like `data/raw/` and `data/processed/`.

> **Academic Research Project — MSc AI & Data Science 2024, Sheffield Hallam University**



#  Dataset Links

The receipt and the email is available in the dataset folder.

https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset

https://www.kaggle.com/datasets/sebastiandixon/yolov8-fraud-detection

https://www.kaggle.com/datasets/kontheeboonmeeprakob/midv500


---

##  Screenshots

### Phishing Email Analysis
![Phishing Email Detection](image1.jpeg)

### Receipt Fraud Detection
![Receipt Fraud Detection](image2.jpeg)

### ID Card Fraud Detection
![ID Card Fraud Detection](image3.jpg)

---

## Detection Modules

| Module | Models | Dataset |
|--------|--------|---------|
| **Phishing Email (NLP)** | Multinomial Naive Bayes, Random Forest | Enron + Ling-Spam |
| **Receipt Fraud (CV)** | MobileNetV2, ResNet50 | SROIE via Roboflow (1,265 images) |
| **ID Card Fraud (CV)** | MobileNetV2 + ResNet50 + One-Class SVM | MIDV-2019 |

---

##  Project Structure

```
project/
│
├── App_Frontend.py                          # Main Streamlit application
├── requirements.txt                         # Python packages I need to run the app
├── scripts/validate_project.py              # Quick project health check
├── docs/                                    # Project notes and traceability
│
├── data/                                   # Main project data folder
│   ├── raw/
│   └── processed/
│
├── backend/saved_models/                   # NLP & ID card models
│   ├── mnb_model.pkl
│   ├── rf_model.pkl
│   ├── tfidf_vectorizer.pkl
│   ├── chi2_selector.pkl
│   ├── ocsvm.pkl
│   ├── feature_scaler.pkl
│   ├── label_encoder.pkl
│   ├── model_config.json
│   ├── phishing_keywords.json
│   ├── stat_feature_cols.json
│   ├── mobilenet_final.h5
│   └── resnet_final.h5
│
└── backend/receipts_models/                # Receipt CV models
    ├── mobilenet_receipt_fraud.keras
    ├── resnet50_receipt_fraud.keras
    ├── cv_config.json
    └── cv_metrics.json
```

---

##  Requirements

If I want the setup to go as smoothly as possible, these are the versions I would use:

- Python 3.10
- TensorFlow 2.19
- Keras 3.x
- NumPy < 2.0

---

##  Project Status

What I have in the tracked `main` branch right now is a **Streamlit-first multimodal prototype** with:

- a Streamlit interface in `App_Frontend.py`
- data-preparation scripts in `src/data/`
- training notebooks and saved model artifacts in `backend/`

Some of the older GitHub issues talk about a bigger FastAPI + React + WebSocket setup, but when I compare those issues with the files that are actually tracked here, that is not the full shape of the repository at the moment.

If I want to explain how the repository and the GitHub issues line up, these are the two files I would point someone to:

- `docs/PROJECT_TRACEABILITY.md`
- `docs/ISSUE_ALIGNMENT.md`

---

##  How to Run

If I were walking someone through the project from scratch, these are the steps I would give them to get the app running locally:

### 1. Clone or download the project

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create a virtual environment (recommended)

```bash
conda create -n fraud_app python=3.10
conda activate fraud_app
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Ensure model files are in place

Before I launch the app, I make sure the model files shown in the **Project Structure** section are actually there. I also keep the project datasets inside the local `data/` folder, because that is the main working data area this repo now uses. If something is missing, the app will show a red status dot in the sidebar, and any unavailable analysis actions will stay disabled instead of failing partway through.

### 5. Run the project check

```bash
python scripts/validate_project.py
```

I added this script so I can quickly check that the main files, Python packages, and saved model files are all in place before I start the app.

### 6. Run the app

```bash
streamlit run App_Frontend.py
```

Then I open my browser at `http://localhost:8501`

If I rebuild or add model files while the app is already open, I can use the **Reload Model Status** button in the sidebar to refresh the model loaders.

---

##  Module Details

###  Phishing Email Analysis (Tab 1)
- I paste the email content into the text area
- I pick either **Naive Bayes** or **Random Forest**
- I can turn on **SHAP Explanation** if I want to see which words pushed the prediction
- Behind the scenes, I am using this flow: pre-cleaning → spaCy lemmatisation → TF-IDF → Chi-squared selection → classification

###  Receipt Fraud Detection (Tab 2)
- I upload a receipt image (`JPG`, `JPEG`, `PNG`, or `BMP`)
- I choose between **MobileNetV2** and **ResNet50**
- The model then gives me a fraud probability and a simple verdict: legitimate or fraudulent

###  ID Card Fraud Detection (Tab 3)
- I upload an ID card image (`JPG`, `JPEG`, `PNG`, `TIF`, `TIFF`, or `BMP`)
- The app pulls features from both CNN models and then runs One-Class SVM anomaly detection on top
- The final result comes back as one of three labels: **Genuine**, **Suspicious**, or **Fake**

###  Dataset Info (Tab 4)
- I use this tab to give a quick overview of the three datasets, the pipeline steps, and the ethical side of the project

---

##  Known Dependency Notes

- **NumPy**: keep it below `2.0`, because pandas and a few other packages can clash with NumPy 2.x
- **Keras**: use **Keras 3.x**, because the `.keras` models were saved that way in Colab and may fail on Keras 2.x
- **Streamlit**: use a fairly recent version, because older versions do not support `use_container_width` in `st.image()`

---

##  Ethical Considerations

- I recognise that the models can still flag genuine users by mistake, so I should never treat the results as perfect
- I also recognise that the training data may not fully represent every group, document type, or real-world fraud pattern
- If I get a high-risk result, I should expect a real person to review it before any important decision is made
- I am not treating this app as a tool for storing submitted content as part of normal use
- If I ever moved this beyond a student project, I would need to make sure it followed GDPR and any other relevant legal or compliance rules
