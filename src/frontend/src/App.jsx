import { useEffect, useMemo, useState } from 'react';
import Header from './components/Header.jsx';
import LiveTable from './components/LiveTable.jsx';
import Controls from './components/Controls.jsx';
import RiskBadge from './components/RiskBadge.jsx';
import SystemStatus from './components/SystemStatus.jsx';
import useWebSocket from './hooks/useWebSocket.js';
import { api } from './services/api.js';

function getWebSocketUrl() {
  // I derive the live URL from the current page by default so deployed builds
  // can connect without hardcoding localhost-specific values.
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }

  if (typeof window === 'undefined') {
    return '';
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws/transactions`;
}

export default function App() {
  // I keep transactions in state because the dashboard needs to re-render
  // whenever new scored transactions arrive from HTTP or WebSocket flows.
  const [transactions, setTransactions] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [readiness, setReadiness] = useState(null);
  const [readinessLoading, setReadinessLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [notice, setNotice] = useState('');

  // WebSocket listener: pushes incoming messages to the live table
  const { status, lastMessage, lastError } = useWebSocket(getWebSocketUrl());

  async function loadReadiness() {
    setReadinessLoading(true);
    try {
      const payload = await api.get('/health/ready');
      setReadiness(payload);
      setApiError('');
    } catch (error) {
      setApiError(error.message);
    } finally {
      setReadinessLoading(false);
    }
  }

  useEffect(() => {
    // I mirror the hook status into a simpler boolean because the Header only
    // needs to know whether the socket is connected or not.
    setWsConnected(status === 'open');
  }, [status]);

  useEffect(() => {
    loadReadiness();
  }, []);

  useEffect(() => {
    if (!lastMessage) return;

    // I parse the incoming WebSocket message here because the dashboard stores
    // transaction results as JavaScript objects, not raw socket events.
    try {
      const parsed = typeof lastMessage === 'string' ? JSON.parse(lastMessage) : lastMessage;
      setTransactions((prev) => [parsed, ...prev].slice(0, 500));
    } catch {
      // If backend already sent JSON (not string), accept it as-is
      if (typeof lastMessage === 'object') {
        setTransactions((prev) => [lastMessage, ...prev].slice(0, 500));
      }
    }
  }, [lastMessage]);

  useEffect(() => {
    if (lastError) {
      setApiError(lastError);
    }
  }, [lastError]);

  // I derive summary numbers from the transaction list so the badges always
  // stay in sync with the live table without storing duplicate state.
  const summary = useMemo(() => {
    const total = transactions.length;
    const highRisk = transactions.filter((t) => (t?.risk ?? 0) >= 0.65).length;
    const avgRisk = total ? (transactions.reduce((s, t) => s + (t?.risk ?? 0), 0) / total) : 0;
    return { total, highRisk, avgRisk: Number(avgRisk.toFixed(3)) };
  }, [transactions]);

  // I keep one helper for transaction submission so Controls can trigger a
  // backend score request and the dashboard can store the returned result.
  async function sendTransaction(payload) {
    try {
      const res = await api.post('/transaction/predict', payload);
      setTransactions((prev) => [res, ...prev].slice(0, 500));
      setApiError('');
      return res;
    } catch (error) {
      setApiError(error.message);
      throw error;
    }
  }

  return (
    <div className="layout">
      <Header wsConnected={wsConnected} apiStatus={readiness?.status} />

      <main className="content">
        <section className="left">
          <SystemStatus
            readiness={readiness}
            isLoading={readinessLoading}
            error={apiError}
            onRefresh={loadReadiness}
          />

          <div className="panel">
            <div className="panel-header">
              <h2>Live Transaction Results</h2>
              <div className="badges">
                <RiskBadge label="Transactions" value={summary.total} color="#64748b" />
                <RiskBadge label="High-Risk Cases" value={summary.highRisk} color="#ef4444" />
                <RiskBadge label="Average Risk" value={summary.avgRisk} color="#22c55e" />
              </div>
            </div>
            {notice ? <p className="feedback success">{notice}</p> : null}
            <LiveTable rows={transactions} />
          </div>
        </section>

        <section className="right">
          <div className="panel">
            <div className="panel-header">
              <h2>Fraud Testing Controls</h2>
            </div>
            <Controls
              onSubmitTransaction={sendTransaction}
              onNotify={setNotice}
              onError={setApiError}
              onRefreshReadiness={loadReadiness}
            />
          </div>
        </section>
      </main>
    </div>
  );
}
