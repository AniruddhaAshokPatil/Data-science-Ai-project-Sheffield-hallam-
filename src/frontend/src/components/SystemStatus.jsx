function formatLabel(key) {
  // I humanize readiness keys here so the dashboard can explain backend state
  // without showing raw API field names directly to operators.
  const customLabels = {
    transaction_api: 'Transaction API',
    analytics_dataset: 'Analytics Dataset',
    financial_raw_dataset: 'Financial Raw Dataset',
    outputs_directory: 'Outputs Directory',
    nlp_corpus: 'NLP Corpus',
    nlp_model: 'NLP Model',
    nlp_vectorizer: 'NLP Vectorizer',
    anomaly_model: 'Anomaly Model',
    anomaly_metadata: 'Anomaly Metadata',
    cv_model: 'CV Model',
    cv_inference_runtime: 'CV Inference Runtime'
  };

  if (customLabels[key]) {
    return customLabels[key];
  }

  return key
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export default function SystemStatus({ readiness, isLoading, error, onRefresh }) {
  const componentEntries = Object.entries(readiness?.components || {});

  return (
    <section className="panel system-panel">
      <div className="panel-header">
        <div>
          <h2>System Readiness</h2>
          <p className="panel-copy">
            I use this panel to confirm that my fraud detection services, saved models, and project datasets are available before I run live checks.
          </p>
        </div>
        <button className="ghost-button" type="button" onClick={onRefresh} disabled={isLoading}>
          {isLoading ? 'Refreshing...' : 'Refresh Readiness'}
        </button>
      </div>

      <div className="system-summary">
        <span className={`status-pill status-${readiness?.status || 'unknown'}`}>
          API: {readiness?.status || 'unknown'}
        </span>
        <span className="system-meta">
          Ready: {String(Boolean(readiness?.ready))}
        </span>
        <span className="system-meta">
          Version: {readiness?.version || 'n/a'}
        </span>
      </div>

      {error ? <p className="feedback error">{error}</p> : null}

      <div className="status-grid">
        {componentEntries.map(([key, component]) => (
          <article key={key} className="status-card">
            <div className="status-card-header">
              <strong>{formatLabel(key)}</strong>
              <span className={`status-pill status-${component.status}`}>{component.status}</span>
            </div>
            <p className="status-description">{component.name}</p>
            <p className="status-path">{component.path || component.reason || 'This component reports a live runtime status rather than a saved file path.'}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
