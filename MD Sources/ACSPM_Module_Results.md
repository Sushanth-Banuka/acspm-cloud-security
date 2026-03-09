# ACSPM Module-Wise Coding Results

When the faculty asks for "Module Wise Coding Results," they typically want to see:
1.  **The Module Name**: What part of the system is it? (e.g., Authentication)
2.  **Key Code Function**: The logic that makes it work.
3.  **The Result/Output**: What happens when you run that code? (e.g., "User gets logged in", "IP is extracted").

Below is a structured breakdown you can use for your report or presentation.

---

## Module 1: Secure Authentication Module (`auth.py`)

**Objective:** To verify user identity and prevent unauthorized access.

### 1. Key Code Snippet (Password Hashing)
```python
import hashlib

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
```

### 2. Result / Output
*   **Input:** User enters `admin` / `admin123`.
*   **Process:** System hashes `admin123` -> `a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3`.
*   **Outcome:** If the hash matches the database, the user is redirected to the **Dashboard**.
*   *(Take a screenshot of the Login Page here)*

---

## Module 2: Threat Detection & Extraction Module (`utils.py`)

**Objective:** To automatically identify Indicators of Compromise (IoCs) from raw text.

### 1. Key Code Snippet (Regex Logic)
```python
import re

def extract_indicators(text):
    # Regex pattern for IPv4 Addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    
    # Regex pattern for Email Addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    ips = re.findall(ip_pattern, text)
    emails = re.findall(email_pattern, text)
    
    return {
        "ips": list(set(ips)),
        "emails": list(set(emails))
    }
```

### 2. Result / Output
*   **Input:** "Failed login attempt from 192.168.1.105 by user root@corp.local"
*   **Output (JSON):**
    ```json
    {
        "ips": ["192.168.1.105"],
        "emails": ["root@corp.local"]
    }
    ```
*   *(Take a screenshot of the 'Extracted Indicators' table in the app)*

---

## Module 3: Threat Intelligence Enrichment Module (`utils.py`)

**Objective:** To validate if an IP address is malicious using external APIs (AbuseIPDB).

### 1. Key Code Snippet (API Integration)
```python
import requests

def check_threat_intel(ip, api_key):
    url = 'https://api.abuseipdb.com/api/v2/check'
    headers = {'Key': api_key, 'Accept': 'application/json'}
    params = {'ipAddress': ip, 'maxAgeInDays': '90'}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()['data']
        return {
            "ip": ip,
            "risk_score": data['abuseConfidenceScore'],
            "is_malicious": data['abuseConfidenceScore'] > 20
        }
```

### 2. Result / Output
*   **Input:** IP `118.25.6.39` (Example Malicious IP)
*   **Output (JSON):**
    ```json
    {
        "ip": "118.25.6.39",
        "risk_score": 100,
        "is_malicious": true
    }
    ```
*   *(Take a screenshot of the results table showing a Red/High Risk row)*

---

## Module 4: Automated Reporting & Response Module (`utils.py`)

**Objective:** To generate a PDF report and send an email alert for critical threats.

### 1. Key Code Snippet (PDF Generation)
```python
from fpdf import FPDF

def generate_pdf_report(incident_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.cell(200, 10, txt="ACSPM Incident Report", ln=True, align='C')
    
    # Incident Details
    pdf.cell(200, 10, txt=f"Risk Level: {incident_data['status']}", ln=True)
    pdf.cell(200, 10, txt=f"IPs Detected: {incident_data['ips_found']}", ln=True)
    
    pdf.output("incident_report.pdf")
```

### 2. Result / Output
*   **Trigger:** System detects a "Critical" threat (Score > 50).
*   **Outcome:**
    1.  A PDF file named `incident_2024...pdf` is created in the project folder.
    2.  An email typically arrives in the configured inbox.
*   *(Take a screenshot of the generated PDF file open)*

---

## Module 5: Persistence & History Module (`db.py`)

**Objective:** To save investigation data to a database so it isn't lost.

### 1. Key Code Snippet (SQLite Insertion)
```python
import sqlite3
import json

def add_incident(incident_record):
    conn = sqlite3.connect('app_data.db')
    c = conn.cursor()
    
    # Serialize the list/dict data to JSON string for storage
    c.execute('INSERT INTO incidents (id, time, data, summary) VALUES (?, ?, ?, ?)',
              (incident_record['id'], incident_record['time'], json.dumps(incident_record['data']), incident_record['summary']))
              
    conn.commit()
    conn.close()
```

### 2. Result / Output
*   **Action:** Analysis completes.
*   **Outcome:** A new row appears in the "Strategic Archives" page of the app.
*   *(Take a screenshot of the History/Archives table)*
