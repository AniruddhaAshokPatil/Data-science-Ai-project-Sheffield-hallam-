function fmt(num) {
  // I format numbers in one helper so the table stays neat and every risk
  // value is displayed with the same number of decimal places.
  if (typeof num !== 'number') return '-';
  return Number(num).toFixed(3);
}

export default function LiveTable({ rows }) {
  if (!rows?.length) {
    return (
      <div className="empty-state">
        <strong>No transactions yet.</strong>
        <p>I will show scored results here as soon as the API or WebSocket stream sends them.</p>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Timestamp (UTC)</th>
            <th>Profile</th>
            <th>Risk</th>
            <th>Tabular Prob</th>
            <th>Ratio (norm)</th>
            <th>Dist (norm)</th>
            <th>Threshold</th>
          </tr>
        </thead>
        <tbody>
          {(rows || []).map((r, idx) => {
            // I compute these display values inside the loop because the table
            // may receive slightly different result shapes over time.
            const risk = r?.risk ?? r?.combined_risk ?? 0;
            const high = risk >= 0.65;
            return (
              <tr key={idx} className={high ? 'high' : ''}>
                <td>{r?.timestamp || '-'}</td>
                <td>{r?.profile || '-'}</td>
                <td>{fmt(risk)}</td>
                <td>{fmt(r?.details?.tabular_prob)}</td>
                <td>{fmt(r?.details?.ratio_norm)}</td>
                <td>{fmt(r?.details?.dist_norm)}</td>
                <td>{fmt(r?.details?.threshold)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
