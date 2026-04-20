# Insurance Claim Samples

I created this file so I can keep a few realistic examples of insurance claim inputs in one place.
I can use these samples to test the UI, demonstrate the product narrative, and explain the fraud-screening logic more clearly.

## Suggested Behavioural Or Claim-History Fields

I recommend starting with a small set of fields that are easy to explain and believable in an insurance claim workflow:

| Field | Meaning | Why I would keep it |
| --- | --- | --- |
| `prior_claims_count` | Number of previous claims by the claimant | I use this to spot repeat claiming behaviour |
| `days_since_policy_start` | How long the policy has been active before the claim | I use this to detect early claims soon after policy purchase |
| `claim_amount_vs_item_value_ratio` | Claimed amount divided by expected item value | I use this to catch inflation or overstatement |
| `recent_high_value_purchase_flag` | Whether the claimant recently showed unusual high-value activity | I use this as a simple behavioural risk signal |
| `late_night_submission_flag` | Whether the claim was submitted at an unusual time | I use this as a weak but useful contextual flag |
| `receipt_mismatch_flag` | Whether the claimed story and receipt details do not align | I use this to connect text and evidence together |
| `duplicate_receipt_flag` | Whether the uploaded receipt appears reused | I use this to detect repeated or fabricated proof |
| `address_change_last_30_days_flag` | Whether the address changed shortly before the claim | I use this as a supporting identity-risk signal |
| `bank_detail_change_last_30_days_flag` | Whether payout details changed recently | I use this to highlight account-change risk |
| `claims_last_12_months` | Number of claims in the last year | I use this to measure short-term claim frequency |

## Sample Claim Email Messages

### 1. Genuine Claim Example

**Subject:** Claim for accidental damage to laptop

Dear Claims Team,

I would like to submit a claim for accidental damage to my laptop under my gadget insurance policy.

On 14 March 2025, I was working at home when I accidentally knocked a glass of water over my desk. The water spilled onto my laptop and the device switched off shortly afterwards. I left it to dry and then took it to a local repair shop the following day, but I was informed that the internal components had been damaged and that repair would not be cost-effective.

I purchased the laptop in September 2024 for university work and I have attached the original purchase receipt and the repair assessment for reference. The device has not previously been damaged and this is the first time I have needed to make a claim on this policy.

Please let me know if you need any further information.

Kind regards,  
Daniel Morgan

### Why this looks genuine

- I give a clear date and event
- I describe a believable sequence of events
- I mention supporting evidence naturally
- I do not push for urgency in an unusual way
- I keep the claimed loss consistent with the story

### 2. Fraudulent Claim Example

**Subject:** Urgent claim request for stolen premium laptop

Dear Insurance,

I need to make an urgent claim for my very expensive laptop which was stolen yesterday evening while I was outside. It was a high-end professional machine worth around £2,400 and I need the full amount paid quickly because I use it for all of my work.

I do not remember the exact time or place because everything happened very fast, but I noticed it was missing when I got home. I have attached the receipt for proof of purchase. I bought the laptop recently and it was in perfect condition. I also need the money sent to my updated bank account because I no longer use the previous one.

Please process this as soon as possible because it is extremely urgent.

Regards,  
Daniel

### Why this looks suspicious

- I stay vague about the incident details
- I emphasise urgency and payout pressure
- I give a high claimed value without much context
- I mention changed bank details during the claim
- I leave room for mismatch between the story and the receipt

## How I Would Use These In The App

I would feed the email text into the NLP model, pass the receipt image into the CV model, and combine the claim-history fields into a simple behavioural risk scorer.
I would then present one final recommendation such as `Low Risk`, `Review Needed`, or `High Risk`.
