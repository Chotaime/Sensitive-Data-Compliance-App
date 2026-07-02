def calculate_risk(detected):

    weights = {
        "Email": 1,
        "Phone": 1,
        "PAN": 3,
        "Aadhaar": 4,
        "Credit Card": 5,
        "Password": 5,
        "API Key": 5,
        "Employee ID": 2
    }

    score = 0

    for key, values in detected.items():
        score += len(values) * weights.get(key, 1)

    if score <= 5:
        level = "🟢 Low Risk"
    elif score <= 12:
        level = "🟡 Medium Risk"
    else:
        level = "🔴 High Risk"

    return score, level
