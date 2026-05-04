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
const CLAIM_SIGNAL_FIELDS = [
  {
    fieldName: "recent_high_value_purchase_flag",
    label: "Recent high-value purchase",
    helpText:
      "Select this if the item was bought recently and was a high-value purchase. Please keep the purchase receipt ready so we can confirm the item details."
  },
  {
    fieldName: "unusual_spend_spike_flag",
    label: "Unusual spending spike",
    helpText:
      "Select this if there was an unusual increase in related spending before the claim. Please provide any useful context in your message body."
  },
  {
    fieldName: "account_login_location_change_flag",
    label: "Login location changed",
    helpText:
      "Select this if you recently signed in from a new town, country, workplace, or travel location. Please make sure your account details are up to date."
  },
  {
    fieldName: "multiple_devices_last_7_days_flag",
    label: "Multiple devices in 7 days",
    helpText:
      "Select this if you used more than one phone, laptop, tablet, or browser to access your account in the last week."
  },
  {
    fieldName: "address_change_last_30_days_flag",
    label: "Address changed recently",
    helpText:
      "Select this if you changed your home or correspondence address recently. Please check that the address on your policy is correct."
  },
  {
    fieldName: "phone_change_last_30_days_flag",
    label: "Phone changed recently",
    helpText:
      "Select this if your contact number changed recently. Please make sure we can reach you on the phone number saved on your account."
  },
  {
    fieldName: "bank_detail_change_last_30_days_flag",
    label: "Bank details changed recently",
    helpText:
      "Select this if your payout bank details changed recently. Please double-check the account details before submitting your claim."
  },
  {
    fieldName: "late_night_submission_flag",
    label: "Late-night submission",
    helpText:
      "Select this if you are submitting the claim late at night. If anything needs clarification, add a short note in your message body."
  },
  {
    fieldName: "weekend_submission_flag",
    label: "Weekend submission",
    helpText:
      "Select this if you are submitting the claim during the weekend. We will still record your claim and guide you through the next steps."
  },
  {
    fieldName: "receipt_present_flag",
    label: "Receipt present",
    helpText:
      "Keep this selected if you have a receipt, invoice, or proof of purchase to upload. Clear images, PDFs, or TIFF files are accepted."
  },
  {
    fieldName: "receipt_mismatch_flag",
    label: "Receipt mismatch",
    helpText:
      "Select this if the receipt amount, date, merchant, or item details do not exactly match your claim. Please explain the difference in your message body."
  },
  {
    fieldName: "duplicate_receipt_flag",
    label: "Duplicate receipt",
    helpText:
      "Select this if you have already used this same receipt for another claim or if you are uploading a copy of an earlier document."
  },
  {
    fieldName: "image_tamper_flag",
    label: "Image tamper suspected",
    helpText:
      "Select this if the image is cropped, edited, unclear, or difficult to read. If possible, upload the clearest original version of the document."
  }
];

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
  const [selectedIdCardFile, setSelectedIdCardFile] = useState(null);

  const selectedEmail =
    homeData.claim_email_samples[activeEmailSample] ||
    claimEmailSamples[activeEmailSample] ||
    claimEmailSamples.suspicious ||
    claimEmailSamples.fraud;

  async function loadHomeData() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/insurance/home`);
      if (!response.ok) {
        return;
      }

      const payload = await response.json();
      setHomeData(payload);
      setLiveAlerts(payload.live_alerts || liveAlertsSeed);
    } catch (error) {
      console.warn("Could not load the public insurance homepage data.", error);
    }
  }

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
        throw new Error("Unable to complete login.");
      }

      const payload = await response.json();
      setAuthState({
        accessToken: payload.access_token,
        role: payload.role,
        username: payload.username,
        fullName: payload.full_name,
        email: payload.email,
        status: "authenticated",
        message: `${payload.full_name} signed in successfully.`
      });
      setActiveView(payload.role === "investigator" ? "company" : "customer");
    } catch (error) {
      setAuthState((currentState) => ({
        ...currentState,
        status: "error",
        message: "Login verification failed."
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
      message: "Signed out of current session."
    });
    setActiveView("home");
  }

  async function loadProtectedData() {
    try {
      const requestHeaders = {
        Authorization: `Bearer ${authState.accessToken}`
      };
      const requestList = [
        authState.role === "user" || authState.role === "investigator"
          ? fetch(`${API_BASE_URL}/api/insurance/customer-dashboard`, { headers: requestHeaders })
          : Promise.resolve(new Response(null, { status: 204 })),
        authState.role === "investigator"
          ? fetch(`${API_BASE_URL}/api/insurance/company-dashboard`, { headers: requestHeaders })
          : Promise.resolve(new Response(null, { status: 204 }))
      ];

      const [customerResponse, companyResponse] = await Promise.all(requestList);
      const customerPayload = customerResponse.status === 204 ? { claims: customerClaims } : await customerResponse.json();
      const companyPayload =
        companyResponse.status === 204
          ? { metrics: companyData.metrics, queue: companyQueue, live_alerts: liveAlertsSeed }
          : await companyResponse.json();

      setCustomerData(customerPayload);
      setCompanyData(companyPayload);
      setLiveAlerts(companyPayload.live_alerts || liveAlertsSeed);
    } catch (error) {
      console.warn("Could not load the protected insurance dashboard data.", error);
    }
  }

  async function handleClaimSubmission(formValues) {
    setSubmissionState({ status: "submitting", message: "Submitting claim to the insurance API." });

    try {
      const formData = new FormData();
      Object.entries(formValues).forEach(([fieldName, fieldValue]) => {
        if (fieldName === "claim_subject" || fieldName === "claim_message_body") {
          return;
        }
        formData.append(fieldName, String(fieldValue));
      });
      if (selectedEvidenceFile) {
        formData.append("evidence_file", selectedEvidenceFile);
      }
      if (selectedIdCardFile) {
        formData.append("id_card_file", selectedIdCardFile);
      }

      const response = await fetch(`${API_BASE_URL}/api/insurance/claims/with-evidence`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authState.accessToken}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error("Could not save the new claim.");
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
      await loadHomeData();
      await loadProtectedData();
      setSubmissionState({
        status: "success",
        message: `Claim ${payload.claim_id} submitted successfully and added to the investigation workflow.`
      });
      setSelectedEvidenceFile(null);
      setSelectedIdCardFile(null);
      setActiveView(authState.role === "investigator" ? "company" : "customer");
    } catch (error) {
      setSubmissionState({
        status: "error",
        message: "Unable to submit the claim. Please make sure the local API is running."
      });
    }
  }

  useEffect(() => {
    loadHomeData();
  }, []);

  useEffect(() => {
    if (!authState.accessToken) {
      return;
    }

    loadProtectedData();
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
          <p className="eyebrow">Gadget Insurance Fraud Platform</p>
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
            onSelectIdCardFile={setSelectedIdCardFile}
            selectedEvidenceFile={selectedEvidenceFile}
            selectedIdCardFile={selectedIdCardFile}
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
      <h2>Secure access for claimants and investigators.</h2>
      <p className="lead">
        Sign in to access protected claim and investigation dashboards.
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
        <p className="evidence-note">Demo accounts available: `demo_user / UserPass123!` and `investigator_anna / InvestigatorPass123!`.</p>
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
      <section className="hero-grid customer-dashboard-grid">
        <div className="hero-copy card spotlight">
          <p className="eyebrow">Real-Time Gadget Claims Experience</p>
          <h2>Screen device claims, receipts, ID evidence, and behaviour together.</h2>
          <p className="lead">
            This demo focuses on gadget and electronics insurance claims for laptops, phones, tablets, cameras, and similar high-value devices.
          </p>
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
            <span>Automatically Cleared Claims</span>
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
                <p>{feature.text ?? feature.description}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="card">
          <p className="section-title">Live Alert Feed</p>
          <div className="alert-list">
            {liveAlerts.map((alert) => (
              <article key={alert.id} className={`alert-card severity-${String(alert.severity).toLowerCase()}`}>
                <div className="alert-header">
                  <strong>{alert.title ?? String(alert.type ?? "alert").replace(/_/g, " ")}</strong>
                  <span>
                    {alert.time ??
                      (alert.timestamp
                        ? new Date(alert.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                        : "")}
                  </span>
                </div>
                <p>{alert.detail ?? alert.message}</p>
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
              <article key={field.name ?? field.field} className="signal-card">
                <h3>{field.name ?? field.field}</h3>
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

function CustomerDashboard({
  claims,
  onSubmitClaim,
  onSelectEvidenceFile,
  onSelectIdCardFile,
  selectedEvidenceFile,
  selectedIdCardFile,
  submissionState,
  currentUser
}) {
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
    claim_subject: "Claim for accidental damage to laptop",
    claim_message_body:
      "Accidental damage occurred after liquid spilled onto the laptop at home. The receipt is attached, and further details can be provided if required."
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
    const claimStory = `Subject: ${formValues.claim_subject}\n\nMessage:\n${formValues.claim_message_body}`;
    await onSubmitClaim({
      ...formValues,
      claim_amount_gbp: Number(formValues.claim_amount_gbp),
      estimated_item_value_gbp: Number(formValues.estimated_item_value_gbp),
      prior_claims_count: Number(formValues.prior_claims_count),
      claims_last_12_months: Number(formValues.claims_last_12_months),
      days_since_policy_start: Number(formValues.days_since_policy_start),
      claim_story: claimStory
    });
  }

  return (
    <>
      <section className="hero-grid">
        <div className="card spotlight">
          <p className="eyebrow">Policyholder Dashboard</p>
          <h2>Claimants see clear status updates and next steps.</h2>
          <p className="lead">
            This dashboard keeps claim status, payout progress, and evidence requirements easy to review.
          </p>
          <p className="evidence-note">Signed in as {currentUser.fullName || currentUser.username}</p>
          <div className="customer-guide">
            <p className="section-title">How To Use This Page</p>
            <ol>
              <li>Review your saved name and email, then choose the gadget policy and cover level for this device claim.</li>
              <li>Enter the device type, incident type, claim amount, and estimated device value as accurately as you can.</li>
              <li>Write an email subject and message body with dates, what happened, and any useful reference details.</li>
              <li>Upload the best purchase receipt or repair invoice, then add a clear image of your ID card before submitting.</li>
              <li>Use the information icons beside each checkbox if you are unsure whether a detail applies to you.</li>
            </ol>
          </div>
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
                  <option value="gadget">Gadget Insurance</option>
                  <option value="electronics_warranty">Electronics Warranty</option>
                  <option value="device_protection">Device Protection</option>
                  <option value="portable_electronics">Portable Electronics</option>
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
                Device Category
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
                Device Value (GBP)
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
              Email Subject
              <input
                value={formValues.claim_subject}
                onChange={(event) => updateField("claim_subject", event.target.value)}
                placeholder="Example: Claim for accidental damage to laptop"
              />
            </label>

            <label>
              Message Body
              <textarea
                value={formValues.claim_message_body}
                onChange={(event) => updateField("claim_message_body", event.target.value)}
                rows="6"
                placeholder="Please explain what happened, when it happened, and what evidence is attached."
              />
            </label>

            <label>
              Device Receipt Or Repair Invoice
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.bmp,.tif,.tiff,.pdf"
                onChange={(event) => onSelectEvidenceFile(event.target.files?.[0] || null)}
              />
            </label>
            <label>
              Claimant ID Card
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.bmp,.tif,.tiff,.pdf"
                onChange={(event) => onSelectIdCardFile(event.target.files?.[0] || null)}
              />
            </label>

            <div className="checkbox-grid">
              {CLAIM_SIGNAL_FIELDS.map(({ fieldName, label, helpText }) => (
                <label key={fieldName} className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={formValues[fieldName]}
                    onChange={(event) => updateField(fieldName, event.target.checked)}
                  />
                  <span>{label}</span>
                  <InfoHint text={helpText} />
                </label>
              ))}
            </div>

            <button className="action-button" type="submit" disabled={submissionState.status === "submitting"}>
              {submissionState.status === "submitting" ? "Submitting Claim..." : "Submit New Claim"}
            </button>
            {selectedEvidenceFile ? (
              <p className="evidence-note">Selected receipt or invoice: {selectedEvidenceFile.name}</p>
            ) : (
              <>
                <p className="evidence-note">Attach a receipt image, TIFF, or PDF evidence file before submission.</p>
              </>
            )}
            {selectedIdCardFile ? (
              <p className="evidence-note">Selected claimant ID card: {selectedIdCardFile.name}</p>
            ) : (
              <p className="evidence-note">Attach a clear claimant ID card image or PDF so the claim can be matched to the signed-in policyholder.</p>
            )}
            <p className="evidence-note">Claimant identity is bound to the signed-in gadget policyholder account.</p>
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
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("all");
  const [policyFilter, setPolicyFilter] = useState("all");
  const [monthFilter, setMonthFilter] = useState("all");
  const [selectedClaimId, setSelectedClaimId] = useState("");

  const normalizedQueue = queue.map((item) => {
    const claimId = item.claim_id ?? item.claimId ?? "Unknown";
    const claimant = item.claimant ?? item.assignee ?? "Unassigned";
    const policyType = item.policy_type ?? item.policyType ?? item.type ?? "Unknown";
    const combinedRisk = item.combined_risk ?? item.combinedRisk ?? item.priority ?? "Review";
    const nlpRisk = item.nlp_risk ?? item.nlpRisk ?? 0;
    const documentRisk = item.document_risk ?? item.documentRisk ?? 0;
    const behaviouralRisk = item.behavioural_risk ?? item.behaviouralRisk ?? 0;
    const alertReason = item.alert_reason ?? item.alertReason ?? "Review for potential fraud.";
    const submittedAt = item.submitted_at ?? item.submittedAt ?? item.submitted ?? "";
    const amount =
      typeof item.amount === "number"
        ? `GBP ${item.amount.toLocaleString("en-GB", { maximumFractionDigits: 0 })}`
        : item.amount ?? "Unknown";
    return {
      ...item,
      claimId,
      claimant,
      policyType,
      combinedRisk,
      nlpRisk,
      documentRisk,
      behaviouralRisk,
      alertReason,
      submittedAt,
      amount
    };
  });

  const availablePolicies = Array.from(new Set(normalizedQueue.map((item) => item.policyType))).sort();
  const availableMonths = Array.from(
    new Set(
      normalizedQueue
        .map((item) => item.submittedAt.slice(3, 11))
        .filter(Boolean)
    )
  );

  const filteredQueue = normalizedQueue.filter((item) => {
    const normalizedSearch = searchTerm.trim().toLowerCase();
    const matchesSearch =
      !normalizedSearch ||
      item.claimId.toLowerCase().includes(normalizedSearch) ||
      item.claimant.toLowerCase().includes(normalizedSearch) ||
      item.policyType.toLowerCase().includes(normalizedSearch) ||
      item.alertReason.toLowerCase().includes(normalizedSearch);
    const matchesRisk = riskFilter === "all" || item.combinedRisk.toLowerCase() === riskFilter;
    const matchesPolicy = policyFilter === "all" || item.policyType === policyFilter;
    const matchesMonth = monthFilter === "all" || item.submittedAt.includes(monthFilter);
    return matchesSearch && matchesRisk && matchesPolicy && matchesMonth;
  });

  const selectedQueueItem =
    filteredQueue.find((item) => item.claimId === selectedClaimId) ||
    filteredQueue[0] ||
    normalizedQueue[0] ||
    null;

  useEffect(() => {
    if (!selectedQueueItem) {
      setSelectedClaimId("");
      return;
    }

    if (selectedClaimId !== selectedQueueItem.claimId) {
      setSelectedClaimId(selectedQueueItem.claimId);
    }
  }, [selectedClaimId, selectedQueueItem]);

  const filteredHighRiskCount = filteredQueue.filter((item) => item.combinedRisk === "High").length;
  const filteredReviewCount = filteredQueue.filter((item) => item.combinedRisk === "Review").length;

  return (
    <>
      <section className="hero-grid">
        <div className="card spotlight">
          <p className="eyebrow">Fraud Operations Dashboard</p>
          <h2>Investigators can monitor claim risk in real time.</h2>
          <p className="lead">
            Operational metrics, live alerts, and the review queue are combined for faster fraud response.
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
            <span>Automatic Approvals</span>
            <strong>{metrics.auto_approvals}</strong>
          </div>
        </div>
      </section>

      <section className="content-grid company-layout">
        <div className="card">
          <p className="section-title">Queue Search And Filters</p>
          <div className="dashboard-toolbar">
            <label className="toolbar-field toolbar-search">
              <span>Search claims</span>
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search by claim ID, claimant, policy, or reason"
              />
            </label>
            <label className="toolbar-field">
              <span>Risk</span>
              <select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)}>
                <option value="all">All risk levels</option>
                <option value="high">High</option>
                <option value="review">Review</option>
                <option value="low">Low</option>
              </select>
            </label>
            <label className="toolbar-field">
              <span>Policy</span>
              <select value={policyFilter} onChange={(event) => setPolicyFilter(event.target.value)}>
                <option value="all">All policy types</option>
                {availablePolicies.map((policy) => (
                  <option key={policy} value={policy}>
                    {policy}
                  </option>
                ))}
              </select>
            </label>
            <label className="toolbar-field">
              <span>Month</span>
              <select value={monthFilter} onChange={(event) => setMonthFilter(event.target.value)}>
                <option value="all">All months</option>
                {availableMonths.map((month) => (
                  <option key={month} value={month}>
                    {month}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="card filter-snapshot">
          <p className="section-title">Filtered View</p>
          <div className="filter-kpis">
            <article className="mini-kpi">
              <span>Matching Claims</span>
              <strong>{filteredQueue.length}</strong>
            </article>
            <article className="mini-kpi">
              <span>High Risk Matches</span>
              <strong>{filteredHighRiskCount}</strong>
            </article>
            <article className="mini-kpi">
              <span>Review Matches</span>
              <strong>{filteredReviewCount}</strong>
            </article>
          </div>
        </div>
      </section>

      <section className="content-grid company-layout">
        <div className="card">
          <p className="section-title">Investigation Queue</p>
          <div className="queue-list">
            {filteredQueue.map((item) => (
              <article
                key={item.claimId}
                className={selectedQueueItem?.claimId === item.claimId ? "queue-card selected" : "queue-card"}
                onClick={() => setSelectedClaimId(item.claimId)}
                role="button"
                tabIndex={0}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    setSelectedClaimId(item.claimId);
                  }
                }}
              >
                <div className="queue-topline">
                  <strong>{item.claimId}</strong>
                  <span className={`status-chip ${item.combinedRisk.toLowerCase()}`}>
                    {item.combinedRisk}
                  </span>
                </div>
                <p className="queue-meta">
                  {item.claimant} • {item.policyType} • {item.amount}
                </p>
                <p className="queue-time">Submitted {item.submittedAt || "Unknown"}</p>
                <div className="risk-bars">
                  <RiskBar label="NLP Risk" value={item.nlpRisk} />
                  <RiskBar label="Document Risk" value={item.documentRisk} />
                  <RiskBar label="Behaviour Risk" value={item.behaviouralRisk} />
                </div>
                <p className="queue-detail">{item.alertReason}</p>
              </article>
            ))}
            {filteredQueue.length === 0 ? (
              <article className="queue-card queue-empty">
                <h3>No matching claims</h3>
                <p>Try clearing one of the filters or searching with a broader claim reference.</p>
              </article>
            ) : null}
          </div>
        </div>

        <div className="card">
          <p className="section-title">Claim Review Workspace</p>
          {selectedQueueItem ? (
            <div className="case-workspace">
              <div className="workspace-headline">
                <div>
                  <h3>{selectedQueueItem.claimId}</h3>
                  <p>
                    {selectedQueueItem.claimant} • {selectedQueueItem.policyType}
                  </p>
                </div>
                <span className={`status-chip ${selectedQueueItem.combinedRisk.toLowerCase()}`}>
                  {selectedQueueItem.combinedRisk}
                </span>
              </div>
              <div className="workspace-grid">
                <article className="workspace-panel">
                  <span>Submitted</span>
                  <strong>{selectedQueueItem.submittedAt || "Unknown"}</strong>
                </article>
                <article className="workspace-panel">
                  <span>Claim Amount</span>
                  <strong>{selectedQueueItem.amount}</strong>
                </article>
                <article className="workspace-panel">
                  <span>NLP Risk</span>
                  <strong>{Math.round(selectedQueueItem.nlpRisk * 100)}%</strong>
                </article>
                <article className="workspace-panel">
                  <span>Document Risk</span>
                  <strong>{Math.round(selectedQueueItem.documentRisk * 100)}%</strong>
                </article>
                <article className="workspace-panel">
                  <span>Behaviour Risk</span>
                  <strong>{Math.round(selectedQueueItem.behaviouralRisk * 100)}%</strong>
                </article>
              </div>
              <div className="workspace-notes">
                <p className="section-title">Investigator Focus</p>
                <p>{selectedQueueItem.alertReason}</p>
              </div>
              <div className="alert-list compact-alerts">
                {liveAlerts.slice(0, 4).map((alert) => (
                  <article key={alert.id} className={`alert-card severity-${String(alert.severity).toLowerCase()}`}>
                    <div className="alert-header">
                      <strong>{alert.id}</strong>
                      <span>
                        {alert.time ??
                          (alert.timestamp
                            ? new Date(alert.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                            : "")}
                      </span>
                    </div>
                    <h3>{alert.title ?? String(alert.type ?? "alert").replace(/_/g, " ")}</h3>
                    <p>{alert.detail ?? alert.message}</p>
                  </article>
                ))}
              </div>
            </div>
          ) : (
            <div className="queue-card queue-empty">
              <h3>No claim selected</h3>
              <p>The review workspace will update when a queue item matches your filters.</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}

function InfoHint({ text }) {
  return (
    <span
      className="info-hint"
      data-tooltip={text}
      title={text}
      aria-label={text}
      tabIndex={0}
      onClick={(event) => event.preventDefault()}
    >
      i
    </span>
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
