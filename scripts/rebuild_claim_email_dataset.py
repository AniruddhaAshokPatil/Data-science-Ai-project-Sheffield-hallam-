import csv
from datetime import date
from datetime import timedelta
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATHS = [
    PROJECT_ROOT / "data" / "raw" / "nlp" / "claim_email_ham_spam.csv",
    PROJECT_ROOT / "data" / "raw" / "insurance_claims" / "claim_email_ham_spam.csv",
]

CSV_COLUMNS = [
    "email_id",
    "claim_id",
    "claimant_name",
    "claimant_email",
    "policy_type",
    "coverage_tier",
    "device_category",
    "incident_type",
    "claim_amount_gbp",
    "device_value_gbp",
    "prior_claims",
    "claims_last_12_months",
    "days_since_policy_start",
    "email_subject",
    "message_body",
    "label",
    "language_risk_band",
    "recent_high_value_purchase_flag",
    "unusual_spend_spike_flag",
    "login_location_changed_flag",
    "multiple_devices_7_days_flag",
    "address_changed_recently_flag",
    "phone_changed_recently_flag",
    "bank_details_changed_recently_flag",
    "late_night_submission_flag",
    "weekend_submission_flag",
    "receipt_present_flag",
    "receipt_mismatch_flag",
    "duplicate_receipt_flag",
    "image_tamper_suspected_flag",
    "urgency_pressure_flag",
    "vague_event_details_flag",
    "payout_pressure_flag",
]

