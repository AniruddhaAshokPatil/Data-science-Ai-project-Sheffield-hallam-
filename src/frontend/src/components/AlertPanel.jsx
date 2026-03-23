import { useState } from 'react';

export default function AlertPanel() {
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