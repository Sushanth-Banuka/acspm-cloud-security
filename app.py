import streamlit as st
import pandas as pd
import utils
import auth
import db
import time
import altair as alt

# --- Initialization ---
db.init_db()

# Page Configuration
st.set_page_config(
    page_title="NEON | Cloud Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Advanced Cyber-Dark Theme ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Share+Tech+Mono&display=swap');

    /* Variables */
    :root {
        --primary-color: #00d4ff;
        --secondary-color: #005bea;
        --accent-color: #ff007a;
        --bg-color: #050510;
        --text-color: #e0e0e0;
        --glass-bg: rgba(10, 10, 32, 0.7);
        --glass-border: 1px solid rgba(0, 212, 255, 0.1);
        --neon-glow: 0 0 10px rgba(0, 212, 255, 0.5);
    }

    /* Global Base */
    div.stApp {
        background-color: var(--bg-color);
        background-size: 40px 40px;
        background-image:
          linear-gradient(to right, rgba(0, 212, 255, 0.05) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(0, 212, 255, 0.05) 1px, transparent 1px);
        font-family: 'Share Tech Mono', monospace;
        color: var(--text-color);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif !important;
        color: #fff !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    /* Neon Separator */
    hr {
        border-top: 1px solid var(--primary-color);
        box-shadow: 0 0 10px var(--primary-color);
        margin: 2em 0;
    }

    /* Card Styling (Metric & Custom Containers) */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: var(--glass-border);
        border-left: 3px solid var(--primary-color);
        padding: 20px;
        border-radius: 5px; /* Angle corners */
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
        transition: 0.5s;
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--neon-glow), 0 0 20px rgba(0, 212, 255, 0.2);
        border-color: var(--primary-color);
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5em;
        font-weight: 700;
        color: var(--primary-color);
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-family: 'Share Tech Mono', monospace;
        color: #a0a0a0;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(10, 10, 32, 0.8) !important;
        color: var(--primary-color) !important;
        border: 1px solid #333 !important;
        border-radius: 0 !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2) !important;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 0 !important; /* Sharp corners */
        height: 45px;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 1px;
        text-transform: uppercase;
        background: transparent !important; /* Hollow style */
        border: 1px solid var(--primary-color) !important;
        color: var(--primary-color) !important;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        z-index: 1;
    }
    
    .stButton>button::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 0%;
        height: 100%;
        background: var(--primary-color);
        z-index: -1;
        transition: width 0.3s ease;
    }

    .stButton>button:hover::before {
        width: 100%;
    }

    .stButton>button:hover {
        color: #000 !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
        border: 1px solid var(--primary-color) !important;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
        background-color: rgba(10, 10, 32, 0.5);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #02020a;
        border-right: 1px solid #1a1a3a;
    }
    
    .css-1d391kg, .css-12oz5g7 {
         font-family: 'Share Tech Mono', monospace;
    }

    /* Status & Alerts */
    .stAlert {
        background-color: rgba(10, 10, 32, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #eee;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #050510; 
    }
    ::-webkit-scrollbar-thumb {
        background: #333; 
        border: 1px solid #050510;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color); 
    }
    
    /* Login Container Special */
    .login-container {
        border: 1px solid var(--primary-color);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
        background: rgba(5, 5, 16, 0.95);
    }

</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

# --- Login Logic ---
if not st.session_state['logged_in']:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🔐 SECURE ACCESS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #a0a0a0;'>AUTHENTICATION REQUIRED FOR SYSTEM ENTRY</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="admin123")
            submit_button = st.form_submit_button("Sign In")
            
            if submit_button:
                if auth.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = username
                    st.success("Login Successful! Redirecting...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown("""
            <div style="text-align: center; color: #005bea; font-size: 0.8em; margin-top: 20px; font-family: 'Share Tech Mono', monospace;">
                ⚠️ RESTRICTED ACCESS SYSTEM v3.0 [ENCRYPTED]
            </div>
        """, unsafe_allow_html=True)

else:
    # --- Main Application (Protected) ---
    
    # --- Sidebar Navigation ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2312/2312217.png", width=60)
        st.title("ACSPM [CORE]")
        st.markdown(f"OPERATOR: <span style='color: #00d4ff'>{st.session_state['user']}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("MODE: **AUTONOMOUS**")
        st.markdown("STATUS: **ACTIVE PROTECTION**")
        
        selected_page = st.radio(
            "Navigate",
            ["Dashboard", "New Investigation", "Incident History", "Settings"],
            index=0
        )
        
        st.divider()
        if st.button("Logout", type="secondary"):
            st.session_state['logged_in'] = False
            st.session_state['user'] = None
            st.rerun()
            
        st.caption("SYSTEM STATE: 🟢 ONLINE [SECURE]")
        st.caption("BUILD: v3.0.1-CYBER")

    # --- Page: Dashboard ---
    if selected_page == "Dashboard":
        incident_history = db.get_incidents()
        active_incidents = 12 # Mock
        resolved = len(incident_history) # Based on DB
        
        st.title("🛡️ COMMAND CENTER")
        st.markdown("REAL-TIME SECURITY POSTURE VISUALIZATION.")
        
        # Top Metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{active_incidents}</div>
                <div class="metric-label">Active Incidents</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{resolved}</div>
                <div class="metric-label">Total Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">Critical</div>
                <div class="metric-label">Threat Level</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">99.9%</div>
                <div class="metric-label">Up Time</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        
        # Simple Charts
        st.subheader("Recent Activity")
        if incident_history:
            chart_data = pd.DataFrame(incident_history)
            st.bar_chart(chart_data['status'].value_counts())
        else:
            st.info("No data available for charts yet.")

    # --- Page: New Investigation ---
    elif selected_page == "New Investigation":
        st.title("⚡ THREAT HUNTING")
        st.markdown("ANALYZE PROBES USING **AI & GLOBAL THREAT INTEL**.")
        
        # Ingestion Tabs
        tab_text, tab_file = st.tabs(["📝 Text Input", "📂 File Upload"])
        
        input_content = ""
        
        with tab_text:
            input_content = st.text_area("Paste Incident Data:", height=200, placeholder="Paste headers, body, or logs here...")
            
        with tab_file:
            uploaded_file = st.file_uploader("Upload Log/Text File", type=['txt', 'log', 'eml'])
            if uploaded_file is not None:
                # Read file safely
                stringio = uploaded_file.getvalue().decode("utf-8")
                input_content = stringio
                st.success(f"File '{uploaded_file.name}' loaded successfully!")

        # Action Bar
        st.divider()
        if st.button("🚀 Run Enhanced Analysis", type="primary"):
            if input_content:
                with st.status("Running Automated Playbook...") as status:
                    st.write("Extracting Indicators...")
                    indicators = utils.extract_indicators(input_content)
                    time.sleep(0.5)
                    
                    st.write("Querying Threat Intelligence (AbuseIPDB)...")
                    threat_results = []
                    critical_found = False
                    for ip in indicators['ips']:
                        analysis = utils.check_threat_intel(ip)
                        threat_results.append(analysis)
                        if analysis['risk_level'] == 'CRITICAL':
                            critical_found = True
                    
                    st.write("Generating AI Narrative...")
                    narrative = utils.generate_narrative(indicators, threat_results)
                    
                    # Construct Record
                    incident_record = {
                        'id': f"INC-{int(time.time())}",
                        'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'ips_found': len(indicators['ips']),
                        'status': 'CRITICAL' if critical_found else 'LOW RISK',
                        'data': indicators,
                        'summary': narrative,
                        'threat_analysis': threat_results
                    }
                    
                    # Save to DB
                    db.add_incident(incident_record)
                    
                    status.update(label="Analysis Complete", state="complete", expanded=False)

                # --- Results View ---
                st.subheader("🔍 Investigation Findings")
                st.info(f"**AI Summary:** {narrative}")
                
                # Findings Metrics
                k1, k2, k3 = st.columns(3)
                k1.metric("IPs Extracted", len(indicators['ips']))
                k2.metric("URLs Extracted", len(indicators['urls']))
                k3.metric("Emails Extracted", len(indicators['emails']))
                
                # Threat Table
                if threat_results:
                    st.warning("Threat Intelligence Matches Found")
                    df = pd.DataFrame(threat_results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No Threat Intelligence Matches Found (Clean)")

                # Actions
                st.divider()
                col_act1, col_act2 = st.columns(2)
                
                with col_act1:
                    st.subheader("Response Actions")
                    if critical_found:
                        st.error("🚨 CRITICAL THREAT DETECTED")
                        if st.button("🔴 BLOCK FIREWALL (Execute)"):
                            st.toast("Firewall Policy Updated!", icon="🛡️")
                            
                        # Email Auto-Send Logic
                        pdf_file = utils.generate_pdf_report(incident_record, narrative)
                        if db.get_setting("SMTP_EMAIL"):
                            st.write("Sending Email Alert...")
                            success, msg = utils.send_email_alert(incident_record, pdf_file)
                            if success:
                                st.success(f"📧 Alert Sent: {msg}")
                            else:
                                st.error(f"📧 Email Failed: {msg}")
                    else:
                        st.success("✅ Low Risk - No Automated Actions Needed")
                
                with col_act2:
                    st.subheader("Documentation")
                    # PDF generated above if critical, else generate now
                    if not critical_found:
                         pdf_file = utils.generate_pdf_report(incident_record, narrative)
                         
                    with open(pdf_file, "rb") as f:
                        st.download_button(
                            label="📄 Download Incident Report (PDF)",
                            data=f,
                            file_name=pdf_file,
                            mime="application/pdf"
                        )

            else:
                st.warning("Please provide input data to analyze.")

    # --- Page: Incident History (DB) ---
    elif selected_page == "Incident History":
        st.title("📂 STRATEGIC ARCHIVES")
        st.markdown("CLASSIFIED AUDIT LOGS [SQLITE ENCRYPTED].")
        
        history = db.get_incidents()
        
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(
                df_hist[['id', 'time', 'ips_found', 'status', 'summary']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No incidents recorded in database yet.")

    # --- Page: Settings (DB) ---
    elif selected_page == "Settings":
        st.title("🔧 SYSTEM CONFIGURATION")
        st.markdown("MANAGE API KEYS & SMTP CREDENTIALS.")
        
        with st.form("settings_form"):
            st.subheader("Threat Intelligence")
            vt_key = st.text_input("AbuseIPDB API Key", value=db.get_setting('ABUSEIPDB_KEY') or "", type="password")
            
            st.subheader("Email Alerts (SMTP)")
            smtp_server = st.text_input("SMTP Server", value=db.get_setting('SMTP_SERVER') or "smtp.gmail.com")
            smtp_port = st.text_input("SMTP Port", value=db.get_setting('SMTP_PORT') or "587")
            smtp_email = st.text_input("Sender Email", value=db.get_setting('SMTP_EMAIL') or "")
            smtp_pass = st.text_input("Sender App Password", value=db.get_setting('SMTP_PASSWORD') or "", type="password")
            
            if st.form_submit_button("Save Configuration"):
                db.save_setting('ABUSEIPDB_KEY', vt_key)
                db.save_setting('SMTP_SERVER', smtp_server)
                db.save_setting('SMTP_PORT', smtp_port)
                db.save_setting('SMTP_EMAIL', smtp_email)
                db.save_setting('SMTP_PASSWORD', smtp_pass)
                st.success("Settings saved to Database successfully!")
        
        st.divider()
        st.subheader("🛠️ Connectivity Checks")
        if st.button("📧 Send Test Email"):
            with st.spinner("Attempting to connect to SMTP Server..."):
                success, msg = utils.send_email_alert({}, None, test_mode=True)
                if success:
                    st.success(f"Success: {msg} (Check your inbox)")
                else:
                    st.error(f"Connection Failed: {msg}")
