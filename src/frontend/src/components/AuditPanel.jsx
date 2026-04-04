import React from 'react';

function formatRisk(value) {
  // I format audit numbers in one place so the table and timeline stay neat.
  if (typeof value !== 'number') {
    return '-';
  }
  return value.toFixed(3);
}

function getBurstFlag(currentRow, previousRow) {
  // I mark bursts when transactions arrive close together because that can be
  // a useful fraud clue in the audit timeline.
  if (!currentRow?.timestamp || !previousRow?.timestamp) {
    return false;
  }

  const currentTime = new Date(currentRow.timestamp).getTime();
  const previousTime = new Date(previousRow.timestamp).getTime();
  const secondsApart = Math.abs(currentTime - previousTime) / 1000;
  return secondsApart < 60;
}

export default function AuditPanel({ contributionRows, transactions, feedbackLog }) {
  const recentRows = (transactions || []).slice(0, 8);

  return (
    <div className="audit-layout">
      <section className="audit-section">
        <div className="audit-header">
          <h3>Feature Attribution</h3>
          <p>
            I break the latest decision into feature-level signals here so I can explain which inputs increased or reduced risk.
          </p>
        </div>
        <div className="audit-table-wrap">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Feature</th>
                <th>Value</th>
                <th>Contribution</th>
                <th>Effect</th>
              </tr>
            </thead>
            <tbody>
              {contributionRows?.length ? contributionRows.map((row) => (
                <tr key={row.feature}>
                  <td>{row.feature}</td>
                  <td>{row.value ?? '-'}</td>
                  <td>{row.contribution}</td>
                  <td>
                    <span className={`audit-effect ${row.effect === 'Risk increasing' ? 'audit-effect-up' : 'audit-effect-down'}`}>
                      {row.effect}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="4" className="audit-empty">
                    I will show feature attribution here after I run transaction, NLP, or CV checks.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="audit-section">
        <div className="audit-header">
          <h3>Temporal Insight</h3>
          <p>
            I show the latest transaction rhythm here so I can spot fast bursts and repeated suspicious activity.
          </p>
        </div>
        <div className="timeline-list">
          {recentRows.length ? recentRows.map((row, index) => {
            const burst = getBurstFlag(row, recentRows[index + 1]);
            const width = `${Math.max(8, Math.round((row.risk || 0) * 100))}%`;
            return (
              <div key={`${row.timestamp || 'row'}-${index}`} className="timeline-row">
                <div className="timeline-meta">
                  <strong>{row.profile || 'unknown'}</strong>
                  <span>{row.timestamp || 'pending timestamp'}</span>
                </div>
                <div className="timeline-bar-track">
                  <div className={`timeline-bar ${burst ? 'timeline-bar-burst' : ''}`} style={{ width }} />
                </div>
                <div className="timeline-side">
                  <strong>{formatRisk(row.risk)}</strong>
                  <span>{burst ? 'Burst < 60s' : 'Normal gap'}</span>
                </div>
              </div>
            );
          }) : (
            <p className="audit-empty-copy">
              I will populate this timeline after I send transactions through the API or receive WebSocket updates.
            </p>
          )}
        </div>
      </section>

      <section className="audit-section">
        <div className="audit-header">
          <h3>Recent Results</h3>
          <p>
            I keep the latest scored cases here so I can compare how recent transaction profiles behaved over time.
          </p>
        </div>
        <div className="audit-table-wrap">
          <table className="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Profile</th>
                <th>Risk</th>
                <th>Threshold</th>
              </tr>
            </thead>
            <tbody>
              {recentRows.length ? recentRows.map((row, index) => (
                <tr key={`${row.timestamp || 'recent'}-${index}`}>
                  <td>{row.timestamp || '-'}</td>
                  <td>{row.profile || '-'}</td>
                  <td>{formatRisk(row.risk)}</td>
                  <td>{formatRisk(row?.details?.threshold)}</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="4" className="audit-empty">
                    I will list recent transaction outputs here after the dashboard receives results.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="audit-section">
        <div className="audit-header">
          <h3>Analyst Feedback Log</h3>
          <p>
            I use this review trail to remember whether a human analyst confirmed fraud or marked a case as safe.
          </p>
        </div>
        <div className="feedback-log">
          {feedbackLog?.length ? feedbackLog.map((entry, index) => (
            <article key={`${entry.timestamp}-${index}`} className="feedback-entry">
              <strong>{entry.label}</strong>
              <span>{entry.scenario}</span>
              <span>Score: {entry.score}</span>
              <span>{entry.timestamp}</span>
            </article>
          )) : (
            <p className="audit-empty-copy">
              I will show analyst review decisions here after I use the feedback buttons in the risk panel.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
