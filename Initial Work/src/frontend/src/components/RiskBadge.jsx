export default function RiskBadge({ label, value, color = '#3b82f6' }) {
  // I build the style object here because each badge can use a different color
  // while still sharing the same badge component structure.
  const style = { borderColor: color, color };
  return (
    <span className="badge" style={style}>
      {label}: {String(value)}
    </span>
  );
}
