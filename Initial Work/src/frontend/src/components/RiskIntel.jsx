import React from 'react';

function toPercent(value) {
  // I convert 0 to 1 style scores into percentages here because percentages
  // are easier to read quickly during demos and reviews.
  return Math.round(Number(value || 0) * 100);
}

function getRiskBand(score) {
  // I use one helper for the score band so my color logic stays consistent
  // across the score ring, badges, and scenario panel.
  if (score < 0.3) {
    return 'low';
  }
  if (score < 0.65) {
    return 'medium';
  }
  return 'high';
}

function getConfidenceTone(label) {
  if (label === 'High') {
    return 'good';
  }
  if (label === 'Low') {
    return 'warn';
  }
  return 'neutral';
}

export default function RiskIntel({
  analysis,
  latestTransaction,
  latestNlpResult,
  latestCvResult,
  onConfirmFraud,
  onMarkSafe
}) {
  const scorePercent = toPercent(analysis?.finalScore);
  const previewPercent = toPercent(analysis?.preview?.risk);
  const riskBand = getRiskBand(Number(analysis?.finalScore || 0));
  const confidenceTone = getConfidenceTone(analysis?.confidence);

  const ringStyle = {
    background: `conic-gradient(var(--ring-${riskBand}) ${scorePercent}%, rgba(148, 163, 184, 0.12) 0%)`
  };

  const contributions = [
    { label: 'Transaction Risk', value: analysis?.transactionScore, tone: 'high' },
    { label: 'NLP Risk', value: analysis?.nlpScore, tone: 'medium' },
    { label: 'CV Risk', value: analysis?.cvScore, tone: 'neutral' }
  ];

  return (
    <div className="risk-panel-body">
      <section className="score-hero">
        <div>
          <p className="eyebrow">Calibrated Multimodal Risk</p>
          <h2 className="hero-title">Risk Intelligence Overview</h2>
          <p className="hero-copy">
            I bring the latest transaction, text, and document signals together here so I can explain one decision clearly.
          </p>
        </div>

        <div className="score-ring-wrap">
          <div className="score-ring" style={ringStyle}>
            <div className="score-ring-inner">
              <strong>{scorePercent}%</strong>
              <span>Final Risk</span>
            </div>
          </div>
        </div>
      </section>

      <div className="intel-grid">
        <article className="intel-card">
          <div className="intel-card-header">
            <h3>Confidence</h3>
            <span className={`chip chip-${confidenceTone}`}>{analysis?.confidence || 'Medium'}</span>
          </div>
          <p className="intel-copy">
            I estimate confidence from how closely the available model scores agree with each other.
          </p>
          <p className="metric-line">Preview Risk: <strong>{previewPercent}%</strong></p>
          <p className="metric-line">Final Risk: <strong>{scorePercent}%</strong></p>
        </article>

        <article className="intel-card">
          <div className="intel-card-header">
            <h3>Scenario</h3>
            <span className={`chip chip-${riskBand}`}>{analysis?.scenario || 'Normal Behaviour'}</span>
          </div>
          <p className="intel-copy">
            I classify the current case by combining the strongest behavioural and message clues I have.
          </p>
          <p className="metric-line">Latest Profile: <strong>{latestTransaction?.profile || 'pending'}</strong></p>
          <p className="metric-line">Verdict: <strong>{analysis?.transactionVerdict || 'PENDING'}</strong></p>
          <p className="metric-line">Threshold: <strong>{latestTransaction?.details?.threshold ?? 0.65}</strong></p>
        </article>
      </div>

      <article className="panel-surface">
        <div className="intel-card-header">
          <h3>Modal Contribution Breakdown</h3>
          <span className="chip chip-neutral">Explainability</span>
        </div>
        <div className="bar-group">
          {contributions.map((item) => (
            <div key={item.label} className="bar-row">
              <div className="bar-meta">
                <span>{item.label}</span>
                <strong>{item.value == null ? 'No data yet' : `${toPercent(item.value)}%`}</strong>
              </div>
              <div className="bar-track">
                <div
                  className={`bar-fill bar-fill-${item.tone}`}
                  style={{ width: `${toPercent(item.value || 0)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </article>

      <article className="panel-surface">
        <div className="intel-card-header">
          <h3>Natural Language Explanation</h3>
          <span className="chip chip-neutral">Narrative</span>
        </div>
        <p className="explanation-copy">
          {analysis?.explanation || 'I will explain the current risk case here after I receive at least one fraud signal.'}
        </p>
        <div className="explanation-list">
          {(analysis?.transactionExplanations || []).slice(0, 3).map((line, index) => (
            <p key={`tx-explanation-${index}`} className="explanation-bullet">{line}</p>
          ))}
        </div>
      </article>

      <article className="panel-surface">
        <div className="intel-card-header">
          <h3>Analyst Review Loop</h3>
          <span className="chip chip-neutral">Human Feedback</span>
        </div>
        <p className="intel-copy">
          I use these buttons to capture an analyst decision after reviewing the multimodal evidence on screen.
        </p>
        <div className="feedback-actions">
          <button type="button" className="secondary-action" onClick={onConfirmFraud}>
            Confirm Fraud
          </button>
          <button type="button" className="secondary-action safe-action" onClick={onMarkSafe}>
            Mark as Safe
          </button>
        </div>
      </article>

      <article className="panel-surface">
        <div className="intel-card-header">
          <h3>Latest Modal Outputs</h3>
          <span className="chip chip-neutral">Evidence</span>
        </div>
        <div className="source-grid">
          <div className="source-card">
            <span className="source-label">Transaction</span>
            <strong>{latestTransaction ? `${toPercent(latestTransaction.risk)}% risk` : 'No transaction scored yet'}</strong>
            <span className="source-copy">{analysis?.transactionExplanations?.[0] || 'I will explain transaction evidence here after scoring.'}</span>
          </div>
          <div className="source-card">
            <span className="source-label">NLP</span>
            <strong>{latestNlpResult ? latestNlpResult.verdict : 'No message screened yet'}</strong>
            <span className="source-copy">{analysis?.nlpExplanations?.[0] || 'I will explain message evidence here after screening.'}</span>
          </div>
          <div className="source-card">
            <span className="source-label">CV</span>
            <strong>{latestCvResult ? latestCvResult.verdict : 'No document checked yet'}</strong>
            <span className="source-copy">{analysis?.cvExplanations?.[0] || 'I will explain document evidence here after inspection.'}</span>
          </div>
        </div>
      </article>
    </div>
  );
}
