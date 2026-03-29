import { useState } from 'react';

export default function AlertPanel() {
  // I keep alerts in state here because this component is meant to represent
  // a list that could later grow or update as new fraud warnings arrive.
  const [alerts, setAlerts] = useState([
    { id: 102, message: 'High-risk transaction detected!' }
  ]);

  return (
    <div>
      <h2>Fraud Alerts</h2>
      <ul>
        {alerts.map(a => (
          <li key={a.id}>
            🚨 {a.message} (ID: {a.id})
          </li>
        ))}
      </ul>
    </div>
  );
}
