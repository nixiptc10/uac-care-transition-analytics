# UAC Care Transition Efficiency & Placement Outcome Analytics

**U.S. Department of Health and Human Services — Unaccompanied Alien Children Program**

> Reframing the UAC dataset from a capacity monitoring lens to a **process efficiency and outcome evaluation lens** — providing actionable insights for improving reunification timelines, reducing delays, and strengthening child welfare outcomes.

---

## Project Overview

The UAC Program operates as a multi-stage care and reunification pipeline:

```
Apprehension → CBP Custody → HHS Care → Sponsor Placement (Discharge)
```

This project measures **how efficiently children move through each stage**, identifies bottlenecks, and evaluates placement outcome trends across the full dataset (Jan 2023 – Dec 2025, 720 reporting days).

---

## Repository Structure

```
uac-analytics/
├── README.md
├── requirements.txt
├── HHS_Unaccompanied_Alien_Children_Program.csv
├── app.py                  # Streamlit live analytics dashboard
└── research_paper.md       # EDA, insights, recommendations
    executive_summary.md  # Government stakeholder brief
```

---

## Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | **Research Paper** | Full EDA, methodology, KPI analysis, insights, and policy recommendations |
| 2 | **Streamlit Dashboard** | Interactive live analytics with 5 analytical modules |
| 3 | **Executive Summary** | 2-page government stakeholder brief with key findings |

---

## Dashboard Modules

| Tab | Content |
|-----|---------|
| 📊 Pipeline Overview | Daily CBP & HHS census, apprehension vs discharge flows |
| ⚡ Efficiency Metrics | Transfer efficiency, discharge effectiveness, throughput ratios |
| 🚨 Bottleneck Detection | Backlog accumulation, census vs pace comparisons, alert table |
| 📈 Outcome Trends | Monthly discharge volumes, variability, HHS vs placement scatter |
| 🗓️ Temporal Patterns | Weekday/weekend patterns, quarterly comparison, rolling stagnation |

---

## Key Performance Indicators

| KPI | Formula | Dataset Average |
|-----|---------|----------------|
| Transfer Efficiency Ratio | Transfers ÷ CBP Custody | 69.1% |
| Discharge Effectiveness Index | Discharges ÷ HHS Care | 2.37% |
| Pipeline Throughput Rate | (Transfers + Discharges) ÷ Apprehensions | variable |
| Backlog Accumulation | Apprehended − Discharged (daily) | −79.9 (net negative = system clearing) |

---

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/nixiptc10/uac-care-transition-analytics.git
cd uac-care-transition-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit dashboard
python -m streamlit run app.py

```

> The dashboard loads `data/HHS_Unaccompanied_Alien_Children_Program.csv` automatically.

---

## Requirements

See `requirements.txt`. Python 3.8+ recommended.

---

## Data Source

**U.S. Department of Health and Human Services**
Office of Refugee Resettlement — Unaccompanied Alien Children Program
Dataset: Daily operational reporting, January 2023 – December 2025

---

## Academic Context

This project was developed as part of a data analytics coursework deliverable under the guidance of **Unified Mentor**, analyzing process efficiency in child welfare systems using Python-based EDA and Streamlit visualization