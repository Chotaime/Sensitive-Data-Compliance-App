import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Create client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_summary(text, detected, risk_level, risk_score):

    prompt = f"""
You are a Cybersecurity Compliance Assistant.

Analyze the following document.

Document:
{text}

Detected Sensitive Data:
{detected}

Risk Level:
{risk_level}

Risk Score:
{risk_score}

Generate a report with the following sections:

1. Document Summary
2. Sensitive Data Found
3. Compliance Risks
4. Security Risks
5. Recommended Remediation
6. Overall Assessment

Return the response in Markdown format.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text