# 🏦 MoMo Data Pipeline

> A fullstack ETL pipeline that processes MTN MoMo SMS transaction data from XML, stores it in SQLite, and visualizes it on an interactive web dashboard.

---

## 👥 Team

**Team Name:** *(To be decided)*

| Name | Role |
|------|------|
| Ange Umukundwa | Team Member |
| Hugue Ishimwe | Team Member |
| Dan Gisa | Team Member |

---

## 📌 Project Description

This project processes raw MTN Mobile Money (MoMo) SMS data exported in XML format. The system cleans and categorizes each transaction, stores it in a SQLite database, and displays the results on an interactive web dashboard with charts and analytics.

### What it does:
- Parses raw MoMo SMS data from an XML file
- Cleans and normalizes dates, amounts, and phone numbers
- Categorizes transactions (incoming, outgoing, payments, etc.)
- Stores structured data in a SQLite database
- Displays analytics and charts on a web dashboard

---

## 🏗️ Architecture Diagram

> 🔗 *Link to be added after diagram is created*

---

## 📋 Scrum Board

> 🔗 *Link to be added after board is set up*

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Data Parsing | Python (ElementTree / lxml) |
| Database | SQLite |
| Backend API | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Version Control | GitHub |

---

## 🚀 Getting Started

> *(Setup instructions will be added as the project develops)*

---

## 📁 Project Structure

```
momo-data-pipeline/
├── README.md                        # Project overview and setup guide
├── .env.example                     # Environment variable template
├── .gitignore                       # Files and folders excluded from GitHub
├── requirements.txt                 # Python dependencies
├── index.html                       # Dashboard entry point
│
├── web/                             # Frontend files
│   ├── styles.css                   # Dashboard styling
│   ├── chart_handler.js             # Fetch and render charts/tables
│   └── assets/                      # Images and icons
│
├── data/                            # All data files
│   ├── raw/                         # Original XML input (git-ignored)
│   │   └── momo.xml
│   ├── processed/                   # Cleaned JSON output (git-ignored)
│   │   └── dashboard.json
│   ├── db.sqlite3                   # SQLite database (git-ignored)
│   └── logs/                        # Generated log files (git-ignored)
│       ├── etl.log
│       └── dead_letter/             # Unparsed XML snippets
│
├── etl/                             # ETL pipeline scripts
│   ├── __init__.py
│   ├── config.py                    # File paths and settings
│   ├── parse_xml.py                 # XML parsing
│   ├── clean_normalize.py           # Data cleaning and normalization
│   ├── categorize.py                # Transaction categorization
│   ├── load_db.py                   # Load data into SQLite
│   └── run.py                       # Run full ETL pipeline
│
├── api/                             # Optional FastAPI backend
│   ├── __init__.py
│   ├── app.py                       # API routes
│   ├── db.py                        # Database connection
│   └── schemas.py                   # Response models
│
├── scripts/                         # Shell scripts
│   ├── run_etl.sh                   # Run the ETL pipeline
│   ├── export_json.sh               # Export dashboard JSON
│   └── serve_frontend.sh            # Serve the frontend locally
│
└── tests/                           # Unit tests
    ├── test_parse_xml.py
    ├── test_clean_normalize.py
    └── test_categorize.py
```

---
