import os
import requests
import json
import dotenv

dotenv.load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

prompt = """You are an expert legal analyst. Classify this clause into 1 or more of 14 categories:
1. Party Identification, 2. Purpose, 3. NDA Type, 4. Definition of Confidential Information, 5. Confidentiality Obligations, 6. Authorized Disclosure, 7. Non-Confidential Information, 8. Liability for Damages, 9. Competition Rights, 10. Term and Termination, 11. Intellectual Property, 12. Employees, 13. Governing Law and Jurisdiction, 14. Additional Information.

Return ONLY valid JSON:
{"clause_id": "test_01", "labels": ["Party Identification", "NDA Type"], "confidence": 0.95, "reason": "Identifies parties and agreement type."}

Clause: THIS NON-DISCLOSURE AGREEMENT is made effective as of January 1, 2023, by and between Alpha Corp and Beta Inc."""

models = ["google/gemini-2.5-flash", "meta-llama/llama-3.3-70b-instruct", "qwen/qwen-2.5-72b-instruct"]

for m in models:
    data = {
        "model": m,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.1
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=20)
        content = res.json()["choices"][0]["message"]["content"]
        print(f"Model {m}: SUCCESS ->", content[:150].replace("\n", " "))
    except Exception as e:
        print(f"Model {m}: FAIL ->", e)
