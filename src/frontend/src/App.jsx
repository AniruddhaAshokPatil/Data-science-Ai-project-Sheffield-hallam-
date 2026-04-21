import { useEffect, useState } from "react";
import {
  behaviouralFieldCards,
  claimEmailSamples,
  companyQueue,
  customerClaims,
  liveAlertsSeed,
  publicFeatures
} from "./data/mockData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const ALERTS_WS_URL = API_BASE_URL.replace(/^http/, "ws") + "/ws/alerts";

function App() {
  const [authState, setAuthState] = useState({
    accessToken: "",
    role: "",
    username: "",
    fullName: "",
    email: "",
    status: "logged_out",
    message: ""
  });
  const [activeView, setActiveView] = useState("home");
  const [liveAlerts, setLiveAlerts] = useState(liveAlertsSeed);
  const [activeEmailSample, setActiveEmailSample] = useState("genuine");
  const [homeData, setHomeData] = useState({
    metrics: {
      claims_processed_today: 128,
      live_review_queue: 14,
      auto_cleared_rate: "84%"
    },
    public_features: publicFeatures,
    behavioural_fields: behaviouralFieldCards,
    claim_email_samples: claimEmailSamples
  });
  const [customerData, setCustomerData] = useState({ claims: customerClaims });
  const [companyData, setCompanyData] = useState({
    metrics: {
      high_risk_open: 6,
      review_needed: 8,
      avg_triage_time: "4m",
      auto_approvals: "84%"
    },
    queue: companyQueue
  });
  const [submissionState, setSubmissionState] = useState({ status: "idle", message: "" });
  const [selectedEvidenceFile, setSelectedEvidenceFile] = useState(null);

  const selectedEmail = homeData.claim_email_samples[activeEmailSample] || claimEmailSamples[activeEmailSample];

  async function handleLogin(credentials) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(credentials)
      });

      if (!response.ok) {
        throw new Error("I could not complete the login.");
      }

      const payload = await response.json();
      setAuthState({
        accessToken: payload.access_token,
        role: payload.role,
        username: payload.username,
        fullName: payload.full_name,
        email: payload.email,
        status: "authenticated",
        message: `I signed in as ${payload.full_name}.`
      });
      setActiveView(payload.role === "investigator" ? "company" : "customer");
    } catch (error) {
      setAuthState((currentState) => ({
        ...currentState,
        status: "error",
        message: "I could not verify the login details."
      }));
    }
  }

  function handleLogout() {
    setAuthState({
      accessToken: "",
      role: "",
      username: "",
      fullName: "",
      email: "",
      status: "logged_out",
      message: "I signed out of the current session."
    });
    setActiveView("home");
  }

  async function loadApiData() {
    if (!authState.accessToken) {
      return;
    }

    try {
      const requestHeaders = {
        Authorization: `Bearer ${authState.accessToken}`
      };
      const requestList = [
        fetch(`${API_BASE_URL}/api/insurance/home`),
        authState.role === "user" || authState.role === "investigator"
          ? fetch(`${API_BASE_URL}/api/insurance/customer-dashboard`, { headers: requestHeaders })
          : Promise.resolve(new Response(null, { status: 204 })),
        authState.role === "investigator"
          ? fetch(`${API_BASE_URL}/api/insurance/company-dashboard`, { headers: requestHeaders })
          : Promise.resolve(new Response(null, { status: 204 }))
      ];

      const [homeResponse, customerResponse, companyResponse] = await Promise.all(requestList);

      if (!homeResponse.ok) {
        return;
      }

      const homePayload = await homeResponse.json();
      const customerPayload = customerResponse.status === 204 ? { claims: customerClaims } : await customerResponse.json();
      const companyPayload =
        companyResponse.status === 204
          ? { metrics: companyData.metrics, queue: companyQueue, live_alerts: liveAlertsSeed }
          : await companyResponse.json();

      setHomeData(homePayload);
      setCustomerData(customerPayload);
      setCompanyData(companyPayload);
      setLiveAlerts(companyPayload.live_alerts || homePayload.live_alerts || liveAlertsSeed);
    } catch (error) {
      // I keep the frontend on mock data if the local API is not running yet.
      console.warn("I could not load the insurance API, so I kept the local demo data.", error);
    }
  }

  async function handleClaimSubmission(formValues) {
    setSubmissionState({ status: "submitting", message: "I am sending the claim to the insurance API." });

    try {
      const formData = new FormData();
      Object.entries(formValues).forEach(([fieldName, fieldValue]) => {
        formData.append(fieldName, String(fieldValue));
      });
      if (selectedEvidenceFile) {
        formData.append("evidence_file", selectedEvidenceFile);
      }

      const response = await fetch(`${API_BASE_URL}/api/insurance/claims/with-evidence`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authState.accessToken}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error("I could not save the new claim.");
      }

      const payload = await response.json();
      setCustomerData((currentData) => ({
        claims: [payload.customer_claim, ...(currentData.claims || [])]
      }));
      setCompanyData((currentData) => ({
        ...currentData,
        queue: [payload.queue_item, ...(currentData.queue || [])]
      }));
      setLiveAlerts((currentAlerts) => [payload.alert, ...currentAlerts].slice(0, 7));
      await loadApiData();
      setSubmissionState({
        status: "success",
        message: `I created claim ${payload.claim_id}, stored the evidence file, and pushed it into the investigation workflow.`
      });
      setSelectedEvidenceFile(null);
      setActiveView(authState.role === "investigator" ? "company" : "customer");
    } catch (error) {
      setSubmissionState({
        status: "error",
        message: "I could not submit the claim. Please make sure the local API is running."
      });
    }
  }

  useEffect(() => {
    async function loadInitialData() {
      await loadApiData();
    }

    if (authState.accessToken) {
      loadInitialData();
    }
  }, [authState.accessToken, authState.role]);

  useEffect(() => {
    if (authState.role !== "investigator" || !authState.accessToken) {
      return undefined;
    }

    const websocket = new WebSocket(`${ALERTS_WS_URL}?token=${encodeURIComponent(authState.accessToken)}`);

    websocket.onmessage = (event) => {
      const parsedAlert = JSON.parse(event.data);
      setLiveAlerts((currentAlerts) => [parsedAlert, ...currentAlerts].slice(0, 7));
    };

    websocket.onerror = () => {
      // I silently fall back here because the demo can still run without the socket.
      websocket.close();
    };

    return () => {
      websocket.close();
    };
  }, [authState.accessToken, authState.role]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Insurance Claim Fraud Platform</p>
          <h1>ShieldWise</h1>
        </div>
        <nav className="topbar-nav">
          <button className={activeView === "home" ? "nav-link active" : "nav-link"} onClick={() => setActiveView("home")}>
            Home
          </button>
          <button
            className={activeView === "customer" ? "nav-link active" : "nav-link"}
            onClick={() => setActiveView("customer")}
            disabled={!authState.accessToken}
          >
            User Dashboard
          </button>
          <button
            className={activeView === "company" ? "nav-link active" : "nav-link"}
            onClick={() => setActiveView("company")}
            disabled={authState.role !== "investigator"}
          >
            Company Dashboard
          </button>
          {authState.accessToken ? (
            <button className="nav-link" onClick={handleLogout}>
              Sign Out
            </button>
          ) : null}
        </nav>
      </header>

      <main className="page-shell">
        {!authState.accessToken && (
          <LoginPanel authState={authState} onLogin={handleLogin} />
        )}
        {activeView === "home" && (
          <HomePage
            activeEmailSample={activeEmailSample}
            behaviouralFieldCards={homeData.behavioural_fields}
            liveAlerts={liveAlerts}
            publicFeatures={homeData.public_features}
            selectedEmail={selectedEmail}
            topMetrics={homeData.metrics}
            setActiveEmailSample={setActiveEmailSample}
          />
        )}
        {activeView === "customer" && (
          <CustomerDashboard
            claims={customerData.claims}
            onSubmitClaim={handleClaimSubmission}
            onSelectEvidenceFile={setSelectedEvidenceFile}
            selectedEvidenceFile={selectedEvidenceFile}
            submissionState={submissionState}
            currentUser={authState}
          />
        )}
        {activeView === "company" && authState.role === "investigator" && (
          <CompanyDashboard liveAlerts={liveAlerts} metrics={companyData.metrics} queue={companyData.queue} />
        )}
      </main>
    </div>
  );
}

