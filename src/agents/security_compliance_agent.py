import re
from typing import Dict


class SecurityComplianceAgent:

    def __init__(self):
        self.pii_patterns = {
            "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            "phone": r"\b(\+65)?[689]\d{7}\b",
            "nric": r"\b[STFG]\d{7}[A-Z]\b",
            "passport": r"\b[A-Z]\d{7,8}\b",
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "cvv": r"\b(?:cvv|cvc)\s*[:\-]?\s*\d{3,4}\b",
            "bank_account": r"\b\d{8,16}\b",
            "dob": r"\b\d{2}/\d{2}/\d{4}\b"
        }


        self.telco_sensitive_keywords = [
            "otp",
            "one time password",
            "verification code",
            "sim swap",
            "replace sim",
            "port out",
            "esim qr",
            "iccid",
            "imei",
            "account pin",
            "change ownership",
            "transfer number"
        ]


        self.jailbreak_patterns  = [
            r"ignore\s+.*instructions",
            r"reveal\s+system\s+prompt",
            r"developer\s+mode",
            r"bypass\s+security",
            r"disable\s+filter",
            r"override\s+policy",
            "show hidden prompt",
            "act as dan",
            "pretend you are not bound",
            "simulate system"
        ]


    def mask_pii(self, text: str) -> (str, bool):
        pii_found = False

        for label, pattern in self.pii_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                pii_found = True
                text = re.sub(pattern, f"[MASKED_{label.upper()}]", text)

        return text, pii_found


    def detect_telco_risk(self, text: str) -> bool:
        lowered = text.lower()
        for keyword in self.telco_sensitive_keywords:
            if keyword in lowered:
                return True
        return False


    def detect_jailbreak(self, text: str) -> bool:
        lowered = text.lower()
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, lowered):
                return True
        return False


    def process(self, user_input: str) -> Dict:

        cleaned_input, pii_found = self.mask_pii(user_input)
        telco_risk = self.detect_telco_risk(user_input)
        jailbreak_detected = self.detect_jailbreak(user_input)

        risk_level = "low"

        if jailbreak_detected:
            risk_level = "critical"
        elif telco_risk:
            risk_level = "high"
        elif pii_found:
            risk_level = "medium"

        blocked = jailbreak_detected

        return {
            "cleaned_input": cleaned_input,
            "pii_found": pii_found,
            "telco_sensitive_detected": telco_risk,
            "jailbreak_detected": jailbreak_detected,
            "risk_level": risk_level,
            "blocked": blocked
        }
