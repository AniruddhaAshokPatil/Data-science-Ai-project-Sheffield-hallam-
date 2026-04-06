import React, { useEffect, useMemo, useState } from 'react';

const MERCHANT_OPTIONS = [
  'online',
  'retail',
  'travel',
  'utilities',
  'restaurant',
  'entertainment',
  'grocery',
  'other'
];

const DEVICE_OPTIONS = ['web', 'mobile', 'pos', 'atm'];
const TRANSACTION_TYPE_OPTIONS = ['payment', 'transfer', 'withdrawal', 'deposit'];
const LOCATION_OPTIONS = ['London', 'Tokyo', 'New York', 'Dubai', 'Singapore', 'Sydney', 'Berlin', 'Toronto'];
const PAYMENT_CHANNEL_OPTIONS = ['card', 'wire_transfer', 'ACH', 'UPI'];

const SAMPLE_CV_PATH = '/Users/productguru/Documents/GitHub/Data-science-Ai-project-Sheffield-hallam-/data/processed/cv/test/original/img_00185_orig.jpg';

function clamp01(value) {
  // I clamp preview values here because my frontend preview should stay on the
  // same 0 to 1 scale that the backend risk response uses.
  const number = Number(value || 0);
  if (number < 0) return 0;
  if (number > 1) return 1;
  return number;
}

function highlightMessage(text) {
  // I highlight phishing-style words here so the user can see why a message
  // feels suspicious before I even send it to the backend NLP route.
  const keywordGroups = [
    { pattern: /\b(urgent|suspended|locked|immediately)\b/gi, className: 'keyword-danger' },
    { pattern: /\b(click|verify|confirm|claim)\b/gi, className: 'keyword-warn' }
  ];

  const parts = [{ text, className: '' }];

  keywordGroups.forEach(({ pattern, className }) => {
    const nextParts = [];
    parts.forEach((part) => {
      if (part.className) {
        nextParts.push(part);
        return;
      }

      let lastIndex = 0;
      let match = pattern.exec(part.text);
      while (match) {
        if (match.index > lastIndex) {
          nextParts.push({ text: part.text.slice(lastIndex, match.index), className: '' });
        }
        nextParts.push({ text: match[0], className });
        lastIndex = match.index + match[0].length;
        match = pattern.exec(part.text);
      }

      if (lastIndex < part.text.length) {
        nextParts.push({ text: part.text.slice(lastIndex), className: '' });
      }
      pattern.lastIndex = 0;
    });
    parts.splice(0, parts.length, ...nextParts);
  });

  return parts;
}

function getPreviewScenario({ amount, velocityScore, geoScore, merchantCategory, deviceUsed, previewRisk }) {
  // I keep the scenario guess simple here so the preview remains easy to
  // explain before the real backend result arrives.
  if (previewRisk >= 0.65 && merchantCategory === 'online' && deviceUsed === 'web') {
    return 'Card Not Present Fraud';
  }
  if (previewRisk >= 0.55 && velocityScore >= 14 && amount <= 50) {
    return 'Card Testing';
  }
  if (previewRisk >= 0.55 && geoScore >= 0.7) {
    return 'Account Takeover';
  }
  return 'Normal Behaviour';
}

