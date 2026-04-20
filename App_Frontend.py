

import streamlit as st
import numpy as np
import pandas as pd
import pickle
import json
import re
import string
import os
import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from PIL import Image
from scipy.sparse import hstack, csr_matrix



warnings.filterwarnings("ignore")


# PAGE CONFIG

st.set_page_config(
    page_title="MULTIMODAL FRAUD DETECTION SYSTEM AI",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# GLOBAL CSS

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --navy:       #050d1a;
    --navy2:      #091628;
    --navy3:      #0e2040;
    --gold:       #c9a84c;
    --gold-light: #e8c97a;
    --gold-dim:   #7a6030;
    --red:        #c0392b;
    --red-light:  #e74c3c;
    --green:      #1a7a4a;
    --green-light:#27ae60;
    --amber:      #d68910;
    --amber-light:#f39c12;
    --white:      #f5f5f0;
    --muted:      #8899aa;
    --border:     rgba(201,168,76,0.18);
    --border2:    rgba(255,255,255,0.06);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--navy);
    color: var(--white);
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.main .block-container { padding: 0 2.5rem 4rem 2.5rem; max-width: 1440px; }

.topbar {
    display: flex; align-items: center; justify-content: space-between;
    background: var(--navy2); border-bottom: 2px solid var(--gold);
    padding: 1rem 2.5rem; margin: -1rem -2.5rem 2.5rem -2.5rem;
}
.topbar-logo { font-family:'Bebas Neue',sans-serif; font-size:2rem; letter-spacing:4px; color:var(--gold); }
.topbar-sub  { font-size:0.7rem; letter-spacing:3px; color:var(--muted); text-transform:uppercase; margin-top:-4px; }
.topbar-badge { background:var(--gold); color:var(--navy); font-size:0.65rem; font-weight:700; letter-spacing:2px; padding:4px 14px; text-transform:uppercase; }

.stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--border); border:1px solid var(--border); margin-bottom:2.5rem; }
.stat-block { background:var(--navy2); padding:1.6rem 2rem; text-align:center; }
.stat-val { font-family:'Bebas Neue',sans-serif; font-size:2.4rem; letter-spacing:2px; color:var(--gold); line-height:1; }
.stat-lbl { font-size:0.68rem; letter-spacing:2px; color:var(--muted); text-transform:uppercase; margin-top:4px; }

.section-label {
    font-family:'Bebas Neue',sans-serif; font-size:1.5rem; letter-spacing:3px;
    color::#000000; text-transform:uppercase; border-left:4px solid var(--gold);
    padding-left:1rem; margin:2rem 0 1.2rem 0;
}

.card { background:var(--navy2); border:1px solid var(--border2); padding:1.8rem 2rem; margin-bottom:1rem; }
.card-title { font-size:0.65rem; letter-spacing:3px; text-transform:uppercase; color:var(--gold); margin-bottom:0.8rem; font-weight:600; }

.verdict-panel { padding:2rem 2.2rem; margin:1rem 0; border-left:6px solid; }
.verdict-panel.genuine    { background:rgba(26,122,74,0.12);   border-color:var(--green-light); }
.verdict-panel.safe       { background:rgba(26,122,74,0.12);   border-color:var(--green-light); }
.verdict-panel.suspicious { background:rgba(214,137,16,0.12);  border-color:var(--amber-light); }
.verdict-panel.warning    { background:rgba(214,137,16,0.12);  border-color:var(--amber-light); }
.verdict-panel.fake       { background:rgba(192,57,43,0.12);   border-color:var(--red-light); }
.verdict-panel.danger     { background:rgba(192,57,43,0.12);   border-color:var(--red-light); }

.verdict-label { font-family:'Bebas Neue',sans-serif; font-size:2.2rem; letter-spacing:4px; line-height:1; }
.verdict-label.genuine    { color:var(--green-light); }
.verdict-label.safe       { color:var(--green-light); }
.verdict-label.suspicious { color:var(--amber-light); }
.verdict-label.warning    { color:var(--amber-light); }
.verdict-label.fake       { color:var(--red-light); }
.verdict-label.danger     { color:var(--red-light); }
.verdict-sub { font-size:0.82rem; color:var(--muted); margin-top:0.4rem; letter-spacing:0.5px; }

.score-wrap { background:rgba(255,255,255,0.05); height:8px; margin:1rem 0 0.4rem; }
.score-fill-genuine    { background:var(--green-light); height:8px; }
.score-fill-safe       { background:var(--green-light); height:8px; }
.score-fill-suspicious { background:var(--amber-light); height:8px; }
.score-fill-warning    { background:var(--amber-light); height:8px; }
.score-fill-fake       { background:var(--red-light);   height:8px; }
.score-fill-danger     { background:var(--red-light);   height:8px; }
.score-meta { font-size:0.72rem; color:var(--muted); letter-spacing:1px; }

