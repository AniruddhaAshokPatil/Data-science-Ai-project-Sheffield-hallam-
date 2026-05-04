export const publicFeatures = [
  { title: "Device Claim Screening", description: "Laptop, phone, tablet, camera, and console claims are checked using language, behaviour, and evidence signals.", icon: "device" },
  { title: "Receipt and ID Evidence", description: "Purchase receipts, repair invoices, and claimant ID cards are handled together in the claim workflow.", icon: "document" },
  { title: "Real-Time Review Alerts", description: "Investigators receive live updates when a gadget claim needs closer fraud review.", icon: "alert" },
  { title: "Explainable Risk Signals", description: "The dashboard shows why a device claim may need review, including receipt mismatch, duplicate evidence, or recent account changes.", icon: "review" }
];

export const behaviouralFieldCards = [
  { field: "Device Claim Frequency", value: "2.3x average", risk: "high", description: "The claimant has submitted more gadget claims than a typical policyholder" },
  { field: "High-Value Device Pattern", value: "Escalating", risk: "medium", description: "Recent claims involve increasingly expensive laptops, phones, or tablets" },
  { field: "Receipt Quality", value: "Inconsistent", risk: "high", description: "Submitted purchase evidence may not match the device details or claim value" },
  { field: "Submission Timing", value: "Unusual", risk: "medium", description: "The device claim was submitted at an unusual time or close to account changes" }
];

export const claimEmailSamples = {
  genuine: { subject: "Claim for accidental laptop damage", from: "policyholder@example.com", body: "Dear Claims Team,\n\nThis message submits a claim for accidental damage to my laptop under my gadget policy. A drink spilled on the device on 14 March 2025, and the attached documents include the purchase receipt and repair assessment.\n\nKind regards,\nDaniel Morgan", risk_score: 15, analysis: "Clear gadget claim with dates, device details, and matching evidence" },
  suspicious: { subject: "URGENT: Need full payout for stolen laptop", from: "claimant@urgent-mail.com", body: "HELLO INSURANCE!!!\n\nMY EXPENSIVE LAPTOP WAS STOLEN AND I NEED MONEY FAST. I CANNOT REMEMBER THE EXACT PLACE BUT THE RECEIPT IS ATTACHED. SEND THE FULL PAYMENT TO MY NEW BANK ACCOUNT TODAY!!!\n\nTHANKS,\nJANE SMITH", risk_score: 85, analysis: "High-pressure wording, vague incident details, and recent payout change suggest review is needed" }
};

export const customerClaims = [
  { claim_id: "CLM-2024-001", date: "2024-03-15", policy_type: "Gadget Premium", item_category: "Laptop", amount: 1499.0, status: "Under Review", next_step: "Upload repair assessment" },
  { claim_id: "CLM-2024-002", date: "2024-02-28", policy_type: "Device Protection Plus", item_category: "Phone", amount: 899.0, status: "Approved", next_step: "Payout scheduled" },
  { claim_id: "CLM-2024-003", date: "2024-01-10", policy_type: "Electronics Warranty", item_category: "Tablet", amount: 650.0, status: "Paid", next_step: "Closed" }
];

export const companyQueue = [
  { claim_id: "CLM-2024-004", priority: "High", type: "Laptop", amount: 2400.0, submitted: "2024-03-20", combined_risk: "High", nlp_risk: 0.82, document_risk: 0.74, behavioural_risk: 0.81, alert_reason: "Receipt merchant and claimed device value do not fully match.", assignee: "Anna Johnson" },
  { claim_id: "CLM-2024-005", priority: "Medium", type: "Phone", amount: 1150.0, submitted: "2024-03-19", combined_risk: "Medium", nlp_risk: 0.49, document_risk: 0.52, behavioural_risk: 0.43, alert_reason: "Urgent wording and recent bank-detail change.", assignee: "Unassigned" },
  { claim_id: "CLM-2024-006", priority: "Low", type: "Tablet", amount: 620.0, submitted: "2024-03-18", combined_risk: "Low", nlp_risk: 0.21, document_risk: 0.18, behavioural_risk: 0.26, alert_reason: "Accidental damage claim with matching receipt and repair note.", assignee: "Mike Chen" }
];

export const liveAlertsSeed = [
  { id: 1, type: "fraud_alert", message: "High-risk laptop claim detected: claimed value exceeds expected device value.", timestamp: "2024-03-20T14:30:00Z", severity: "critical" },
  { id: 2, type: "system_alert", message: "Receipt verification needs review for claim CLM-2024-007.", timestamp: "2024-03-20T14:15:00Z", severity: "warning" },
  { id: 3, type: "processing_alert", message: "Multiple gadget claims submitted from recently changed account details.", timestamp: "2024-03-20T14:00:00Z", severity: "info" }
];