INSURED_ITEMS = [
    ("smartphone", "phone", "Apple", "iPhone 15 Pro", 949),
    ("foldable smartphone", "phone", "Samsung", "Galaxy Z Fold5", 1599),
    ("flagship camera phone", "phone", "Google", "Pixel 8 Pro", 1249),
    ("tablet", "tablet", "Apple", "iPad Pro 12.9", 899),
    ("drawing tablet", "tablet", "Wacom", "Cintiq Pro 16", 1299),
    ("laptop", "laptop", "Dell", "XPS 15", 1499),
    ("gaming laptop", "laptop", "ASUS", "ROG Zephyrus G16", 2299),
    ("MacBook Pro", "laptop", "Apple", "MacBook Pro 16", 2499),
    ("ultrabook", "laptop", "Lenovo", "ThinkPad X1 Carbon", 1399),
    ("desktop workstation", "computer", "HP", "Z2 Tower G9", 2799),
    ("gaming PC tower", "computer", "Corsair", "Vengeance i7400", 2199),
    ("all-in-one computer", "computer", "Apple", "iMac 24", 1699),
    ("4K OLED television", "television", "LG", "OLED C3 65", 1899),
    ("8K television", "television", "Samsung", "QN900C 75", 3299),
    ("laser projector", "home cinema", "Epson", "EH-LS12000B", 1799),
    ("home cinema receiver", "home cinema", "Denon", "AVR-X3800H", 1199),
    ("mirrorless camera", "camera", "Sony", "Alpha A7 IV", 2099),
    ("DSLR camera", "camera", "Canon", "EOS 90D", 1499),
    ("cinema camera body", "camera", "Blackmagic", "Cinema Camera 6K", 3999),
    ("telephoto camera lens", "camera lens", "Nikon", "Z 70-200mm f/2.8", 2499),
    ("drone", "drone", "DJI", "Air 3", 1199),
    ("cinematic drone kit", "drone", "DJI", "Mavic 3 Pro Fly More", 2499),
    ("action camera bundle", "camera", "GoPro", "Hero 12 Creator Edition", 699),
    ("smartwatch", "wearable", "Apple", "Watch Ultra 2", 699),
    ("luxury smartwatch", "wearable", "Garmin", "MARQ Athlete Gen 2", 1299),
    ("fitness tracker bundle", "wearable", "Whoop", "Whoop 4.0 Pro Kit", 449),
    ("VR headset", "vr equipment", "Meta", "Quest 3", 649),
    ("mixed reality headset", "vr equipment", "Apple", "Vision Pro", 3499),
    ("games console", "gaming", "Sony", "PlayStation 5", 549),
    ("handheld gaming console", "gaming", "Valve", "Steam Deck OLED", 599),
    ("pro gaming monitor", "gaming", "Alienware", "AW3423DWF", 999),
    ("graphics card", "computer component", "NVIDIA", "GeForce RTX 4090", 1499),
    ("studio headphones", "audio", "Beyerdynamic", "DT 1990 Pro", 599),
    ("wireless earbuds", "audio", "Sony", "WF-1000XM5", 299),
    ("hi-fi amplifier", "audio", "Naim", "Nait XS 3", 1299),
    ("turntable system", "audio", "Rega", "Planar 6", 899),
    ("digital piano", "music equipment", "Yamaha", "P-525", 1599),
    ("synthesizer", "music equipment", "Korg", "Prologue 16", 1399),
    ("DJ controller", "music equipment", "Pioneer DJ", "DDJ-FLX10", 999),
    ("recording microphone kit", "music equipment", "Shure", "SM7B Studio Bundle", 749),
    ("portable PA speaker", "audio", "Bose", "S1 Pro Plus", 899),
    ("e-bike", "electric mobility", "VanMoof", "S5", 2499),
    ("electric scooter", "electric mobility", "Segway", "Ninebot Max G2", 899),
    ("e-skateboard", "electric mobility", "Evolve", "Hadean Bamboo", 799),
    ("robot vacuum", "smart home", "Roborock", "S8 Pro Ultra", 799),
    ("smart fridge display module", "smart appliance", "Samsung", "Family Hub Panel", 1199),
    ("smart security camera system", "smart home", "Arlo", "Ultra 2 Kit", 899),
    ("network storage server", "computer", "Synology", "DS923 Plus", 1299),
    ("3D printer", "maker equipment", "Bambu Lab", "X1 Carbon Combo", 999),
    ("laser cutter controller", "maker equipment", "Glowforge", "Aura Bundle", 1599),
    ("portable power station", "electronics", "EcoFlow", "Delta 2 Max", 1499),
    ("satellite internet kit", "network equipment", "Starlink", "Standard Kit", 599),
    ("field monitor", "video equipment", "Atomos", "Ninja V Plus", 899),
    ("video switcher", "video equipment", "Blackmagic", "ATEM Mini Extreme ISO", 1299),
    ("thermal imaging camera", "specialist equipment", "FLIR", "E8 Pro", 2199),
    ("surveying tablet", "specialist equipment", "Trimble", "T10x", 1799),
    ("medical-grade laptop", "specialist equipment", "Panasonic", "Toughbook 55 Healthcare", 1999),
    ("barcode scanner set", "business equipment", "Zebra", "DS2278 Kit", 799),
    ("card payment terminal kit", "business equipment", "Square", "Terminal Pro Bundle", 699),
    ("portable label printer fleet", "business equipment", "Brother", "QL-820NWB Bundle", 599),
]

