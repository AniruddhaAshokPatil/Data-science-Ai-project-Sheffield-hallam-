import { useEffect, useMemo, useState } from 'react';
import Header from './components/Header.jsx';
import LiveTable from './components/LiveTable.jsx';
import Controls from './components/Controls.jsx';
import RiskBadge from './components/RiskBadge.jsx';
import useWebSocket from './hooks/useWebSocket.js';
import { api } from './services/api.js';

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  // WebSocket listener: pushes incoming messages to the live table
  const { status, lastMessage } = useWebSocket(import.meta.env.VITE_WS_URL);

  useEffect(() => {
    setWsConnected(status === 'open');
  }, [status]);

  useEffect(() => {
    if (!lastMessage) return;

    // Expecting messages shaped like:
    // { risk: number, details: {...}, timestamp: "..." , ... }
    try {
      const parsed = JSON.parse(lastMessage.data || lastMessage);
      setTransactions((prev) => [parsed, ...prev].slice(0, 500));
    } catch {
      // If backend already sent JSON (not string), accept it as-is
      if (typeof lastMessage === 'object') {
        setTransactions((prev) => [lastMessage, ...prev].slice(0, 500));
      }
    }
  }, [lastMessage]);

  // Counters
  const summary = useMemo(() => {
    const total = transactions.length;
    const highRisk = transactions.filter((t) => (t?.risk ?? 0) >= 0.65).length;
    const avgRisk = total ? (transactions.reduce((s, t) => s + (t?.risk ?? 0), 0) / total) : 0;
    return { total, highRisk, avgRisk: Number(avgRisk.toFixed(3)) };
  }, [transactions]);

  // Manual test: call /transaction/predict with a small feature dict
  async function testOne() {
    const payload = {
      features: {
        ratio_to_median_purchase_price: 3.2,
        distance_from_home: 420,
        transaction_amount: 500.5
      }
    };
    const res = await api.post('/transaction/predict', payload);
    // Push into the table for visibility
    setTransactions((prev) => [res, ...prev].slice(0, 500));
  }

  return (
    <div className="layout">
      <Header wsConnected={wsConnected} />

      <main className="content">
        <section className="left">
          <div className="panel">
            <div className="panel-header">
              <h2>Live Transactions</h2>
              <div className="badges">
                <RiskBadge label="Total" value={summary.total} color="#64748b" />
                <RiskBadge label="High Risk" value={summary.highRisk} color="#ef4444" />
                <RiskBadge label="Avg Risk" value={summary.avgRisk} color="#22c55e" />
              </div>
            </div>
            <LiveTable rows={transactions} />
          </div>
        </section>

        <section className="right">
          <div className="panel">
            <div className="panel-header">
              <h2>Controls</h2>
            </div>
            <Controls onTestOne={testOne} />
          </div>
        </section>
      </main>
    </div>
  );
}

