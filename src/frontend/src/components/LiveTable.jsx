function fmt(num) {
  if (typeof num !== 'number') return '-';
  return Number(num).toFixed(3);
}

export default function LiveTable({ rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Timestamp (UTC)</th>
            <th>Risk</th>
            <th>Tabular Prob</th>
            <th>Ratio (norm)</th>
            <th>Dist (norm)</th>
            <th>Threshold</th>
          </tr>
        </thead>
        <tbody>
          {(rows || []).map((r, idx) => {
            const risk = r?.risk ?? r?.combined_risk ?? 0;
            const high = risk >= 0.65;
            return (
              <tr key={idx} className={high ? 'high' : ''}>
                <td>{r?.timestamp || '-'}</td>
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

