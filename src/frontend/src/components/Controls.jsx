import { useState } from 'react';
import { api } from '../services/api.js';

export default function Controls({ onSubmitTransaction, onNotify, onError, onRefreshReadiness }) {
  // I keep each form input in its own state value because I want the dashboard
  // controls to behave like controlled React inputs.
  const [ratio, setRatio] = useState(3.2);
  const [dist, setDist] = useState(420);
  const [amount, setAmount] = useState(500.5);

  const [nlpText, setNlpText] = useState(
    'URGENT: Your account has been suspended. Click here now.'
  );

  const [vizPath, setVizPath] = useState('');
  const [busyAction, setBusyAction] = useState('');

  async function predictTransaction() {
    // I build the payload explicitly here so it matches the backend transaction
    // route schema instead of relying on form field names by accident.
    const payload = {
      features: {
        ratio_to_median_purchase_price: Number(ratio),
        distance_from_home: Number(dist),
        transaction_amount: Number(amount)
      }
    };
    setBusyAction('transaction');
    try {
      const res = onSubmitTransaction
        ? await onSubmitTransaction(payload)
        : await api.post('/transaction/predict', payload);
      onNotify?.(`I scored the transaction with a risk value of ${Number(res.risk).toFixed(3)} under the ${res.profile} profile.`);
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  async function predictNlp() {
    // I call the NLP route directly here because this panel lets me test the
    // spam-detection part of the project from the frontend.
    setBusyAction('nlp');
    try {
      const res = await api.post('/nlp/predict', { message: nlpText });
      if (!res.ready) {
        onError?.(res.message || 'NLP model not available.');
        onRefreshReadiness?.();
        return;
      }
      onNotify?.(`I classified the message as ${res.verdict}.`);
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  async function visualize() {
    // I call the analytics route here because the frontend should be able to
    // trigger backend chart generation without leaving the dashboard.
    setBusyAction('visualize');
    try {
      const res = await api.post('/analytics/visualize', {
        path: vizPath || undefined,
        show_plot: false
      });
      onNotify?.(`I saved the analytics chart to ${res.saved_to}.`);
      onRefreshReadiness?.();
    } catch (error) {
      onError?.(error.message);
    } finally {
      setBusyAction('');
    }
  }

  return (
    <div className="controls">
      {/* I group controls by feature area so transaction scoring, analytics,
          and NLP testing each feel like separate dashboard actions. */}
      <div className="row">
        <strong>▶ Transaction Risk Check</strong>
        <span className="control-copy">
          I use these fields to test a card-style transaction and send it to the backend fraud scoring route.
        </span>
      </div>
      <div className="group">
        <div className="row">
          <label>Purchase ratio to normal spending</label>
          <input type="number" step="0.1" value={ratio} onChange={(e) => setRatio(e.target.value)} />
        </div>
        <div className="row">
          <label>Distance from home</label>
          <input type="number" step="1" value={dist} onChange={(e) => setDist(e.target.value)} />
        </div>
      </div>
      <div className="row">
        <label>Reference amount</label>
        <input type="number" step="0.1" value={amount} onChange={(e) => setAmount(e.target.value)} />
      </div>
      <div className="row">
        <button onClick={predictTransaction} disabled={busyAction !== ''}>
          {busyAction === 'transaction' ? 'Scoring...' : 'Check Transaction Risk'}
        </button>
      </div>

      <hr style={{ borderColor: '#1f2937' }} />

      <div className="row">
        <strong>▶ Risk Visualization</strong>
        <span className="control-copy">
          I use this tool to generate a fraud visual from the default analytics dataset or from a CSV path that I provide.
        </span>
      </div>
      <div className="row">
        <label>CSV path (optional)</label>
        <input
          type="text"
          placeholder="Leave empty to use the default analytics transaction dataset"
          value={vizPath}
          onChange={(e) => setVizPath(e.target.value)}
        />
      </div>
      <div className="row">
        <button onClick={visualize} disabled={busyAction !== ''}>
          {busyAction === 'visualize' ? 'Generating...' : 'Generate Risk Chart'}
        </button>
      </div>

      <hr style={{ borderColor: '#1f2937' }} />

      <div className="row">
        <strong>▶ NLP Message Screening</strong>
        <span className="control-copy">
          I use this form to test whether a message looks like normal communication or suspicious spam content.
        </span>
      </div>
      <div className="row">
        <label>Message</label>
        <textarea
          value={nlpText}
          onChange={(e) => setNlpText(e.target.value)}
          rows="3"
          placeholder="Enter a message to check for spam or phishing language"
        />
      </div>
      <div className="row">
        <button onClick={predictNlp} disabled={busyAction !== ''}>
          {busyAction === 'nlp' ? 'Checking...' : 'Screen Message'}
        </button>
      </div>
    </div>
  );
}
