import { useState, useEffect } from 'react';

export default function TransactionTable() {
  // I keep dummy state here because this component looks like an earlier
  // prototype version of the transaction table UI.
  const [transactions, setTransactions] = useState([
    { id: 101, amount: 250, risk: 0.1 },
    { id: 102, amount: 1200, risk: 0.85 },
    { id: 103, amount: 60, risk: 0.05 }
  ]);

  // I compute summary metrics directly from the current rows so the numbers
  // always reflect the table contents without extra duplicated state.
  const total = transactions.length;
  const highRisk = transactions.filter(t => t.risk > 0.8).length;
  const avgRisk = (transactions.reduce((sum, t) => sum + t.risk, 0) / total).toFixed(2);

  return (
    <div>
      <h2>Live Transactions</h2>
      <p>Total: {total} | High Risk: {highRisk} | Avg Risk: {avgRisk}</p>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Amount</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map(t => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>{t.amount}</td>
              <td style={{ color: t.risk > 0.8 ? 'red' : 'black' }}>
                {t.risk}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
