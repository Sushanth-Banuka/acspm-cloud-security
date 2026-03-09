# Project Documentation: Autonomous Cloud Security Posture Management (ACSPM)

## 1. Project Overview
**Title:** Autonomous Cloud Security Posture Management (ACSPM)
**Type:** Web-based Security Orchestration, Automation, and Response (SOAR) Tool.
**Objective:** To automate the detection, analysis, and reporting of security incidents (phishing, malware, suspicious logs) using real-time threat intelligence and AI-driven insights.

---

## 2. Key Features
*   **🔐 Secure Authentication:** Role-based access control with SHA-256 password hashing.
*   **🕶️ Premium Dark UI:** Modern "Glassmorphism" design for a professional Security Operations Center (SOC) feel.
*   **🌐 Real-Time Threat Intelligence:** Integrated with **AbuseIPDB API** to validate IP reputations against global threat databases.
*   **🧠 AI-Powered Analysis:** Logic-based Natural Language Processing (NLP) that generates human-readable executive summaries of technical data.
*   **💾 Persistent Storage:** SQLite database integration ensures incident history and settings are saved permanently.
*   **📧 Automated Response:** Auto-triggers SMTP email alerts with PDF reports when critical threats are detected.
*   **📊 Interactive Dashboard:** Visualizes attack trends, risk distribution, and operational metrics.

---

## 3. System Architecture & Modules
The application follows a modular Model-View-Controller (MVC) pattern:

### A. Frontend (View) - `app.py`
*   Built with **Streamlit**.
*   Handles UI rendering, user input (File Upload/Text), and data visualization (Altair Charts).
*   Manages Session State for navigation and user context.

### B. Authentication (Security) - `auth.py`
*   Manages user sessions.
*   **Algorithm:** SHA-256 Hashing with Salt.
    *   *Why?* To securely store passwords without exposing plain text.
    *   *Flow:* User Input -> Hash -> Compare with DB Hash -> Grant/Deny Access.

### C. Database (Model) - `db.py`
*   **Technology:** SQLite3.
*   **Tables:**
    *   `users`: Stores credentials and roles.
    *   `incidents`: Stores JSON-serialized investigation logs and summaries.
    *   `settings`: Stores encrypted API keys and SMTP credentials.

### D. Core Logic (Controller) - `utils.py`
*   **Indicator Extraction:** identifying IPs, URLs, and Emails from raw logs.
*   **Threat Lookup:** Querying external APIs.
*   **Reporting:** Generating PDF reports using FPDF.

---

## 4. Algorithms & Logic

### A. Artifact Extraction (Regex)
Uses Regular Expressions to parse unstructured text:
*   **IP Extraction:** `\b(?:\d{1,3}\.){3}\d{1,3}\b`
*   **URL Extraction:** Captures standard HTTP/HTTPS patterns.
*   **Email Extraction:** Standard RFC 5322 compliant patterns.

### B. Threat Scoring Algorithm
A composite scoring logic to determine "Risk Level":
1.  **Extract IPs** from input.
2.  **Query API** (AbuseIPDB) for each IP.
3.  **Score Evaluation:**
    *   Abuse Score > 50% → **CRITICAL**
    *   Abuse Score > 20% → **MEDIUM**
    *   Otherwise → **LOW RISK**
4.  **Fallback:** If API fails, checks against a local "Blacklist" of known bad IPs.

### C. AI Narrative Generation
A logic-based text handling algorithm:
*   *Input:* List of threats and counts.
*   *Process:* Evaluates the severity ratio (Malicious vs Total).
*   *Output:* Constructs dynamic sentences (e.g., *"CRITICAL FINDINGS: 2 malicious IPs were identified..."*) rather than static templates.

---

## 5. Working Mechanism (Workflow)
1.  **Ingestion:** User logs in and uploads a log file (or pastes text) into the "New Investigation" tab.
2.  **Extraction:** The system parses the text and isolates potential Indicators of Compromise (IoCs).
3.  **Enrichment:** The system queries the Global Threat Database for reputation data on the found IPs.
4.  **Analysis:** The logic engine calculates a Threat Score and generates an AI summary.
5.  **Storage:** The full record is permanently saved to the SQLite database.
6.  **Response:**
    *   If **CRITICAL**: The system flashes a Red Alert, enables the "Block Firewall" response, and auto-sends an email report to the administrator.
    *   If **SAFE**: It displays a Green status.

---

## 6. Applications & Use Cases
*   **Security Operations Centers (SOC):** For Level 1 analysts to quickly triage suspicious emails or logs.
*   **Network Administration:** To verify if an external IP connecting to the server is malicious.
*   **Forensics:** To parse large log files and extract readable data instantly.
*   **Educational Demo:** To demonstrate how automated security tools process data.