NAMES = [
    "Aisha Khan",
    "Daniel Brooks",
    "Maya Singh",
    "Oliver Turner",
    "Priya Shah",
    "James Wilson",
    "Amelia Green",
    "Thomas Hughes",
    "Sofia Ahmed",
    "Ethan Clarke",
    "Hannah Patel",
    "Noah Evans",
]
INSURERS = ["ShieldWise", "NorthCover", "Harbour Mutual", "CivicSure", "MetroGuard"]
HANDLER_TEAMS = ["gadget_claims", "digital_evidence", "repair_network", "fraud_triage", "customer_claims"]
REGIONS = ["London", "Sheffield", "Manchester", "Leeds", "Birmingham", "Bristol", "Cardiff", "Glasgow", "Edinburgh", "Liverpool"]
CHANNELS = ["portal_email", "mobile_app", "web_portal", "call_centre_followup", "repair_partner_email"]
INCIDENTS = [
    "theft",
    "loss",
    "accidental_damage",
    "water_damage",
    "screen_damage",
    "electrical_fault",
    "liquid_spill",
    "battery_failure",
    "power_surge",
    "malicious_damage",
    "in_transit_damage",
    "accessory_damage",
]
RETAILERS = ["Currys", "John Lewis", "Apple Store", "Amazon UK", "Argos", "Scan Computers", "Wex Photo Video", "Richer Sounds"]
REPAIR_SHOPS = ["iSmash", "Team Knowhow", "Square Repair", "Authorised Service Centre", "Local Repair Partner", "Manufacturer Repair Hub"]
COVERAGE_TIERS = ["standard", "plus", "premium", "business_plus"]
SEGMENTS = ["student", "professional", "family", "creator", "small_business"]

HAM_TEMPLATES = [
    (
        "I would like to submit a claim for my {make} {model}. The incident happened "
        "on {incident_date} in {region}. I have attached the purchase receipt, serial "
        "number photo, and incident photographs. The item was bought from {retailer} "
        "on {purchase_date} for GBP {purchase_price}. Please let me know if you need "
        "any further information."
    ),
    (
        "I am reporting {incident} affecting my insured {item}. The item was purchased "
        "from {retailer} for about GBP {purchase_price}, and the event took place on "
        "{incident_date}. I have included the invoice and repair assessment from "
        "{repair_shop} for review."
    ),
    (
        "Please find the supporting information for my {model} claim. The damage was "
        "noticed on {incident_date} after the incident in {region}. I can provide the "
        "original box, serial number {serial}, and retailer receipt if required."
    ),
    (
        "I need to open a claim for my {item} under my gadget equipment policy. The "
        "details are attached, including proof of ownership, photographs of the "
        "damaged equipment, and a repair quote. The incident date was {incident_date}."
    ),
    (
        "Could this be reviewed as soon as possible please? I use my {model} for work "
        "and need to know whether repair or replacement is covered. I have the serial "
        "number {serial}, photographs, and the {retailer} order confirmation, but I "
        "may need a little time to locate the original PDF receipt."
    ),
    (
        "I am worried because the {item} stopped working after water damage on "
        "{incident_date}. I changed bank accounts recently for normal billing, but "
        "I am happy for any settlement to follow the standard claims process. The "
        "repair quote from {repair_shop} is attached."
    ),
    (
        "This is an urgent claim because the {model} is used for my coursework and "
        "the screen is unusable. I have uploaded photos and can send the receipt from "
        "{retailer}; the purchase was GBP {purchase_price} on {purchase_date}."
    ),
    (
        "I cannot find the box for my {make} {model}, but the device is registered to "
        "my account and the serial number is {serial}. The incident happened on "
        "{incident_date} in {region}. Please advise what evidence is still needed."
    ),
]

SPAM_TEMPLATES = [
    (
        "This is urgent. Approve the full payout for my {item} today and do not delay. "
        "I cannot provide the receipt right now but the item cost GBP {claim_amount}. "
        "Send the money to my new bank details immediately."
    ),
    (
        "I lost my {model} somewhere recently. I need the full amount released without "
        "questions. The date is not important and I have changed my bank account, so "
        "transfer the claim payment today."
    ),
    (
        "Please pay GBP {claim_amount} for my {item} as soon as possible. The receipt "
        "was misplaced and the serial number is unavailable. I need a quick settlement "
        "before the end of today."
    ),
    (
        "My {item} was stolen but I do not have exact details. I need the full payout "
        "urgently. Ignore the old account and use the updated bank details I sent in "
        "the next message."
    ),
    (
        "Hello, I am submitting a claim for my {make} {model}. I believe the loss was "
        "around {region} last week, although I do not have the exact time. The item "
        "was worth GBP {claim_amount}. Please confirm the payment can be made by "
        "bank transfer."
    ),
    (
        "Please review the attached information for my {model}. I have included a "
        "photo and a receipt image. The serial number should be {serial}. If the "
        "documents are not clear, I can resend them after the payment is arranged."
    ),
    (
        "I need to update the payout account before this {item} claim is settled. The "
        "equipment was damaged recently and I am requesting GBP {claim_amount}. I do "
        "not have a repair quote yet, but I can provide one later if required."
    ),
    (
        "The {make} {model} was taken after I left it unattended. I have a purchase "
        "record from {retailer}, but the incident date may be different from the one "
        "on the form. Please process the claim using the replacement value."
    ),
]

