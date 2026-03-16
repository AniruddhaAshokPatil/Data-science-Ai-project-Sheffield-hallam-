import { useState } from 'react';
import { api } from '../services/api.js';

export default function Controls({ onTestOne }) {
  const [ratio, setRatio] = useState(3.2);
  const [dist, setDist] = useState(420);
  const [amount, setAmount] = useState(500.5);

  const [nlpText, setNlpText] = useState(
    'URGENT: Your account has been suspended. Click here now.'
  );

  const [vizPath, setVizPath] = useState('');

  async function predictTransaction() {
    const payload = {
      features: {
        ratio_to_median_purchase_price: Number(ratio),
        distance_from_home: Number(dist),
        transaction_amount: Number(amount)
      }
    };
    const res = await api.post('/transaction/predict', payload);
    // Surface a tiny confirmation; the App will also push it into the table if onTestOne provided
    alert(`Transaction risk: ${Number(res.risk).toFixed(3)}`);
    if (onTestOne) onTestOne(); // optional: trigger a refresh insert
  }

  async function predictNlp() {
    const res = await api.post('/nlp/predict', { message: nlpText });
    if (!res.ready) {
      alert(res.message || 'NLP model not available.');
      return;
    }
    alert(`NLP verdict: ${res.verdict}`);
  }

  async function visualize() {
    const res = await api.post('/analytics/visualize', {
      path: vizPath || undefined,
      show_plot: false
    });
    alert(`Chart saved to: ${res.saved_to}`);
  }

  return (
    <div className="controls">
      <div className="row">
        <strong>▶ Quick Transaction Test</strong>
      </div>
      <div className="group">
        <div className="row">
          <label>ratio_to_median_purchase_price</label>
          <input type="number" step="0.1" value={ratio} onChange={(e) => setRatio(e.target.value)} />
        </div>
        <div className="row">
          <label>distance_from_home</label>
          <input type="number" step="1" value={dist} onChange={(e) => setDist(e.target.value)} />
        </div>
      </div>
      <div className="row">
        <label>transaction_amount</label>
        <input type="number" step="0.1" value={amount} onChange={(e) => setAmount(e.target.value)} />
      </div>
      <div className="row">
        <button onClick={predictTransaction}>Send Transaction</button>
      </div>

      <hr style={{ borderColor: '#1f2937' }} />

      <div className="row">
  <strong>▶ Generate Risk Visualization</strong>
</div>
<div className="row">
  <label>CSV path (optional)</label>
  <input
    type="text"
    placeholder="Leave empty to use default card_transdata.csv"
    value={vizPath}
    onChange={(e) => setVizPath(e.target.value)}
  />
</div>
<div className="row">
  <button onClick={visualize}>Generate Chart</button>
</div>

      <hr style={{ borderColor: '#1f2937' }} />

      <div className="row">
        <strong>▶ NLP Spam Detection</strong>
      </div>
      <div className="row">
        <label>Message</label>
        <textarea
          value={nlpText}
          onChange={(e) => setNlpText(e.target.value)}
          rows="3"
          placeholder="Enter message to check for spam"
        />
      </div>
      <div className="row">
        <button onClick={predictNlp}>Check Message</button>
      </div>
    </div>
  );
}