export default function RiskBadge({ label, value, color = '#3b82f6' }) {
  const style = { borderColor: color, color };
  return (
    <span className="badge" style={style}>
      {label}: {String(value)}
    </span>
  );
}

