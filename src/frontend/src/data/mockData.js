export const publicFeatures = [
  { title: "AI-Powered Fraud Detection", description: "Advanced machine learning algorithms analyze claim patterns and detect suspicious activities in real-time.", icon: "🤖" },
  { title: "Automated Claim Processing", description: "Streamline claim workflows with intelligent automation that reduces processing time by 60%.", icon: "⚡" },
  { title: "Real-Time Alerts", description: "Get instant notifications about high-risk claims and emerging fraud patterns.", icon: "🚨" },
  { title: "Document Analysis", description: "OCR and AI-powered document verification ensures authenticity of submitted evidence.", icon: "📄" }
];

export const behaviouralFieldCards = [
  { field: "Claim Frequency", value: "2.3x average", risk: "high", description: "Customer submits claims more frequently than typical policyholders" },
  { field: "Amount Pattern", value: "Escalating", risk: "medium", description: "Claim amounts have been steadily increasing over time" },
  { field: "Document Quality", value: "Inconsistent", risk: "high", description: "Submitted documents show signs of manipulation or forgery" },
  { field: "Timing Pattern", value: "Suspicious", risk: "medium", description: "Claims submitted during unusual hours or patterns" }
];

export const claimEmailSamples = {
  genuine: { subject: "Medical Claim Submission - Policy #12345", from: "patient@example.com", body: "Dear Insurance Company,\n\nI am submitting a claim for medical expenses incurred on March 15, 2024. Please find attached the necessary documentation including medical bills, doctor's notes, and receipts.\n\nThank you for your prompt attention.\n\nBest regards,\nJohn Doe", risk_score: 15, analysis: "Standard medical claim with proper documentation" },
  suspicious: { subject: "URGENT: Claim for Accident - Need Immediate Processing", from: "claimant@urgent-mail.com", body: "HELLO INSURANCE!!!\n\nI HAD A CAR ACCIDENT LAST WEEK. NEED MONEY FAST. ALL PAPERS ATTACHED. PLEASE APPROVE QUICKLY!!!\n\nTHANKS,\nJANE SMITH", risk_score: 85, analysis: "High-pressure language, urgent requests, and inconsistent formatting suggest potential fraud" }
};

export const customerClaims = [
  { claim_id: "CLM-2024-001", date: "2024-03-15", policy_type: "Health", item_category: "Medical", amount: 2500.0, status: "Under Review", next_step: "Submit medical receipts" },
  { claim_id: "CLM-2024-002", date: "2024-02-28", policy_type: "Auto", item_category: "Collision", amount: 3500.0, status: "Approved", next_step: "Payout scheduled" },
  { claim_id: "CLM-2024-003", date: "2024-01-10", policy_type: "Home", item_category: "Water Damage", amount: 1200.0, status: "Paid", next_step: "Closed" }
];

export const companyQueue = [
  { claim_id: "CLM-2024-004", priority: "High", type: "Auto", amount: 4500.0, submitted: "2024-03-20", combined_risk: "High", nlp_risk: 0.82, document_risk: 0.74, behavioural_risk: 0.81, alert_reason: "Multiple documents show inconsistent vendor details.", assignee: "Anna Johnson" },
  { claim_id: "CLM-2024-005", priority: "Medium", type: "Medical", amount: 3200.0, submitted: "2024-03-19", combined_risk: "Medium", nlp_risk: 0.49, document_risk: 0.52, behavioural_risk: 0.43, alert_reason: "Urgent wording and conflicting provider notes.", assignee: "Unassigned" },
  { claim_id: "CLM-2024-006", priority: "Low", type: "Property", amount: 800.0, submitted: "2024-03-18", combined_risk: "Low", nlp_risk: 0.21, document_risk: 0.18, behavioural_risk: 0.26, alert_reason: "Minor property damage with full receipt match.", assignee: "Mike Chen" }
];

export const liveAlertsSeed = [
  { id: 1, type: "fraud_alert", message: "High-risk claim detected: Amount exceeds policy limit by 200%", timestamp: "2024-03-20T14:30:00Z", severity: "critical" },
  { id: 2, type: "system_alert", message: "Document verification failed for claim CLM-2024-007", timestamp: "2024-03-20T14:15:00Z", severity: "warning" },
  { id: 3, type: "processing_alert", message: "Bulk claim submission detected from single IP address", timestamp: "2024-03-20T14:00:00Z", severity: "info" }
];
