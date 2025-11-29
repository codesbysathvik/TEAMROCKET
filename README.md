# TEAMROCKET
Advanced Phishing &amp; Malware Link Analyzer

 ##Problem
Modern phishing attacks use hidden redirects, disguised attachments, and obfuscation techniques that bypass basic filters. Traditional security tools often fail to detect these threats in real time, leaving users vulnerable.

##Challenge
Build a tool or browser extension that:
- Scans links and attachments in **real time**
- Uses **static + dynamic analysis** to detect malicious patterns
- Assigns **threat scores** (Low, Medium, High)
- Displays **clear warning prompts** when risks are detected
- Provides a **dashboard** summarizing all identified threats and overall system safety

##Expected Solution
A system that:
- Performs **real-time analysis** of URLs and attachments
- Assigns **risk levels** with detailed findings
- Warns users immediately via **browser extension alerts**
- Logs threats in a **dashboard** for easy monitoring

##Project Structure
.
├── backend/ # Python API + ML + heuristics
│ ├── app.py # FastAPI/Flask entrypoint
│ ├── features.py # URL feature extractor
│ ├── ml/
│ │ ├── generate_synthetic_data.py
│ │ ├── train_model.py
│ │ └── phish_logreg.joblib
│ └── utils/ # Common helpers
├── extension/ # Browser extension (JS/HTML/CSS)
│ ├── manifest.json
│ ├── popup.html
│ ├── popup.js
│ └── icons/
├── dashboard/ # Web UI for threats
│ ├── index.html
│ └── js/
├── docs/
│ ├── README.md
│ ├── TECH.md
│ └── DEMO.md
└── tests/
└── ...

To effectively detect and respond to advanced phishing and malware threats, this project proposes a modular system with three core components:

Backend (Threat Analysis Engine)
- Performs static analysis on URLs and attachments using pattern matching, domain reputation, and file type checks.
- Implements dynamic analysis using headless browser or sandbox techniques to simulate behavior and detect hidden redirects or payloads.
- Assigns threat scores (Low, Medium, High) based on weighted findings from both static and dynamic checks.
- Stores scan results in a database for logging, auditing, and dashboard display.

Frontend (Dashboard Interface)
- Displays a summary of threats with severity levels and timestamps.
- Shows a detailed table of scanned URLs and attachments, including findings and risk scores.
- Provides a clean, responsive UI built with HTML, CSS, and JavaScript.
- Can be extended to include user authentication, filtering, and export options.

Browser Extension (Real-Time Protection)
- Intercepts link clicks and navigation events in real time.
- Sends URLs to the backend for scanning before allowing access.
- Injects warning banners into web pages when threats are detected.
- Includes a popup interface for manual URL scanning and viewing recent alerts.

System Workflow
- User clicks a link or downloads a file.
- Extension intercepts the action and sends it to the backend.
- Backend performs analysis and assigns a threat score.
- Extension displays a warning if needed, and the frontend dashboard logs the result.
