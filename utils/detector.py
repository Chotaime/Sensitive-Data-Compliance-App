import re


def detect_sensitive_data(text):

    patterns = {

        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",

        "Phone": r"(?:\+91[- ]?)?[6-9]\d{9}",

        "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]",

        "Aadhaar": r"\b\d{4}\s\d{4}\s\d{4}\b",

        "Credit Card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",

        "Password": r"(?i)(password\s*[:=]\s*\S+)",

        "API Key": r"(?i)(api[_-]?key\s*[:=]\s*\S+)",

        "Employee ID": r"\bEMP\d+\b"

    }

    detected = {}

    for item, pattern in patterns.items():

        matches = re.findall(pattern, text)

        detected[item] = matches

    return detected