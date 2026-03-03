# 🤖 AI Call Analysis & Automation Agent

An end-to-end Python automation agent that leverages **Generative AI** to analyze client conversations, log outcomes to **Google Sheets**, and prepare follow-up drafts in **Gmail**.

---

## 🌟 Overview
This project solves the "follow-up fatigue" problem for sales and support teams. Instead of manually logging call notes and writing follow-up emails, this agent handles the entire post-call workflow in seconds.

### 🚀 Key Features
- **Sentiment Analysis:** Uses **Gemini 2.5 Flash** to determine if a client said "YES" or "NO".
- **Database Integration:** Automatically appends call details, timestamps, and AI summaries to **Google Sheets**.
- **Pending Follow-ups:** Generates context-aware email drafts in **Gmail** based on the call outcome.
- **Secure Auth:** Implements **OAuth 2.0** for secure access to Google Cloud Services.

---

## 🛠️ Tech Stack
- **Language:** Python 3.11+
- **AI Model:** Google Gemini API
- **APIs:** Google Sheets API v4, Gmail API v1
- **Libraries:** `google-auth-oauthlib`, `google-api-python-client`, `google-genai`

---

## 📸 Demo & Screenshots
*(Add your screenshots here! Tip: Upload them to a folder named 'screenshots' in this repo)*

1. **AI Analysis Logic:**
![AI Analysis](./screenshots/analysis_result.png)

2. **Automated Google Sheet Log:**
![Google Sheets](./screenshots/sheets_log.png)

3. **Contextual Gmail Draft:**
![Gmail Draft](./screenshots/gmail_draft.png)

---

## ⚙️ Setup & Installation

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd AI-CALLER-outcome-agent
