# 🎯 AI Account Intelligence & Enrichment System

> Automatically enrich any company name or visitor IP into a full B2B sales intelligence profile — powered by Gemini AI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange)

---

## 🚀 Getting Started
- **Frontend:** `http://localhost:8501`
- **API Docs:** `http://localhost:8000/docs`

---

## 🧠 What It Does

Takes either (a) a website visitor's IP or (b) a company name and enriches it into a full sales intelligence profile with:

| Field | Description |
|---|---|
| 🏢 Company Profile | Name, domain, industry, size, HQ, founding year |
| 📊 Intent Score | 0–10 score + Awareness / Evaluation / Purchase stage |
| 👤 Buyer Persona | Likely title + confidence % |
| 🛠️ Tech Stack | CRM, analytics, marketing tools |
| 👥 Leadership | CEO, VP Sales, Head of Marketing + LinkedIn |
| 📡 Business Signals | Hiring, funding, expansion news |
| 🤖 AI Summary | 3-sentence Gemini-powered sales brief |
| ⚡ Recommended Actions | 3 SDR next steps |

---

## 🏗️ Architecture

```
Visitor IP / Company Name
        │
        ▼
┌─────────────────────────────┐
│     FastAPI /enrich          │
└────────────┬────────────────┘
             │
    ┌────────▼────────┐
    │  core/pipeline  │  ← Master Orchestrator
    └────────┬────────┘
             │
    ┌────────▼──────────────────────────────┐
    │         5 Enrichment Agents           │
    │  ip_resolver   → IPinfo API           │
    │  company_enricher → Clearbit/Scraper  │
    │  tech_detector → BuiltWith/Scraper    │
    │  leadership_finder → Tavily Search    │
    │  signals_agent → Tavily Search        │
    └────────┬──────────────────────────────┘
             │
    ┌────────▼────────┐
    │  core/scorer    │  ← Rules + Gemini AI
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ core/summarizer │  ← Gemini AI
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Streamlit UI   │
    └─────────────────┘
```

---

## ⚙️ Tech Stack

- **Backend:** FastAPI + Uvicorn
- **AI/LLM:** Google Gemini 2.0 Flash
- **Web Search:** Tavily API
- **IP Lookup:** IPinfo API
- **Company Data:** Clearbit API
- **Tech Detection:** BuiltWith + BeautifulSoup scraper
- **Validation:** Pydantic v2
- **Frontend:** Streamlit
- **Deployment:** Render

---

## 🛠️ Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/abhizazu/ai-account-intelligence
cd ai-account-intelligence

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API keys
cp .env.example .env
# Edit .env with your keys

# 5. Start the API (Terminal 1)
uvicorn api.main:app --reload --port 8000

# 6. Start the frontend (Terminal 2)
streamlit run frontend/app.py
```

---

## 📡 API Endpoints

### `POST /enrich`
```json
{
  "company_name": "Figma",
  "page_behavior": {
    "visited_pricing": true,
    "visited_demo": true,
    "repeat_visitor": true,
    "dwell_time_seconds": 340,
    "pages_visited": ["/pricing", "/demo"]
  }
}
```

### `POST /batch`
```json
{
  "company_names": ["Figma", "HubSpot", "Postman"]
}
```

### `GET /health`
```json
{"status": "healthy", "version": "1.0.0"}
```

---

## 📊 Sample Output

```json
{
  "company_name": "Figma",
  "domain": "figma.com",
  "industry": "Design / Collaboration Software",
  "company_size": "201-1000",
  "headquarters": "San Francisco, CA, USA",
  "intent_score": 9.0,
  "intent_stage": "Purchase",
  "persona": {"title": "Head of Product Design", "confidence": 0.88},
  "tech_stack": {"crm": "Salesforce", "analytics": "Amplitude"},
  "leadership": [{"name": "Dylan Field", "title": "CEO"}],
  "business_signals": [{"signal_type": "Hiring", "summary": "..."}],
  "ai_summary": "Figma is in an active purchase stage...",
  "recommended_actions": ["Assign senior AE immediately..."]
}
```

---

## 👨💻 Built By
**Abhishek D N** 
