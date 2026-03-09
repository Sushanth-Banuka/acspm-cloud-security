import re
import smtplib
import requests
import json
import db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF
from datetime import datetime

# Global Blacklist for Simulation/Fallback
BLACKLIST_IPS = [
    "192.168.1.105",
    "10.0.0.99",
    "203.0.113.5",
    "198.51.100.23",
    "172.16.0.42"
]

def extract_indicators(text):
    """
    Extracts IP addresses, URLs, and Email addresses from the provided text using regex.
    """
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    ips = re.findall(ip_pattern, text)
    urls = re.findall(url_pattern, text)
    emails = re.findall(email_pattern, text)

    return {
        "ips": list(set(ips)),
        "urls": list(set(urls)),
        "emails": list(set(emails))
    }

def check_threat_intel(ip):
    """
    Checks IP reputation using AbuseIPDB if API key exists, else checks local blacklist.
    """
    # 1. ALWAYS check Simulation Blacklist first (Override for Demo)
    if ip in BLACKLIST_IPS:
        return {
            "ip": ip,
            "is_malicious": True,
            "risk_level": "CRITICAL",
            "details": "Match found in Local Blacklist DB (SIMULATION)"
        }
        
    api_key = db.get_setting('ABUSEIPDB_KEY')
    
    # 2. Real API Check
    if api_key:
        try:
            url = 'https://api.abuseipdb.com/api/v2/check'
            querystring = {'ipAddress': ip, 'maxAgeInDays': '90'}
            headers = {'Key': api_key, 'Accept': 'application/json'}
            response = requests.request(method='GET', url=url, headers=headers, params=querystring)
            
            if response.status_code == 200:
                data = response.json()['data']
                score = data['abuseConfidenceScore']
                return {
                    "ip": ip,
                    "is_malicious": score > 20,
                    "risk_level": "CRITICAL" if score > 50 else ("MEDIUM" if score > 20 else "LOW RISK"),
                    "details": f"AbuseIPDB Score: {score}% | Usage: {data.get('usageType', 'Unknown')}"
                }
        except Exception as e:
            print(f"API Error: {e}")
            
    return {
        "ip": ip,
        "is_malicious": False,
        "risk_level": "LOW RISK",
        "details": "Clean (Simulation/No API Key)"
    }

def generate_narrative(indicators, threats):
    """
    Generates a natural language summary of the investigation.
    """
    ip_count = len(indicators['ips'])
    malicious_count = len([t for t in threats if t['is_malicious']])
    
    summary = f"Investigation Report generated on {datetime.now().strftime('%Y-%m-%d')}. "
    summary += f"The automated system analyzed {ip_count} unique IP addresses, {len(indicators['urls'])} URLs, and {len(indicators['emails'])} emails. "
    
    if malicious_count > 0:
        summary += f"CRITICAL FINDINGS: {malicious_count} malicious IPs were identified. "
        summary += "Immediate containment is recommended. "
        for t in threats:
            if t['is_malicious']:
                summary += f"IP {t['ip']} is flagged as {t['risk_level']} ({t['details']}). "
    else:
        summary += "No significant threats were detected in the analyzed artifacts. "
        summary += "The indicators appear to be benign based on current intelligence."
        
    return summary

def send_email_alert(report_data, pdf_path=None, test_mode=False):
    """
    Sends an email alert using SMTP settings from DB.
    Handles both SSL (465) and TLS (587).
    """
    smtp_server = db.get_setting('SMTP_SERVER')
    # Default to 587 if not set or empty
    port_val = db.get_setting('SMTP_PORT')
    smtp_port = int(port_val) if port_val else 587
    
    smtp_email = db.get_setting('SMTP_EMAIL')
    smtp_password = db.get_setting('SMTP_PASSWORD')
    
    if not (smtp_server and smtp_email and smtp_password):
        return False, "SMTP Settings missing in configuration."
        
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = smtp_email # Sending to self
        
        if test_mode:
             msg['Subject'] = "✅ SYSTEM ALERT: SMTP CONNECTION ESTABLISHED"
             body = "SECURE CHANNEL VERIFIED. READY FOR TRANSMISSION."
        else:
            msg['Subject'] = f"🚨 SECURITY BREACH PROTOCOL INITIATED"
            body = f"""
            *** AUTOMATED THREAT REPORT ***
            --------------------------------
            CRITICAL ANOMALY DETECTED. IMMEDIATE ACTION REQUIRED.
            
            Analysis Summary:
            {report_data.get('summary', 'No summary available.')}
            
            Please find the full technical report attached.
            """
            
        msg.attach(MIMEText(body, 'plain'))
        
        if pdf_path:
            with open(pdf_path, "rb") as f:
                attach = MIMEApplication(f.read(),_subtype="pdf")
                attach.add_header('Content-Disposition','attachment',filename=str(pdf_path).split('/')[-1])
                msg.attach(attach)
        
        # Connect logic
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully."
        
    except Exception as e:
        return False, f"Email failed: {str(e)}"

def generate_pdf_report(incident_data, narrative=None):
    """
    Generates a PDF report for the incident.
    """
    if narrative is None:
        narrative = "No summary generated."

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ACSPM Incident Report", ln=True, align='C')
    pdf.ln(10)

    # Meta
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Report ID: {incident_data.get('id', 'N/A')}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    
    # Executive Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Executive Summary", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=narrative)
    pdf.ln(10)

    # Threat Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Technical Analysis:", ln=True)
    pdf.set_font("Arial", size=11)
    
    if incident_data.get('threat_analysis'):
        for threat in incident_data['threat_analysis']:
            status = "[MALICIOUS]" if threat['is_malicious'] else "[CLEAN]"
            pdf.cell(200, 10, txt=f"{status} {threat['ip']} - {threat['details']}", ln=True)
    else:
         pdf.cell(200, 10, txt="No Threat Data Available", ln=True)

    file_name = f"incident_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = f"e:/MRU/App Devlopment Projects/Major Project/project 1/{file_name}" 
    pdf.output(file_name) 
    return file_name