function LoginPanel({ authState, onLogin }) {
  const [credentials, setCredentials] = useState({
    username: "demo_user",
    password: "UserPass123!"
  });

  async function handleSubmit(event) {
    event.preventDefault();
    await onLogin(credentials);
  }

  return (
    <section className="card login-panel">
      <p className="section-title">Authentication</p>
      <h2>I protect claimants and investigators with separate roles.</h2>
      <p className="lead">
        I now require sign-in before opening protected claim or investigation views.
      </p>
      <form className="claim-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Username
            <input value={credentials.username} onChange={(event) => setCredentials((current) => ({ ...current, username: event.target.value }))} />
          </label>
          <label>
            Password
            <input type="password" value={credentials.password} onChange={(event) => setCredentials((current) => ({ ...current, password: event.target.value }))} />
          </label>
        </div>
        <button className="action-button" type="submit">
          Sign In
        </button>
        <p className="evidence-note">I seeded demo accounts: `demo_user / UserPass123!` and `investigator_anna / InvestigatorPass123!`.</p>
        {authState.message ? <p className={`form-status ${authState.status === "authenticated" ? "success" : "error"}`}>{authState.message}</p> : null}
      </form>
    </section>
  );
}

function HomePage({
  activeEmailSample,
  behaviouralFieldCards,
  liveAlerts,
  publicFeatures,
  selectedEmail,
  topMetrics,
  setActiveEmailSample
}) {
  return (
    <>
      <section className="hero-grid">
        <div className="hero-copy card spotlight">
          <p className="eyebrow">Real-Time Insurance Experience</p>
          <h2>I screen claim stories, receipts, and behaviour together.</h2>
          <p className="lead">
            I turn the project into one realistic insurance product flow with a public homepage, a policyholder dashboard, and a live fraud-operations dashboard.
          </p>
          <div className="pill-row">
            <span className="pill">Issue #23: React Frontend Skeleton</span>
            <span className="pill">Issue #24: Dashboard Components</span>
            <span className="pill">Issue #25: Live Alert Flow Ready</span>
          </div>
        </div>

        <div className="card kpi-stack">
          <div className="kpi-card">
            <span>Claims Processed Today</span>
            <strong>{topMetrics.claims_processed_today}</strong>
          </div>
          <div className="kpi-card">
            <span>Live Review Queue</span>
            <strong>{topMetrics.live_review_queue}</strong>
          </div>
          <div className="kpi-card">
            <span>Auto-Cleared Claims</span>
            <strong>{topMetrics.auto_cleared_rate}</strong>
          </div>
        </div>
      </section>

      <section className="content-grid">
        <div className="card">
          <p className="section-title">Platform Highlights</p>
          <div className="feature-grid">
            {publicFeatures.map((feature) => (
              <article key={feature.title} className="feature-card">
                <h3>{feature.title}</h3>
                <p>{feature.text}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="card">
          <p className="section-title">Live Alert Feed</p>
          <div className="alert-list">
            {liveAlerts.map((alert) => (
              <article key={alert.id} className={`alert-card severity-${alert.severity.toLowerCase()}`}>
                <div className="alert-header">
                  <strong>{alert.title}</strong>
                  <span>{alert.time}</span>
                </div>
                <p>{alert.detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="content-grid">
        <div className="card">
          <p className="section-title">Behavioural Signals</p>
          <div className="signal-grid">
            {behaviouralFieldCards.map((field) => (
              <article key={field.name} className="signal-card">
                <h3>{field.name}</h3>
                <p>{field.description}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="card">
          <p className="section-title">Claim Email Samples</p>
          <div className="sample-toggle">
            <button
              className={activeEmailSample === "genuine" ? "sample-button active" : "sample-button"}
              onClick={() => setActiveEmailSample("genuine")}
            >
              Genuine Claim
            </button>
            <button
              className={activeEmailSample === "fraud" ? "sample-button active" : "sample-button"}
              onClick={() => setActiveEmailSample("fraud")}
            >
              Fraudulent Claim
            </button>
          </div>
          <div className="email-sample">
            <p className="email-subject">{selectedEmail.subject}</p>
            <pre>{selectedEmail.body}</pre>
          </div>
        </div>
      </section>
    </>
  );
}

function CustomerDashboard({ claims, onSubmitClaim, onSelectEvidenceFile, selectedEvidenceFile, submissionState, currentUser }) {
  const [formValues, setFormValues] = useState({
    claimant_name: currentUser.fullName || "",
    claimant_email: currentUser.email || "",
    policy_type: "gadget",
    coverage_tier: "premium",
    item_category: "laptop",
    incident_type: "theft",
    claim_amount_gbp: 1499,
    estimated_item_value_gbp: 1299,
    prior_claims_count: 1,
    claims_last_12_months: 0,
    days_since_policy_start: 180,
    recent_high_value_purchase_flag: false,
    unusual_spend_spike_flag: false,
    account_login_location_change_flag: false,
    multiple_devices_last_7_days_flag: false,
    address_change_last_30_days_flag: false,
    phone_change_last_30_days_flag: false,
    bank_detail_change_last_30_days_flag: false,
    late_night_submission_flag: false,
    weekend_submission_flag: false,
    receipt_present_flag: true,
    receipt_mismatch_flag: false,
    duplicate_receipt_flag: false,
    image_tamper_flag: false,
    claim_story:
      "I would like to submit a claim for accidental damage to my laptop after it stopped working following a spill at home. I have attached the receipt and I can provide more details if required."
  });

  function updateField(fieldName, fieldValue) {
    setFormValues((currentValues) => ({
      ...currentValues,
      [fieldName]: fieldValue
    }));
  }

  useEffect(() => {
    setFormValues((currentValues) => ({
      ...currentValues,
      claimant_name: currentUser.fullName || "",
      claimant_email: currentUser.email || ""
    }));
  }, [currentUser.email, currentUser.fullName]);

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmitClaim({
      ...formValues,
      claim_amount_gbp: Number(formValues.claim_amount_gbp),
      estimated_item_value_gbp: Number(formValues.estimated_item_value_gbp),
      prior_claims_count: Number(formValues.prior_claims_count),
      claims_last_12_months: Number(formValues.claims_last_12_months),
      days_since_policy_start: Number(formValues.days_since_policy_start)
    });
  }

  return (
    <>
      <section className="hero-grid">
        <div className="card spotlight">
          <p className="eyebrow">Policyholder Dashboard</p>
          <h2>I give claimants a clean view of their claims and next steps.</h2>
          <p className="lead">
            I keep this page simple so a user can see claim status, payout progress, and what evidence is still required.
          </p>
          <p className="evidence-note">Signed in as {currentUser.fullName || currentUser.username}</p>
        </div>
        <div className="card quick-actions">
          <p className="section-title">Claim Intake</p>
          <form className="claim-form" onSubmit={handleSubmit}>
            <div className="form-grid">
              <label>
                Claimant Name
                <input value={formValues.claimant_name} readOnly />
              </label>
              <label>
                Email
                <input value={formValues.claimant_email} readOnly />
              </label>
              <label>
                Policy Type
                <select value={formValues.policy_type} onChange={(event) => updateField("policy_type", event.target.value)}>
                  <option value="gadget">Gadget</option>
                  <option value="contents">Contents</option>
                  <option value="home">Home</option>
                  <option value="travel">Travel</option>
                </select>
              </label>
              <label>
                Coverage Tier
                <select value={formValues.coverage_tier} onChange={(event) => updateField("coverage_tier", event.target.value)}>
                  <option value="basic">Basic</option>
                  <option value="standard">Standard</option>
                  <option value="plus">Plus</option>
                  <option value="premium">Premium</option>
                </select>
              </label>
              <label>
                Item Category
                <input value={formValues.item_category} onChange={(event) => updateField("item_category", event.target.value)} />
              </label>
              <label>
                Incident Type
                <input value={formValues.incident_type} onChange={(event) => updateField("incident_type", event.target.value)} />
              </label>
              <label>
                Claim Amount (GBP)
                <input
                  type="number"
                  min="1"
                  value={formValues.claim_amount_gbp}
                  onChange={(event) => updateField("claim_amount_gbp", event.target.value)}
                />
              </label>
              <label>
                Item Value (GBP)
                <input
                  type="number"
                  min="1"
                  value={formValues.estimated_item_value_gbp}
                  onChange={(event) => updateField("estimated_item_value_gbp", event.target.value)}
                />
              </label>
              <label>
                Prior Claims
                <input
                  type="number"
                  min="0"
                  value={formValues.prior_claims_count}
                  onChange={(event) => updateField("prior_claims_count", event.target.value)}
                />
              </label>
              <label>
                Claims Last 12 Months
                <input
                  type="number"
                  min="0"
                  value={formValues.claims_last_12_months}
                  onChange={(event) => updateField("claims_last_12_months", event.target.value)}
                />
              </label>
              <label>
                Days Since Policy Start
                <input
                  type="number"
                  min="0"
                  value={formValues.days_since_policy_start}
                  onChange={(event) => updateField("days_since_policy_start", event.target.value)}
                />
              </label>
            </div>

            <label>
              Claim Story
              <textarea value={formValues.claim_story} onChange={(event) => updateField("claim_story", event.target.value)} rows="5" />
            </label>

            <label>
              Evidence File
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.bmp,.pdf"
                onChange={(event) => onSelectEvidenceFile(event.target.files?.[0] || null)}
              />
            </label>

            <div className="checkbox-grid">
              {[
                ["recent_high_value_purchase_flag", "Recent high-value purchase"],
                ["unusual_spend_spike_flag", "Unusual spending spike"],
                ["account_login_location_change_flag", "Login location changed"],
                ["multiple_devices_last_7_days_flag", "Multiple devices in 7 days"],
                ["address_change_last_30_days_flag", "Address changed recently"],
                ["phone_change_last_30_days_flag", "Phone changed recently"],
                ["bank_detail_change_last_30_days_flag", "Bank details changed recently"],
                ["late_night_submission_flag", "Late-night submission"],
                ["weekend_submission_flag", "Weekend submission"],
                ["receipt_present_flag", "Receipt present"],
                ["receipt_mismatch_flag", "Receipt mismatch"],
                ["duplicate_receipt_flag", "Duplicate receipt"],
                ["image_tamper_flag", "Image tamper suspected"]
              ].map(([fieldName, label]) => (
                <label key={fieldName} className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={formValues[fieldName]}
                    onChange={(event) => updateField(fieldName, event.target.checked)}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>

            <button className="action-button" type="submit" disabled={submissionState.status === "submitting"}>
              {submissionState.status === "submitting" ? "Submitting Claim..." : "Submit New Claim"}
            </button>
            {selectedEvidenceFile ? (
              <p className="evidence-note">I will upload evidence file: {selectedEvidenceFile.name}</p>
            ) : (
              <>
                <p className="evidence-note">I can attach a receipt image or PDF evidence file before submission.</p>
                <p className="evidence-note">I bind the claimant identity to the signed-in policyholder account for claim submission.</p>
              </>
            )}
            {submissionState.message ? (
              <p className={`form-status ${submissionState.status}`}>{submissionState.message}</p>
            ) : null}
          </form>
        </div>
      </section>

      <section className="card">
        <p className="section-title">My Claims</p>
        <div className="table-shell">
          <table>
            <thead>
              <tr>
                <th>Claim ID</th>
                <th>Policy</th>
                <th>Item</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Next Step</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((claim) => (
                <tr key={claim.claim_id ?? claim.claimId}>
                  <td>{claim.claim_id ?? claim.claimId}</td>
                  <td>{claim.policy_type ?? claim.policyType}</td>
                  <td>{claim.item_category ?? claim.itemCategory}</td>
                  <td>{claim.amount}</td>
                  <td>{claim.status}</td>
                  <td>
                    {claim.next_step ?? claim.nextStep}
                    {claim.evidence_name || claim.evidenceName ? ` Evidence: ${claim.evidence_name ?? claim.evidenceName}` : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function CompanyDashboard({ liveAlerts, metrics, queue }) {
  return (
    <>
      <section className="hero-grid">
        <div className="card spotlight">
          <p className="eyebrow">Fraud Operations Dashboard</p>
          <h2>I give investigators one place to watch claim risk in real time.</h2>
          <p className="lead">
            I combine operational metrics, live alerts, and the review queue so the company can act at the claim-submission stage.
          </p>
        </div>
        <div className="card kpi-grid">
          <div className="mini-kpi">
            <span>High Risk Open</span>
            <strong>{metrics.high_risk_open}</strong>
          </div>
          <div className="mini-kpi">
            <span>Review Needed</span>
            <strong>{metrics.review_needed}</strong>
          </div>
          <div className="mini-kpi">
            <span>Avg Triage Time</span>
            <strong>{metrics.avg_triage_time}</strong>
          </div>
          <div className="mini-kpi">
            <span>Auto Approvals</span>
            <strong>{metrics.auto_approvals}</strong>
          </div>
        </div>
      </section>

      <section className="content-grid company-layout">
        <div className="card">
          <p className="section-title">Investigation Queue</p>
          <div className="queue-list">
            {queue.map((item) => (
              <article key={item.claim_id ?? item.claimId} className="queue-card">
                <div className="queue-topline">
                  <strong>{item.claim_id ?? item.claimId}</strong>
                  <span className={`status-chip ${(item.combined_risk ?? item.combinedRisk).toLowerCase()}`}>
                    {item.combined_risk ?? item.combinedRisk}
                  </span>
                </div>
                <p className="queue-meta">
                  {item.claimant} • {item.policy_type ?? item.policyType} • {item.amount}
                </p>
                <div className="risk-bars">
                  <RiskBar label="NLP Risk" value={item.nlp_risk ?? item.nlpRisk} />
                  <RiskBar label="Document Risk" value={item.document_risk ?? item.documentRisk} />
                  <RiskBar label="Behaviour Risk" value={item.behavioural_risk ?? item.behaviouralRisk} />
                </div>
                <p className="queue-detail">{item.alert_reason ?? item.alertReason}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="card">
          <p className="section-title">Live Monitoring Feed</p>
          <div className="alert-list">
            {liveAlerts.map((alert) => (
              <article key={alert.id} className={`alert-card severity-${alert.severity.toLowerCase()}`}>
                <div className="alert-header">
                  <strong>{alert.id}</strong>
                  <span>{alert.time}</span>
                </div>
                <h3>{alert.title}</h3>
                <p>{alert.detail}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

function RiskBar({ label, value }) {
  return (
    <div className="risk-row">
      <div className="risk-label-line">
        <span>{label}</span>
        <strong>{Math.round(value * 100)}%</strong>
      </div>
      <div className="risk-track">
        <div className="risk-fill" style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
    </div>
  );
}

export default App;