.metric-row { display:flex; gap:0.6rem; flex-wrap:wrap; margin:0.8rem 0; }
.metric-tile { background:rgba(255,255,255,0.04); border:1px solid var(--border2); padding:0.8rem 1.2rem; min-width:90px; text-align:center; }
.metric-tile-val { font-family:'Bebas Neue',sans-serif; font-size:1.5rem; letter-spacing:1px; color:var(--gold-light); }
.metric-tile-lbl { font-size:0.6rem; letter-spacing:2px; color:var(--muted); text-transform:uppercase; }

.alert-info { background:rgba(15,60,120,0.3); border-left:4px solid #4a90d9; padding:0.9rem 1.2rem; margin:0.8rem 0; font-size:0.85rem; color:#9ab8e0; line-height:1.6; }
.alert-warn { background:rgba(120,80,0,0.25); border-left:4px solid var(--amber-light); padding:0.9rem 1.2rem; margin:0.8rem 0; font-size:0.85rem; color:#d4a84b; line-height:1.6; }

.tag { display:inline-block; border:1px solid var(--border); color:var(--gold); font-size:0.65rem; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; padding:3px 10px; margin:2px; }
.tag-red   { border-color:rgba(192,57,43,0.5);  color:#e87060; }
.tag-green { border-color:rgba(26,122,74,0.5);  color:#60c890; }

.gold-divider { height:1px; background:linear-gradient(90deg,var(--gold),transparent); margin:2rem 0; opacity:0.4; }

.stButton > button {
    background:var(--gold) !important; color:var(--navy) !important;
    border:none !important; border-radius:0 !important;
    font-family:'Bebas Neue',sans-serif !important; font-size:1.05rem !important;
    letter-spacing:3px !important; padding:0.7rem 2rem !important; width:100% !important;
}
.stButton > button:hover { background:var(--gold-light) !important; }

.stTextArea textarea {
    background:var(--navy3) !important; border:1px solid rgba(201,168,76,0.2) !important;
    border-radius:0 !important; color:var(--white) !important;
}
.stTextArea textarea:focus { border-color:var(--gold) !important; box-shadow:none !important; }
.stSelectbox > div > div {
    background:var(--navy3) !important; border:1px solid rgba(201,168,76,0.2) !important;
    border-radius:0 !important; color:var(--white) !important;
}

[data-testid="stFileUploader"] {
    border:2px dashed rgba(201,168,76,0.25) !important;
    border-radius:0 !important; background:var(--navy2) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background:var(--navy2) !important; border-bottom:2px solid var(--gold) !important;
    gap:0 !important; padding:0 !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; border-radius:0 !important;
    color:var(--muted) !important; font-family:'Bebas Neue',sans-serif !important;
    font-size:0.95rem !important; letter-spacing:2px !important;
    padding:1rem 2rem !important; border-bottom:3px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    background:rgba(201,168,76,0.08) !important; color:var(--gold) !important;
    border-bottom:3px solid var(--gold) !important;
}

[data-testid="stSidebar"] { background:var(--navy2) !important; border-right:1px solid var(--border) !important; }
.sidebar-logo { font-family:'Bebas Neue',sans-serif; font-size:1.6rem; letter-spacing:4px; color:var(--gold); text-align:center; padding:1.5rem 0 0.2rem; }
.sidebar-sub  { font-size:0.6rem; letter-spacing:3px; color:var(--muted); text-transform:uppercase; text-align:center; margin-bottom:1.5rem; }
.sidebar-section { font-size:0.6rem; letter-spacing:2px; color:var(--gold-dim); text-transform:uppercase; font-weight:700; margin:1.2rem 0 0.5rem; }
.sidebar-item { font-size:0.82rem; color:var(--muted); padding:2px 0; line-height:1.8; }

.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }
.dot-green { background:var(--green-light); }
.dot-red   { background:var(--red-light); }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:var(--navy); }
::-webkit-scrollbar-thumb { background:var(--gold-dim); }
</style>
""", unsafe_allow_html=True)



# MODEL LOADERS


@st.cache_resource
def load_nlp_models():
    m = {}
    try:
        with open('./backend/saved_models/mnb_model.pkl',        'rb') as f: m['mnb']      = pickle.load(f)
        with open('./backend/saved_models/rf_model.pkl',         'rb') as f: m['rf']       = pickle.load(f)
        with open('./backend/saved_models/tfidf_vectorizer.pkl', 'rb') as f: m['tfidf']    = pickle.load(f)
        with open('./backend/saved_models/chi2_selector.pkl',    'rb') as f: m['chi2']     = pickle.load(f)
        with open('./backend/saved_models/phishing_keywords.json')     as f: m['keywords'] = json.load(f)
        with open('./backend/saved_models/stat_feature_cols.json')     as f: m['stat_cols']= json.load(f)
        m['loaded'] = True
    except Exception as e:
        m['loaded'] = False; m['error'] = str(e)
    return m

   
@st.cache_resource
def load_receipt_models():
    import tensorflow as tf
    import traceback, os
    m = {}
    try:
        m['mobilenet'] = tf.keras.models.load_model(
            './backend/receipts_models/mobilenet_receipt_fraud.keras', compile=False)
        m['resnet'] = tf.keras.models.load_model(
            './backend/receipts_models/resnet50_receipt_fraud.keras', compile=False)
        with open('./backend/receipts_models/cv_config.json')  as f: m['config']  = json.load(f)
        with open('./backend/receipts_models/cv_metrics.json') as f: m['metrics'] = json.load(f)
        m['loaded'] = True
    except Exception as e:
        m['loaded'] = False
        m['error']  = str(e)
        m['trace']  = traceback.format_exc()  # ← full stack trace
    return m

@st.cache_resource
def load_id_models():
    import tensorflow as tf
    from tensorflow.keras.models import load_model as keras_load
    m = {}
    try:
        m['mobilenet'] = keras_load('./backend/saved_models/mobilenet_final.h5')
        m['resnet']    = keras_load('./backend/saved_models/resnet_final.h5')
        with open('./backend/saved_models/ocsvm.pkl',          'rb') as f: m['ocsvm']  = pickle.load(f)
        with open('./backend/saved_models/feature_scaler.pkl', 'rb') as f: m['scaler'] = pickle.load(f)
        with open('./backend/saved_models/label_encoder.pkl',  'rb') as f: m['le']     = pickle.load(f)
        with open('./backend/saved_models/model_config.json')       as f: m['config']  = json.load(f)
        m['thresholds'] = m['config'].get('thresholds', {'genuine': 0.85, 'suspicious': 0.40})
        m['loaded'] = True
    except Exception as e:
        m['loaded'] = False; m['error'] = str(e)
    return m








@st.cache_resource
def load_spacy():
    import spacy
    return spacy.load("en_core_web_sm")



# NLP HELPERS


KEEP_POS    = {"NOUN","VERB","ADJ","ADV","PROPN"}
EMAIL_NOISE = {"enron","ect","hou","forwarded","original","attached","fw","re",
               "fwd","cc","bcc","please","thank","thanks","regards","sincerely",
               "dear","hello","hi","hey","said","say","says"}

def pre_clean(text):
    if not text or str(text).strip() == "": return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\S+@\S+",        "", text)
    text = re.sub(r"\d+",            "", text)
    text = text.translate(str.maketrans("","",string.punctuation))
    return re.sub(r"\s+", " ", text).strip()

def pos_filter(doc):
    return " ".join(
        t.lemma_ for t in doc
        if t.pos_ in KEEP_POS and t.lemma_ not in EMAIL_NOISE
        and len(t.lemma_) > 2 and not t.is_stop
    )

def extract_stat_features(text, keywords):
    return {
        "char_count":             len(text),
        "word_count":             len(text.split()),
        "unique_word_ratio":      len(set(text.split()))/(len(text.split())+1),
        "url_count":              len(re.findall(r"http\S+|www\S+", text)),
        "email_count":            len(re.findall(r"\S+@\S+", text)),
        "has_unsubscribe":        int("unsubscribe" in text.lower()),
        "phishing_keyword_count": sum(1 for kw in keywords if kw in text.lower())
    }

def predict_email(text, model_choice, nlp_models, nlp):
    cleaned   = pre_clean(text)
    processed = pos_filter(nlp(cleaned))
    tfidf_vec = nlp_models['tfidf'].transform([processed])
    stat_feat = extract_stat_features(text, nlp_models['keywords'])
    stat_sp   = csr_matrix(pd.DataFrame([stat_feat]).values)
    combined  = hstack([tfidf_vec, stat_sp])
    final_inp = nlp_models['chi2'].transform(combined)
    model     = nlp_models['mnb'] if model_choice == "Naive Bayes" else nlp_models['rf']
    pred      = model.predict(final_inp)[0]
    prob      = model.predict_proba(final_inp)[0][1]
    return {"pred": int(pred), "prob": float(prob),
            "label": "PHISHING" if pred==1 else "LEGITIMATE",
            "processed": processed, "stat_feat": stat_feat,
            "final_inp": final_inp, "model": model}

def compute_shap(result, nlp_models):
    try:
        import shap
        model = result['model']
        inp   = result['final_inp']
        name  = type(model).__name__
        exp   = (shap.LinearExplainer(model, inp, feature_perturbation="interventional")
                 if name == 'MultinomialNB' else shap.TreeExplainer(model))
        vals  = exp.shap_values(inp)
        if isinstance(vals, list): vals = vals[1]
        vals  = np.array(vals).flatten()
        all_names = np.array(
            list(nlp_models['tfidf'].get_feature_names_out()) + nlp_models['stat_cols']
        )
        sel   = all_names[nlp_models['chi2'].get_support()]
        top   = np.argsort(np.abs(vals))[-15:][::-1]
        return {"names": sel[top], "values": vals[top], "success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def render_shap(shap_result):
    names, values = shap_result['names'], shap_result['values']
    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor('#091628'); ax.set_facecolor('#091628')
    colors = ['#c0392b' if v > 0 else '#2980b9' for v in values]
    ax.barh(range(len(names)), values, color=colors, edgecolor='none', height=0.6)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=8.5, color='#aabbcc')
    ax.invert_yaxis()
    ax.axvline(0, color='rgba(255,255,255,0.1)', lw=0.8, ls='--')
    ax.set_xlabel('SHAP Value  (positive = phishing signal  |  negative = legitimate signal)',
                  fontsize=8, color='#8899aa')
    ax.set_title('Feature Attribution', fontsize=10, fontweight='bold', color='#f5f5f0', pad=10)
    ax.tick_params(axis='x', colors='#8899aa', labelsize=8)
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('rgba(255,255,255,0.08)')
    ax.grid(axis='x', alpha=0.07, color='white')
    p1 = mpatches.Patch(color='#c0392b', label='Phishing indicator')
    p2 = mpatches.Patch(color='#2980b9', label='Legitimate indicator')
    ax.legend(handles=[p1,p2], fontsize=8, facecolor='#0e2040',
              edgecolor='none', labelcolor='#aabbcc', loc='lower right')
    plt.tight_layout(); return fig



# CV HELPERS — RECEIPT


def predict_receipt(image, model_choice, cv_models):
    img_size  = tuple(cv_models['config']['img_size'])
    arr       = np.expand_dims(np.array(image.convert('RGB').resize(img_size))/255.0, 0)
    model     = cv_models['mobilenet'] if model_choice=="MobileNetV2" else cv_models['resnet']
    threshold = cv_models['config'].get(
        'mobilenet_threshold' if model_choice=="MobileNetV2" else 'resnet_threshold',
        cv_models['config'].get('threshold', 0.5)
    )
    prob = float(model.predict(arr, verbose=0)[0][0])
    pred = 1 if prob >= threshold else 0
    conf = prob if pred==1 else 1-prob
    return {"pred": pred, "prob": prob, "conf": conf, "threshold": threshold,
            "label": "FRAUDULENT" if pred==1 else "LEGITIMATE"}



# CV HELPERS — ID CARD


def predict_id_card(image, id_models):
    from tensorflow.keras.models import Model as KModel
    IMG_SIZE = (224, 224)
    arr      = np.expand_dims(np.array(image.convert('RGB').resize(IMG_SIZE))/255.0, 0)
    mn, rn   = id_models['mobilenet'], id_models['resnet']
    ocsvm    = id_models['ocsvm']
    scaler   = id_models['scaler']
    le       = id_models['le']
    thr      = id_models['thresholds']

    mn_feat  = KModel(inputs=mn.input, outputs=mn.get_layer('feature_layer').output).predict(arr, verbose=0)
    rn_feat  = KModel(inputs=rn.input, outputs=rn.get_layer('feature_layer').output).predict(arr, verbose=0)
    combined = np.concatenate([mn_feat, rn_feat], axis=1)
    score    = float(np.clip((ocsvm.decision_function(scaler.transform(combined))[0]+1)/2, 0, 1))

    avg_probs = (mn.predict(arr, verbose=0)[0] + rn.predict(arr, verbose=0)[0]) / 2
    doc_idx   = np.argmax(avg_probs)
    doc_type  = le.inverse_transform([doc_idx])[0]
    confidence= float(avg_probs[doc_idx])

    if score >= thr['genuine']:
        verdict, css, label = "GENUINE",    "genuine",    "Genuine Identity Document"
    elif score >= thr['suspicious']:
        verdict, css, label = "SUSPICIOUS", "suspicious", "Suspicious — Manual Review Required"
    else:
        verdict, css, label = "FAKE",       "fake",       "Fake / Not a Valid ID"

    return {"score": round(score,4), "verdict": verdict, "css": css, "label": label,
            "doc_type": doc_type, "confidence": round(confidence,4), "thresholds": thr}



# UI HELPERS


def verdict_panel(label, sub, css, score_pct, meta):
    st.markdown(f"""
    <div class="verdict-panel {css}">
        <div class="verdict-label {css}">{label}</div>
        <div class="verdict-sub">{sub}</div>
        <div class="score-wrap"><div class="score-fill-{css}" style="width:{score_pct}%"></div></div>
        <div class="score-meta">{meta}</div>
    </div>""", unsafe_allow_html=True)

def metric_tiles(items):
    tiles = "".join(
        f'<div class="metric-tile"><div class="metric-tile-val">{v}</div>'
        f'<div class="metric-tile-lbl">{k}</div></div>'
        for k, v in items
    )
    st.markdown(f'<div class="metric-row">{tiles}</div>', unsafe_allow_html=True)

def section_label(text):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)

def gold_divider():
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

def alert_info(text):
    st.markdown(f'<div class="alert-info">{text}</div>', unsafe_allow_html=True)

def alert_warn(text):
    st.markdown(f'<div class="alert-warn">{text}</div>', unsafe_allow_html=True)

def empty_state(icon, title, sub):
    st.markdown(f"""
    <div style="text-align:center;padding:3.5rem 1rem;color:#334455">
        <div style="font-size:2.8rem;margin-bottom:0.8rem">{icon}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:3px;
                    color:#445566;margin-bottom:0.4rem">{title}</div>
        <div style="font-size:0.8rem;color:#334455;letter-spacing:1px">{sub}</div>
    </div>""", unsafe_allow_html=True)



# LOAD MODELS


nlp_models     = load_nlp_models()
receipt_models = load_receipt_models()
id_models      = load_id_models()



# SIDEBAR


with st.sidebar:
    st.markdown('<div class="sidebar-logo">MULTIMODAL FRAUD DETECTION SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Fraud Detection System</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-section">System Status</div>', unsafe_allow_html=True)

    for name, m in [("NLP Module",  nlp_models),
                    ("Receipt CV",  receipt_models),
                    ("ID Card CV",  id_models)]:
        ok    = m.get('loaded')
        dot   = "dot-green" if ok else "dot-red"
        state = "Operational" if ok else "Offline"
        color = "#60c890"    if ok else "#e87060"
        st.markdown(
            f'<div class="sidebar-item"><span class="status-dot {dot}"></span>'
            f'<span style="color:{color}">{name}</span> — {state}</div>',
            unsafe_allow_html=True
        )
        if not ok and 'error' in m:
            st.code(m.get('trace', m['error']))  # shows full traceback if available

    st.markdown("---")
    st.markdown('<div class="sidebar-section">NLP Module</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">Multinomial Naive Bayes<br>Random Forest<br>TF-IDF + Chi2 Selection<br>SHAP Explainability</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Receipt CV Module</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item">MobileNetV2 (Transfer Learning)<br>ResNet50 (Transfer Learning)<br>COCO Annotated Dataset</div>', unsafe_allow_html=True)

  

# TOP BAR + STATS


st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-logo">MULTIMODAL FRAUD DETECTION SYSTEM AI</div>
        <div class="topbar-sub">Multimodal Fraud Detection System</div>
    </div>

</div>
<div class="stat-row">
    <div class="stat-block"><div class="stat-val">3</div><div class="stat-lbl">Detection Modules</div></div>
    <div class="stat-block"><div class="stat-val">5</div><div class="stat-lbl">Trained Models</div></div>
    <div class="stat-block"><div class="stat-val">1,265</div><div class="stat-lbl">Receipt Images</div></div>
    <div class="stat-block"><div class="stat-val">SHAP</div><div class="stat-lbl">Explainability</div></div>
</div>
""", unsafe_allow_html=True)



# TABS


tab1, tab2, tab3, tab4 = st.tabs([
    "  Email Fraud  ",
    "  Receipt Fraud  ",
    "  ID Card Fraud  ",
    "  Dataset Info  ",
])



# TAB 1 — PHISHING EMAIL

with tab1:
    section_label("Email Fruad Analysis")
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.markdown('<div class="card"><div class="card-title">Email Content</div>', unsafe_allow_html=True)
        email_text = st.text_area("Email", height=220,
            placeholder="Paste the full email text — subject, body, any URLs...",
            label_visibility="collapsed")
        col_a, col_b = st.columns(2)
        with col_a: nlp_algo  = st.selectbox("Algorithm", ["Naive Bayes", "Random Forest"])
        with col_b: show_shap = st.checkbox("SHAP Explanation", value=True)
        run_nlp = st.button("RUN ANALYSIS", key="nlp_btn")
        st.markdown('</div>', unsafe_allow_html=True)



    with right:
        if run_nlp and email_text.strip():
            if not nlp_models.get('loaded'):
                alert_warn("NLP models not found. Train and save using the notebook first.")
            else:
                with st.spinner("Analysing..."):
                    try:
                        nlp = load_spacy()
                        res = predict_email(email_text, nlp_algo, nlp_models, nlp)
                        prob, pred = res['prob'], res['pred']
                        css  = "danger" if pred==1 else "safe"
                        lbl  = "FRAUD DETECTED" if pred==1 else "LEGITIMATE EMAIL"
                        pct  = round(prob*100 if pred==1 else (1-prob)*100, 1)
                        verdict_panel(lbl, f"Spam probability: {round(prob*100,1)}%",
                                      css, pct, f"Algorithm: {nlp_algo}  |  Confidence: {pct}%")
                        sf = res['stat_feat']
                        metric_tiles([
                            ("URLs",      sf['url_count']),
                            ("Emails",    sf['email_count']),
                            ("Keywords",  sf['phishing_keyword_count']),
                            ("Unsub",     "Yes" if sf['has_unsubscribe'] else "No"),
                            ("Words",     sf['word_count']),
                        ])
                    except Exception as e:
                        st.error(f"Error: {e}")
        elif run_nlp:
            alert_info("Please enter email text before running analysis.")
        else:
            empty_state("✉", "AWAITING INPUT", "Enter an email and click Run Analysis")

    if run_nlp and email_text.strip() and nlp_models.get('loaded') and show_shap:
        gold_divider()
        section_label("SHAP Feature Attribution")
        alert_info("Red bars push toward phishing. Blue bars push toward legitimate.")
        with st.spinner("Computing SHAP values..."):
            try:
                nlp    = load_spacy()
                res    = predict_email(email_text, nlp_algo, nlp_models, nlp)
                shap_r = compute_shap(res, nlp_models)
                if shap_r['success']:
                    fig = render_shap(shap_r)
                    st.pyplot(fig, use_column_width=True)
                    plt.close()
                    with st.expander("Raw SHAP values"):
                        st.dataframe(pd.DataFrame({
                            'Feature':   shap_r['names'],
                            'SHAP':      [round(v,5) for v in shap_r['values']],
                            'Direction': ['Phishing' if v>0 else 'Legitimate' for v in shap_r['values']]
                        }), use_column_width=True, hide_index=True)
                else:
                    alert_warn(f"SHAP unavailable: {shap_r['error']}. Run: pip install shap")
            except Exception as e:
                alert_warn(f"SHAP error: {e}")



# TAB 2 — RECEIPT FRAUD

with tab2:
    section_label("Receipt Fraud Detection")
    left2, right2 = st.columns([1, 1.1], gap="large")

    with left2:
        st.markdown('<div class="card"><div class="card-title">Upload Receipt Image</div>', unsafe_allow_html=True)
        receipt_file = st.file_uploader("Receipt", type=["jpg","jpeg","png","bmp"],
                                        label_visibility="collapsed")
        receipt_algo = st.selectbox("CV Algorithm", ["MobileNetV2", "ResNet50"])
        run_receipt  = st.button("RUN ANALYSIS", key="receipt_btn")
        st.markdown('</div>', unsafe_allow_html=True)

        if receipt_file:
            st.image(Image.open(receipt_file), caption="Uploaded Receipt", use_column_width=True)

        if receipt_models.get('loaded') and 'metrics' in receipt_models:
            with st.expander("Model Performance"):
                for mname, mvals in receipt_models['metrics'].items():
                    st.markdown(f"**{mname}**")
                    cols = st.columns(5)
                    for col, (k, v) in zip(cols, list(mvals.items())[:5]):
                        col.metric(k.replace('_',' ').title(), f"{v:.3f}" if isinstance(v,float) else str(v))

    with right2:
        if run_receipt and receipt_file:
            if not receipt_models.get('loaded'):
                alert_warn("Receipt CV models not found. Train and save using the notebook first.")
            else:
                with st.spinner("Analysing receipt..."):
                    try:
                        res  = predict_receipt(Image.open(receipt_file), receipt_algo, receipt_models)
                        prob, pred = res['prob'], res['pred']
                        css  = "danger" if pred==1 else "safe"
                        lbl  = "FRAUDULENT RECEIPT" if pred==1 else "LEGITIMATE RECEIPT"
                        pct  = round(res['conf']*100, 1)
                        verdict_panel(lbl, f"Fraud probability: {round(prob*100,1)}%", css, pct,
                                      f"Algorithm: {receipt_algo}  |  Threshold: {res['threshold']}  |  Confidence: {pct}%")
                        metric_tiles([
                            ("Legitimate",  f"{round((1-prob)*100,1)}%"),
                            ("Fraudulent",  f"{round(prob*100,1)}%"),
                            ("Confidence",  f"{pct}%"),
                            ("Threshold",   res['threshold']),
                        ])
                        if   prob >= 0.8: alert_warn("HIGH RISK — Flag for immediate manual review.")
                        elif prob >= 0.5: alert_warn("MODERATE RISK — Further verification recommended.")
                        else:             alert_info("LOW RISK — No significant fraud indicators detected.")
                    except Exception as e:
                        st.error(f"Error: {e}")
        elif run_receipt:
            alert_info("Please upload a receipt image first.")
        else:
            empty_state("🧾", "AWAITING IMAGE", "Upload a receipt and click Run Analysis")



# TAB 3 — ID CARD FRAUD

with tab3:
    section_label("Identity Card Fraud Detection")
    alert_info(
        "One-class anomaly detection trained on the <strong>MIDV-2019</strong> dataset. "
        "The system assigns an authenticity score to the uploaded ID image and classifies "
        "it as <strong>Genuine</strong>, <strong>Suspicious</strong>, or <strong>Fake</strong> "
        "using calibrated thresholds."
    )

    left3, right3 = st.columns([1, 1.1], gap="large")

    with left3:
        st.markdown('<div class="card"><div class="card-title">Upload ID Card Image</div>', unsafe_allow_html=True)
        id_file  = st.file_uploader("ID Card", type=["jpg","jpeg","png","tif","tiff","bmp"],
                                    label_visibility="collapsed", key="id_uploader")
        run_id   = st.button("RUN ANALYSIS", key="id_btn")
        st.markdown('</div>', unsafe_allow_html=True)

        if id_file:
            st.image(Image.open(id_file), caption="Uploaded ID Card", use_column_width=True)

        thr = id_models.get('thresholds', {'genuine': 0.85, 'suspicious': 0.40}) \
              if id_models.get('loaded') else {'genuine': 0.85, 'suspicious': 0.40}
        st.markdown(f"""
        <div class="card" style="margin-top:1rem">
            <div class="card-title">Detection Thresholds</div>
            <div style="font-size:0.85rem;line-height:2.4;color:#8899aa">
                <span style="color:#27ae60;font-weight:600">Genuine</span>
                &nbsp;&nbsp;&nbsp; Score &ge; {thr['genuine']}<br>
                <span style="color:#f39c12;font-weight:600">Suspicious</span>
                &nbsp; Score {thr['suspicious']} &ndash; {thr['genuine']}<br>
                <span style="color:#e74c3c;font-weight:600">Fake</span>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Score &lt; {thr['suspicious']}
            </div>
        </div>
        <div class="card">
            <div class="card-title">How It Works</div>
            <div style="font-size:0.82rem;color:#8899aa;line-height:2.1">
                1. MobileNetV2 extracts 64-dimensional features<br>
                2. ResNet50 extracts 64-dimensional features<br>
                3. Features concatenated into 128-dim vector<br>
                4. StandardScaler normalises the vector<br>
                5. One-Class SVM computes anomaly score<br>
                6. Score mapped to Genuine / Suspicious / Fake
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right3:
        if run_id and id_file:
            if not id_models.get('loaded'):
                alert_warn(
                    "ID card models not found. Expected in <code>saved_models/id/</code>:<br>"
                    "mobilenet_final.h5 &nbsp; resnet_final.h5 &nbsp; ocsvm.pkl &nbsp; "
                    "feature_scaler.pkl &nbsp; label_encoder.pkl &nbsp; model_config.json"
                )
            else:
                with st.spinner("Analysing ID card..."):
                    try:
                        res   = predict_id_card(Image.open(id_file), id_models)
                        score = res['score']
                        css   = res['css']
                        pct   = round(score * 100, 1)
                        verdict_panel(
                            res['verdict'], res['label'], css, pct,
                            f"Authenticity score: {score}  |  "
                            f"Document type: {res['doc_type']}  |  "
                            f"Classifier confidence: {round(res['confidence']*100,1)}%"
                        )
                        metric_tiles([
                            ("Auth Score",  f"{score:.3f}"),
                            ("Verdict",     res['verdict']),
                            ("Doc Type",    res['doc_type']),
                            ("Confidence",  f"{round(res['confidence']*100,1)}%"),
                        ])

                        # Score gauge chart
                        fig, ax = plt.subplots(figsize=(8, 1.6))
                        fig.patch.set_facecolor('#091628'); ax.set_facecolor('#091628')
                        t = res['thresholds']
                        ax.barh(0, t['suspicious'],              height=0.45, color='#c0392b', alpha=0.35, left=0)
                        ax.barh(0, t['genuine']-t['suspicious'], height=0.45, color='#d68910', alpha=0.35, left=t['suspicious'])
                        ax.barh(0, 1.0-t['genuine'],             height=0.45, color='#1a7a4a', alpha=0.35, left=t['genuine'])
                        ax.axvline(score, color='#c9a84c', lw=2.5)
                        ax.text(score+0.01, 0.28, f"{score:.3f}", color='#e8c97a',
                                fontsize=9, fontweight='bold', va='center')
                        ax.set_xlim(0,1); ax.set_ylim(-0.5,0.5); ax.axis('off')
                        ax.set_title('Authenticity Score Gauge', color='#8899aa', fontsize=8, loc='left', pad=4)
                        plt.tight_layout()
                        st.pyplot(fig); plt.close()

                        if css == 'genuine':
                            alert_info("Document appears genuine. Visual and anomaly checks passed.")
                        elif css == 'suspicious':
                            alert_warn("Anomalous characteristics detected. Manual verification by a qualified officer is strongly recommended before accepting this document.")
                        else:
                            alert_warn("HIGH RISK — Document shows strong indicators of being fraudulent. Do not accept without thorough in-person verification.")

                    except Exception as e:
                        st.error(f"Error during ID analysis: {e}")
        elif run_id:
            alert_info("Please upload an ID card image before running analysis.")
        else:
            empty_state("🪪", "AWAITING IMAGE", "Upload an ID card image and click Run Analysis")



# TAB 4 — DATASET INFO

with tab4:
    section_label("Dataset & System Information")
    col_d1, col_d2, col_d3 = st.columns(3, gap="large")

    with col_d1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Phishing Email Dataset</div>
            <p style="font-size:0.85rem;color:#8899aa;line-height:1.8;margin:0 0 1rem 0">
                Compiled to study phishing email tactics, combining emails from the
                Enron and Ling-Spam datasets to create a comprehensive resource for
                spam and phishing analysis.
            </p>
            <div style="font-size:0.8rem;color:#aabbcc;line-height:2.1">
                <strong style="color:#c9a84c">Sources</strong><br>
                Enron Email Dataset<br>Ling-Spam Dataset<br><br>
                <strong style="color:#c9a84c">Labels</strong><br>
                Spam / Phishing &nbsp; (class 1)<br>Ham / Legitimate &nbsp; (class 0)
            </div>
            <br>
            <span class="tag">TF-IDF</span><span class="tag">Chi2 Selection</span>
            <span class="tag tag-red">Phishing</span><span class="tag tag-green">Legitimate</span>
            <span class="tag">SHAP</span>
        </div>
        <div class="card">
            <div class="card-title">NLP Pipeline Steps</div>
            <div style="font-size:0.82rem;color:#8899aa;line-height:2.2;counter-reset:step">
                1. Pre-cleaning (URLs, emails, digits removed)<br>
                2. spaCy lemmatisation + POS tag filtering<br>
                3. TF-IDF vectorisation (top 10,000 n-grams)<br>
                4. Statistical features (URL count, keyword density)<br>
                5. Chi-squared feature selection (top 5,000)<br>
                6. Classification — Naive Bayes or Random Forest<br>
                7. SHAP feature attribution
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_d2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Receipt Fraud Dataset</div>
            <p style="font-size:0.85rem;color:#8899aa;line-height:1.8;margin:0 0 1rem 0">
                Exported via Roboflow (October 2024). Based on the SROIE dataset —
                988 scanned receipts with realistic fraudulent modifications annotated
                in COCO format. 3x augmentation applied per source image.
            </p>
            <div style="font-size:0.8rem;color:#aabbcc;line-height:2.1">
                <strong style="color:#c9a84c">Volume</strong><br>
                1,265 images &nbsp; 640x640 px<br><br>
                <strong style="color:#c9a84c">Annotation Categories</strong><br>
                fraud &nbsp; (category_id 2)<br>damage &nbsp; (category_id 1)
            </div>
            <br>
            <span class="tag">COCO Format</span><span class="tag">Roboflow</span>
            <span class="tag tag-red">Fraudulent</span><span class="tag tag-green">Legitimate</span>
        </div>
        <div class="card">
            <div class="card-title">Receipt CV Pipeline Steps</div>
            <div style="font-size:0.82rem;color:#8899aa;line-height:2.2">
                1. COCO annotation parsing (fraud/damage vs clean)<br>
                2. ImageDataGenerator augmentation for training<br>
                3. MobileNetV2 or ResNet50 transfer learning<br>
                4. Binary classification (fraudulent vs legitimate)<br>
                5. Mild class weighting for imbalance handling<br>
                6. Fixed threshold (0.5) for final classification
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_d3:
        st.markdown("""
        <div class="card">
            <div class="card-title">MIDV-2019 ID Card Dataset</div>
            <p style="font-size:0.85rem;color:#8899aa;line-height:1.8;margin:0 0 1rem 0">
                A benchmark dataset for identity document analysis containing
                genuine identity documents captured under four controlled
                conditions — desktop and smartphone, good and complex backgrounds.
            </p>
            <div style="font-size:0.8rem;color:#aabbcc;line-height:2.1">
                <strong style="color:#c9a84c">Capture Conditions</strong><br>
                DG — Desktop, Good lighting<br>
                DX — Desktop, Complex background<br>
                LG — Smartphone, Good lighting<br>
                LX — Smartphone, Complex background<br><br>
                <strong style="color:#c9a84c">Approach</strong><br>
                One-class anomaly detection (genuine IDs only)
            </div>
            <br>
            <span class="tag">MIDV-2019</span><span class="tag">One-Class SVM</span>
            <span class="tag tag-green">Genuine</span>
            <span class="tag" style="border-color:rgba(214,137,16,0.5);color:#f39c12">Suspicious</span>
            <span class="tag tag-red">Fake</span>
        </div>
        <div class="card">
            <div class="card-title">ID Card CV Pipeline Steps</div>
            <div style="font-size:0.82rem;color:#8899aa;line-height:2.2">
                1. Image loading — TIF / JPG / PNG / video frames<br>
                2. MobileNetV2 feature extraction (64-dim)<br>
                3. ResNet50 feature extraction (64-dim)<br>
                4. Feature concatenation (128-dim vector)<br>
                5. StandardScaler normalisation<br>
                6. One-Class SVM anomaly scoring<br>
                7. Three-tier threshold classification
            </div>
        </div>
        """, unsafe_allow_html=True)

    gold_divider()
    st.markdown("""
    <div class="card">
        <div class="card-title">Ethical Considerations</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:2rem;
                    font-size:0.83rem;color:#8899aa;line-height:1.9">
            <div>
                <strong style="color:#c9a84c;display:block;margin-bottom:0.4rem">Bias and Fairness</strong>
                Training data may underrepresent certain demographics, writing styles, or document
                types. Models may produce false positives for legitimate users. Regular bias audits are recommended.
            </div>
            <div>
                <strong style="color:#c9a84c;display:block;margin-bottom:0.4rem">Privacy and Data Protection</strong>
                Email and identity document content is sensitive personal data. This system does not
                store submitted content. Production deployment must comply with GDPR and applicable law.
            </div>
            <div>
                <strong style="color:#c9a84c;display:block;margin-bottom:0.4rem">Human Oversight</strong>
                AI predictions should augment, not replace, human judgement. All high-risk verdicts
                should be reviewed by a qualified person before any consequential decision is made.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