export default function Controls({
  onSubmitTransaction,
  onSubmitNlp,
  onSubmitCv,
  onPreviewChange,
  onNotify,
  onError,
  onRefreshReadiness
}) {
  // I keep the transaction form close to the financial dataset columns so the
  // dashboard can demonstrate realistic fraud features from the project data.
  const [amount, setAmount] = useState(420.0);
  const [spendingDeviation, setSpendingDeviation] = useState(0.9);
  const [velocityScore, setVelocityScore] = useState(12);
  const [geoScore, setGeoScore] = useState(0.45);
  const [merchantCategory, setMerchantCategory] = useState('online');
  const [deviceUsed, setDeviceUsed] = useState('web');
  const [transactionType, setTransactionType] = useState('payment');
  const [location, setLocation] = useState('London');
  const [paymentChannel, setPaymentChannel] = useState('card');
  const [receiverAccount, setReceiverAccount] = useState('ACC344098');
  const [deviceHash, setDeviceHash] = useState('D9961380');
  const [ipAddress, setIpAddress] = useState('107.136.36.87');

  const [nlpText, setNlpText] = useState(
    'URGENT: Your account has been suspended. Click here now to verify your details.'
  );

  const [vizPath, setVizPath] = useState('');
  const [cvPath, setCvPath] = useState(SAMPLE_CV_PATH);
  const [cvSuspicious, setCvSuspicious] = useState(false);
  const [cvEdited, setCvEdited] = useState(false);
  const [cvSource, setCvSource] = useState('internal');
  const [busyAction, setBusyAction] = useState('');

  const preview = useMemo(() => {
    // I mirror the backend financial scoring branch here so the preview feels
    // consistent with the real API result when I submit the form.
    const amountNorm = clamp01(Number(amount) / 1500);
    const spendingNorm = clamp01(Math.abs(Number(spendingDeviation)) / 3);
    const velocityNorm = clamp01(Number(velocityScore) / 20);
    const geoNorm = clamp01(Number(geoScore));
    const tabularProb = (0.30 * amountNorm) + (0.25 * spendingNorm) + (0.25 * velocityNorm) + (0.20 * geoNorm);
    const finalRisk = clamp01(tabularProb * 0.6);
    const scenario = getPreviewScenario({
      amount: Number(amount),
      velocityScore: Number(velocityScore),
      geoScore: Number(geoScore),
      merchantCategory,
      deviceUsed,
      previewRisk: finalRisk
    });

    return {
      risk: finalRisk,
      scenario
    };
  }, [amount, spendingDeviation, velocityScore, geoScore, merchantCategory, deviceUsed]);

  useEffect(() => {
    // I push preview changes upward here so the risk intelligence panel can
    // update live while the user moves sliders or edits inputs.
    onPreviewChange?.(preview);
  }, [preview, onPreviewChange]);

  const highlightedMessage = useMemo(() => highlightMessage(nlpText), [nlpText]);

  async function predictTransaction() {
    const payload = {
      features: {
        amount: Number(amount),
        spending_deviation_score: Number(spendingDeviation),
        velocity_score: Number(velocityScore),
        geo_anomaly_score: Number(geoScore)
      }
    };

    const context = {
      amount: Number(amount),
      spending_deviation_score: Number(spendingDeviation),
      velocity_score: Number(velocityScore),
      geo_anomaly_score: Number(geoScore),
      merchant_category: merchantCategory,
      device_used: deviceUsed,
      transaction_type: transactionType,
      location,
      payment_channel: paymentChannel,
      receiver_account: receiverAccount,
      device_hash: deviceHash,
      ip_address: ipAddress,
      timestamp: new Date().toISOString()
    };

    setBusyAction('transaction');
    try {
      const res = await onSubmitTransaction({ ...payload, context }, context);
      onNotify?.(`I scored the transaction at ${Math.round(Number(res.risk) * 100)}% risk using the financial feature profile.`);
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  async function predictNlp() {
    setBusyAction('nlp');
    try {
      const res = await onSubmitNlp(nlpText);
      if (!res.ready) {
        onError?.(res.message || 'NLP model not available.');
        onRefreshReadiness?.();
        return;
      }
      onNotify?.(`I screened the message and classified it as ${res.verdict}.`);
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  async function predictCv() {
    setBusyAction('cv');
    try {
      const res = await onSubmitCv({
        image_path: cvPath,
        metadata: {
          suspicious: cvSuspicious,
          was_edited: cvEdited,
          source: cvSource
        }
      });
      onNotify?.(`I inspected the document and returned a ${Math.round(Number(res.fraud_score) * 100)}% fraud score in ${res.details.cv_mode} mode.`);
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  async function visualize() {
    setBusyAction('visualize');
    try {
      const res = await fetch('/api/analytics/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: vizPath || undefined,
          show_plot: false
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }

      const payload = await res.json();
      onNotify?.(`I saved the analytics chart to ${payload.saved_to}.`);
      onRefreshReadiness?.();
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  return (
    <div className="controls">
      <section className="control-section">
        <div className="control-section-header">
          <div>
            <strong>Transaction Risk Analysis</strong>
            <p className="control-copy">
              I use the strongest financial dataset features here so I can test unusual spending, high velocity, and geographic anomalies.
            </p>
          </div>
          <div className={`preview-pill preview-${preview.risk < 0.3 ? 'low' : preview.risk < 0.65 ? 'medium' : 'high'}`}>
            Predicted Risk: {Math.round(preview.risk * 100)}%
          </div>
        </div>

        <div className="control-grid two-up">
          <div className="row">
            <label>Amount</label>
            <input type="number" step="0.01" value={amount} onChange={(event) => setAmount(event.target.value)} />
          </div>
          <div className="row">
            <label>Merchant Category</label>
            <select value={merchantCategory} onChange={(event) => setMerchantCategory(event.target.value)}>
              {MERCHANT_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="control-grid two-up">
          <div className="row">
            <label>Transaction Type</label>
            <select value={transactionType} onChange={(event) => setTransactionType(event.target.value)}>
              {TRANSACTION_TYPE_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
          <div className="row">
            <label>Location</label>
            <select value={location} onChange={(event) => setLocation(event.target.value)}>
              {LOCATION_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="control-grid two-up">
          <div className="row">
            <label>Spending Deviation Score: <strong>{Number(spendingDeviation).toFixed(2)}</strong></label>
            <input type="range" min="-4" max="4" step="0.1" value={spendingDeviation} onChange={(event) => setSpendingDeviation(event.target.value)} />
          </div>
          <div className="row">
            <label>Velocity Score: <strong>{Number(velocityScore).toFixed(0)}</strong></label>
            <input type="range" min="1" max="20" step="1" value={velocityScore} onChange={(event) => setVelocityScore(event.target.value)} />
          </div>
        </div>

        <div className="control-grid two-up">
          <div className="row">
            <label>Geo Anomaly Score: <strong>{Number(geoScore).toFixed(2)}</strong></label>
            <input type="range" min="0" max="1" step="0.01" value={geoScore} onChange={(event) => setGeoScore(event.target.value)} />
          </div>
          <div className="row">
            <label>Device Used</label>
            <select value={deviceUsed} onChange={(event) => setDeviceUsed(event.target.value)}>
              {DEVICE_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="control-grid two-up">
          <div className="row">
            <label>Payment Channel</label>
            <select value={paymentChannel} onChange={(event) => setPaymentChannel(event.target.value)}>
              {PAYMENT_CHANNEL_OPTIONS.map((option) => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
          <div className="row">
            <label>Receiver Account</label>
            <input type="text" value={receiverAccount} onChange={(event) => setReceiverAccount(event.target.value)} />
          </div>
        </div>

        <div className="control-grid two-up">
          <div className="row">
            <label>Device Hash</label>
            <input type="text" value={deviceHash} onChange={(event) => setDeviceHash(event.target.value)} />
          </div>
          <div className="row">
            <label>IP Address</label>
            <input type="text" value={ipAddress} onChange={(event) => setIpAddress(event.target.value)} />
          </div>
        </div>

        <div className="inline-summary">
          <span className="mini-label">Preview Scenario</span>
          <strong>{preview.scenario}</strong>
        </div>

        <button onClick={predictTransaction} disabled={busyAction !== ''}>
          {busyAction === 'transaction' ? 'Running...' : 'Run Multimodal Risk Analysis'}
        </button>
      </section>

      <section className="control-section">
        <div className="control-section-header">
          <div>
            <strong>NLP Message Screening</strong>
            <p className="control-copy">
              I screen suspicious text here and highlight urgent or action-based language before I submit the message.
            </p>
          </div>
          <div className="preview-pill preview-medium">
            Live Keyword Scan
          </div>
        </div>

        <div className="row">
          <label>Message</label>
          <textarea
            value={nlpText}
            onChange={(event) => setNlpText(event.target.value)}
            rows="4"
            placeholder="Enter a message to check for phishing or spam language"
          />
        </div>

        <div className="highlight-box">
          {highlightedMessage.map((part, index) => (
            <span key={`${part.text}-${index}`} className={part.className}>{part.text}</span>
          ))}
        </div>

        <button onClick={predictNlp} disabled={busyAction !== ''}>
          {busyAction === 'nlp' ? 'Checking...' : 'Screen Message'}
        </button>
      </section>

      <section className="control-section">
        <div className="control-section-header">
          <div>
            <strong>CV Document Review</strong>
            <p className="control-copy">
              I pass a project image path into the backend CV route so I can test forged or suspicious document evidence.
            </p>
          </div>
          <div className="preview-pill preview-low">
            Image Evidence
          </div>
        </div>

        <div className="row">
          <label>Image Path</label>
          <input type="text" value={cvPath} onChange={(event) => setCvPath(event.target.value)} />
        </div>

        <div className="control-grid two-up">
          <label className="toggle-card">
            <input type="checkbox" checked={cvSuspicious} onChange={(event) => setCvSuspicious(event.target.checked)} />
            <span>I mark the document as suspicious context</span>
          </label>
          <label className="toggle-card">
            <input type="checkbox" checked={cvEdited} onChange={(event) => setCvEdited(event.target.checked)} />
            <span>I mark the document as edited</span>
          </label>
        </div>

        <div className="row">
          <label>Evidence Source</label>
          <select value={cvSource} onChange={(event) => setCvSource(event.target.value)}>
            <option value="internal">internal</option>
            <option value="external">external</option>
            <option value="unknown">unknown</option>
          </select>
        </div>

        <button onClick={predictCv} disabled={busyAction !== ''}>
          {busyAction === 'cv' ? 'Inspecting...' : 'Inspect Document Evidence'}
        </button>
      </section>

      <section className="control-section">
        <div className="control-section-header">
          <div>
            <strong>Risk Visualization</strong>
            <p className="control-copy">
              I use this tool to generate a chart from the transaction dataset so I can support my fraud interpretation with a saved visual.
            </p>
          </div>
          <div className="preview-pill preview-low">
            Analytics
          </div>
        </div>

        <div className="row">
          <label>CSV Path (optional)</label>
          <input
            type="text"
            placeholder="Leave empty to use the default analytics transaction dataset"
            value={vizPath}
            onChange={(event) => setVizPath(event.target.value)}
          />
        </div>

        <button onClick={visualize} disabled={busyAction !== ''}>
          {busyAction === 'visualize' ? 'Generating...' : 'Generate Risk Chart'}
        </button>
      </section>
    </div>
  );
}
