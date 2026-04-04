import React, { useEffect, useMemo, useState } from 'react';
import Header from './components/Header.jsx';
import Controls from './components/Controls.jsx';
import SystemStatus from './components/SystemStatus.jsx';
import RiskIntel from './components/RiskIntel.jsx';
import AuditPanel from './components/AuditPanel.jsx';
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
  const [previewRisk, setPreviewRisk] = useState(null);
  const [latestTransactionContext, setLatestTransactionContext] = useState(null);
  const [latestNlpResult, setLatestNlpResult] = useState(null);
  const [latestCvResult, setLatestCvResult] = useState(null);
  const [feedbackLog, setFeedbackLog] = useState([]);

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

  const latestTransaction = transactions[0] || null;

  function buildScenario(transactionScore, nlpScore, cvScore, transactionContext) {
    // I classify the likely scenario here so the right-hand panel can explain
    // the most plausible fraud story from the available signals.
    const amount = Number(transactionContext?.amount ?? 0);
    const velocity = Number(transactionContext?.velocity_score ?? 0);
    const geo = Number(transactionContext?.geo_anomaly_score ?? 0);
    const merchant = String(transactionContext?.merchant_category || '').toLowerCase();
    const device = String(transactionContext?.device_used || '').toLowerCase();

    if ((transactionScore ?? 0) >= 0.65 && (nlpScore ?? 0) >= 0.7) {
      return 'Account Takeover';
    }
    if ((transactionScore ?? 0) >= 0.6 && merchant === 'online' && device === 'web') {
      return 'Card Not Present Fraud';
    }
    if ((transactionScore ?? 0) >= 0.45 && amount <= 50 && velocity >= 14) {
      return 'Card Testing';
    }
    if ((cvScore ?? 0) >= 0.6) {
      return 'Document Review Needed';
    }
    if ((transactionScore ?? 0) >= 0.55 && geo >= 0.7) {
      return 'Geographic Anomaly';
    }
    return 'Normal Behaviour';
  }

  function buildConfidenceLabel(scores) {
    // I use score disagreement here because large disagreement means the
    // available models do not tell the same story with equal strength.
    const availableScores = scores.filter((value) => typeof value === 'number');
    if (availableScores.length <= 1) {
      return 'Medium';
    }

    const spread = Math.max(...availableScores) - Math.min(...availableScores);
    if (spread <= 0.15) {
      return 'High';
    }
    if (spread <= 0.35) {
      return 'Medium';
    }
    return 'Low';
  }

  function buildExplanation({ finalScore, transactionScore, nlpScore, cvScore, transactionContext, nlpResult, cvResult, scenario }) {
    // I build one plain-language summary here so the dashboard can explain the
    // current decision in a way that is easier to present than raw numbers.
    const reasons = [];

    if ((transactionScore ?? 0) >= 0.55) {
      const geo = Number(transactionContext?.geo_anomaly_score ?? 0);
      const velocity = Number(transactionContext?.velocity_score ?? 0);
      const spending = Math.abs(Number(transactionContext?.spending_deviation_score ?? 0));

      if (velocity >= 12) {
        reasons.push('rapid transaction velocity');
      }
      if (geo >= 0.6) {
        reasons.push('unusual geography');
      }
      if (spending >= 1.2) {
        reasons.push('spending behaviour that differs from the normal pattern');
      }
      if (!reasons.length) {
        reasons.push('the transaction behaviour looks unusual');
      }
    }

    if ((nlpScore ?? 0) >= 0.7 && nlpResult?.verdict === 'SPAM') {
      reasons.push('phishing or spam language in the linked message');
    }

    if ((cvScore ?? 0) >= 0.6 && cvResult?.verdict) {
      reasons.push('document evidence that needs closer review');
    }

    if (!reasons.length && finalScore < 0.3) {
      return 'I assess this case as lower risk because the current transaction, message, and document signals do not show strong suspicious behaviour.';
    }

    return `I assess this case as ${scenario.toLowerCase()} because I can see ${reasons.join(', ')}.`;
  }

  const analysis = useMemo(() => {
    // I derive the full interpretation object here so every panel can read
    // from one shared multimodal summary instead of rebuilding logic separately.
    const transactionScore = typeof latestTransaction?.risk === 'number' ? latestTransaction.risk : null;
    const nlpScore = latestNlpResult
      ? (latestNlpResult.prediction === 1 ? 0.91 : 0.08)
      : null;
    const cvScore = typeof latestCvResult?.fraud_score === 'number' ? latestCvResult.fraud_score : null;

    const weightedScores = [];
    if (transactionScore !== null) weightedScores.push({ value: transactionScore, weight: 0.55 });
    if (nlpScore !== null) weightedScores.push({ value: nlpScore, weight: 0.20 });
    if (cvScore !== null) weightedScores.push({ value: cvScore, weight: 0.25 });

    const totalWeight = weightedScores.reduce((sum, item) => sum + item.weight, 0);
    const finalScore = totalWeight
      ? weightedScores.reduce((sum, item) => sum + (item.value * item.weight), 0) / totalWeight
      : Number(previewRisk?.risk ?? 0);

    const scenario = latestTransaction?.scenario || buildScenario(transactionScore, nlpScore, cvScore, latestTransactionContext);
    const confidence = buildConfidenceLabel([transactionScore, nlpScore, cvScore]);
    const explanation = latestTransaction?.explanations?.[0] || buildExplanation({
      finalScore,
      transactionScore,
      nlpScore,
      cvScore,
      transactionContext: latestTransactionContext,
      nlpResult: latestNlpResult,
      cvResult: latestCvResult,
      scenario
    });

    const contributionRows = [];
    if (latestTransaction?.feature_importance?.length) {
      for (const item of latestTransaction.feature_importance) {
        contributionRows.push({
          feature: item.feature,
          value: item.value ?? '-',
          contribution: Number(item.contribution ?? 0).toFixed(3),
          effect: item.effect ?? 'Risk increasing'
        });
      }
    } else if (latestTransactionContext) {
      const amountNorm = Math.max(0, Math.min(1, Number(latestTransactionContext.amount ?? 0) / 1500));
      const spendingNorm = Math.max(0, Math.min(1, Math.abs(Number(latestTransactionContext.spending_deviation_score ?? 0)) / 3));
      const velocityNorm = Math.max(0, Math.min(1, Number(latestTransactionContext.velocity_score ?? 0) / 20));
      const geoNorm = Math.max(0, Math.min(1, Number(latestTransactionContext.geo_anomaly_score ?? 0)));

      contributionRows.push(
        {
          feature: 'amount',
          value: Number(latestTransactionContext.amount ?? 0).toFixed(2),
          contribution: (amountNorm * 0.18).toFixed(3),
          effect: amountNorm >= 0.45 ? 'Risk increasing' : 'Risk reducing'
        },
        {
          feature: 'spending_deviation_score',
          value: Number(latestTransactionContext.spending_deviation_score ?? 0).toFixed(2),
          contribution: (spendingNorm * 0.15).toFixed(3),
          effect: spendingNorm >= 0.45 ? 'Risk increasing' : 'Risk reducing'
        },
        {
          feature: 'velocity_score',
          value: Number(latestTransactionContext.velocity_score ?? 0).toFixed(2),
          contribution: (velocityNorm * 0.15).toFixed(3),
          effect: velocityNorm >= 0.5 ? 'Risk increasing' : 'Risk reducing'
        },
        {
          feature: 'geo_anomaly_score',
          value: Number(latestTransactionContext.geo_anomaly_score ?? 0).toFixed(2),
          contribution: (geoNorm * 0.12).toFixed(3),
          effect: geoNorm >= 0.5 ? 'Risk increasing' : 'Risk reducing'
        }
      );
    }

    if (latestNlpResult) {
      contributionRows.push({
        feature: 'message_signal',
        value: latestNlpResult.verdict,
        contribution: (nlpScore ?? 0).toFixed(3),
        effect: latestNlpResult.prediction === 1 ? 'Risk increasing' : 'Risk reducing'
      });
    }

    if (latestCvResult) {
      contributionRows.push({
        feature: 'cv_document_signal',
        value: latestCvResult.verdict,
        contribution: Number(latestCvResult.fraud_score ?? 0).toFixed(3),
        effect: Number(latestCvResult.fraud_score ?? 0) >= 0.5 ? 'Risk increasing' : 'Risk reducing'
      });
    }

    return {
      preview: previewRisk,
      transactionScore,
      nlpScore,
      cvScore,
      finalScore,
      confidence,
      scenario,
      explanation,
      contributionRows,
      transactionVerdict: latestTransaction?.verdict || 'PENDING',
      transactionExplanations: latestTransaction?.explanations || [],
      nlpExplanations: latestNlpResult?.explanations || [],
      cvExplanations: latestCvResult?.explanations || []
    };
  }, [latestTransaction, latestNlpResult, latestCvResult, latestTransactionContext, previewRisk]);

  // I keep one helper for transaction submission so Controls can trigger a
  // backend score request and the dashboard can store the returned result.
  async function sendTransaction(payload, context) {
    try {
      const res = await api.post('/transaction/predict', payload);
      setTransactions((prev) => [res, ...prev].slice(0, 500));
      setLatestTransactionContext(context);
      setApiError('');
      return res;
    } catch (error) {
      setApiError(error.message);
      throw error;
    }
  }

  async function runNlp(message) {
    // I keep the NLP API call here so the whole dashboard shares one source of
    // truth for the latest text-screening result.
    const res = await api.post('/nlp/predict', { message });
    setLatestNlpResult(res);
    setApiError('');
    return res;
  }

  async function runCv(payload) {
    // I keep the CV API call here so the risk panel can react immediately to
    // the latest document result without extra prop drilling.
    const res = await api.post('/cv/predict', payload);
    setLatestCvResult(res);
    setApiError('');
    return res;
  }

  function recordFeedback(label) {
    // I store analyst feedback locally here so the audit panel can show a
    // simple review trail without changing the backend contract.
    const entry = {
      label,
      scenario: analysis.scenario,
      score: Number(analysis.finalScore ?? 0).toFixed(3),
      timestamp: new Date().toISOString()
    };
    setFeedbackLog((prev) => [entry, ...prev].slice(0, 12));
    setNotice(`I recorded analyst feedback: ${label}.`);
  }

  return (
    <div className="layout">
      <Header wsConnected={wsConnected} apiStatus={readiness?.status} />

      <main className="intelligence-grid">
        <section className="column-stack">
          <SystemStatus
            readiness={readiness}
            isLoading={readinessLoading}
            error={apiError}
            onRefresh={loadReadiness}
          />

          <div className="panel">
            <div className="panel-header">
              <h2>Multimodal Input Studio</h2>
              <span className="panel-tag">Input</span>
            </div>
            {notice ? <p className="feedback success">{notice}</p> : null}
            <Controls
              onSubmitTransaction={sendTransaction}
              onSubmitNlp={runNlp}
              onSubmitCv={runCv}
              onPreviewChange={setPreviewRisk}
              onNotify={setNotice}
              onError={setApiError}
              onRefreshReadiness={loadReadiness}
            />
          </div>
        </section>

        <section className="column-stack">
          <RiskIntel
            analysis={analysis}
            latestTransaction={latestTransaction}
            latestNlpResult={latestNlpResult}
            latestCvResult={latestCvResult}
            onConfirmFraud={() => recordFeedback('Confirm Fraud')}
            onMarkSafe={() => recordFeedback('Mark as Safe')}
          />
        </section>

        <section className="panel panel-span-full">
          <div className="panel-header">
            <h2>Audit Trail And Explainability</h2>
            <span className="panel-tag">Audit</span>
          </div>
          <AuditPanel
            contributionRows={analysis.contributionRows}
            transactions={transactions}
            feedbackLog={feedbackLog}
          />
        </section>
      </main>
    </div>
  );
}