HAM_SUBJECTS = [
    "Supporting evidence for {make} {model} claim",
    "Repair assessment attached for {model}",
    "Follow-up documents for gadget claim",
    "Urgent help needed with {model} repair claim",
    "Receipt query for {make} {model}",
    "Claim evidence update for {item}",
]

SPAM_SUBJECTS = [
    "Claim request for {make} {model}",
    "Documents for {model} claim",
    "Payment account update for claim",
    "Urgent payout request for {make} {model} claim",
    "Replacement value request for {item}",
    "Follow-up on gadget equipment claim",
]


def code(prefix, index, width=6):
    return f"{prefix}-{index + 1:0{width}d}"


def serial_for(make, index):
    clean_make = "".join(character for character in make.upper() if character.isalnum())[:4]
    return f"{clean_make}{2025 + index % 2}{index + 10137:06d}"


def email_for(name, index):
    local = name.lower().replace(" ", ".")
    return f"{local}{index % 17}@examplemail.co.uk"


def build_rows(row_count=240):
    rows = []
    start_date = date(2025, 1, 8)

    for index in range(row_count):
        label = "ham" if index < row_count / 2 else "spam"
        item, category, make, model, base_price = INSURED_ITEMS[index % len(INSURED_ITEMS)]
        claimant_name = NAMES[(index * 5) % len(NAMES)]
        incident = INCIDENTS[(index * 5) % len(INCIDENTS)]
        region = REGIONS[(index * 5 + 2) % len(REGIONS)]
        retailer = RETAILERS[(index * 4) % len(RETAILERS)]
        repair_shop = REPAIR_SHOPS[(index * 5) % len(REPAIR_SHOPS)]
        coverage_tier = COVERAGE_TIERS[(index * 2) % len(COVERAGE_TIERS)]
        device_value = base_price + (index % 9) * 45
        claim_amount = round(device_value * (0.72 + (index % 5) * 0.07))
        purchase_date = start_date - timedelta(days=90 + (index * 11) % 900)
        incident_date = start_date + timedelta(days=(index * 4) % 330)
        serial = serial_for(make, index)

        risk_variant = index % 8
        if label == "ham":
            template = HAM_TEMPLATES[risk_variant]
            language_risk_band = ["low", "low", "low", "low", "medium", "medium", "medium", "medium"][risk_variant]
            receipt_flag = 0 if risk_variant in {4, 7} else 1
            urgency_pressure = 1 if risk_variant in {4, 6} else 0
            bank_change = 1 if risk_variant == 5 else 0
            vague_event_details = 1 if risk_variant == 7 else 0
            payout_pressure = 0
            prior_claims = 0 if risk_variant < 4 else 1
            claims_last_12_months = 0 if risk_variant != 5 else 1
            days_since_policy_start = 180 + (index % 8) * 35
            duplicate_receipt = 0
            receipt_mismatch = 0
            image_tamper = 0
            high_value_purchase = 1 if device_value >= 1500 else 0
            unusual_spend = 0
            login_changed = 0
            multiple_devices = 0
            address_changed = 0
            phone_changed = 0
        else:
            template = SPAM_TEMPLATES[risk_variant]
            language_risk_band = ["high", "high", "high", "high", "medium", "medium", "medium", "medium"][risk_variant]
            receipt_flag = 1 if risk_variant in {5, 7} else 0
            urgency_pressure = 1 if risk_variant in {0, 2, 3, 6} else 0
            bank_change = 1 if risk_variant in {0, 1, 3, 6} else 0
            vague_event_details = 1 if risk_variant in {1, 3, 4, 7} else 0
            payout_pressure = 1 if risk_variant in {0, 1, 2, 3, 6, 7} else 0
            prior_claims = 2 if risk_variant < 4 else 1
            claims_last_12_months = 1 if risk_variant in {0, 1, 3, 6} else 0
            days_since_policy_start = 18 if risk_variant < 4 else 75
            duplicate_receipt = 1 if risk_variant == 5 else 0
            receipt_mismatch = 1 if risk_variant in {3, 4, 7} else 0
            image_tamper = 1 if risk_variant in {4, 5} else 0
            high_value_purchase = 1
            unusual_spend = 1 if risk_variant in {0, 2, 6} else 0
            login_changed = 1 if risk_variant in {1, 3} else 0
            multiple_devices = 1 if risk_variant in {0, 6} else 0
            address_changed = 1 if risk_variant == 3 else 0
            phone_changed = 1 if risk_variant in {3, 6} else 0

        body = template.format(
            item=item,
            make=make,
            model=model,
            incident=incident.replace("_", " "),
            incident_date=incident_date.strftime("%d %B %Y"),
            purchase_date=purchase_date.strftime("%d %B %Y"),
            region=region,
            retailer=retailer,
            repair_shop=repair_shop,
            serial=serial,
            purchase_price=device_value,
            claim_amount=claim_amount,
        )
        subject = (HAM_SUBJECTS if label == "ham" else SPAM_SUBJECTS)[index % 6].format(
            item=item,
            make=make,
            model=model,
        )

        rows.append(
            {
                "email_id": code("CLMMAIL", index, 4),
                "claim_id": code("GCLM", index),
                "claimant_name": claimant_name,
                "claimant_email": email_for(claimant_name, index),
                "policy_type": "Gadget Insurance",
                "coverage_tier": coverage_tier.title(),
                "device_category": category,
                "incident_type": incident,
                "claim_amount_gbp": claim_amount,
                "device_value_gbp": device_value,
                "prior_claims": prior_claims,
                "claims_last_12_months": claims_last_12_months,
                "days_since_policy_start": days_since_policy_start,
                "email_subject": subject,
                "message_body": body,
                "label": label,
                "language_risk_band": language_risk_band,
                "recent_high_value_purchase_flag": int(high_value_purchase),
                "unusual_spend_spike_flag": int(unusual_spend),
                "login_location_changed_flag": int(login_changed),
                "multiple_devices_7_days_flag": int(multiple_devices),
                "address_changed_recently_flag": int(address_changed),
                "phone_changed_recently_flag": int(phone_changed),
                "bank_details_changed_recently_flag": int(bank_change),
                "late_night_submission_flag": int(risk_variant in {0, 3}),
                "weekend_submission_flag": int(index % 3 == 0),
                "receipt_present_flag": int(receipt_flag),
                "receipt_mismatch_flag": int(receipt_mismatch),
                "duplicate_receipt_flag": int(duplicate_receipt),
                "image_tamper_suspected_flag": int(image_tamper),
                "urgency_pressure_flag": int(urgency_pressure),
                "vague_event_details_flag": int(vague_event_details),
                "payout_pressure_flag": int(payout_pressure),
            }
        )

    return rows


def write_dataset(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = build_rows()
    for output_path in OUTPUT_PATHS:
        write_dataset(output_path, rows)

    print(f"Wrote {len(rows)} realistic gadget/equipment claim emails.")
    print(f"Columns: {len(CSV_COLUMNS)}")
    for output_path in OUTPUT_PATHS:
        print(output_path)


if __name__ == "__main__":
    main()
