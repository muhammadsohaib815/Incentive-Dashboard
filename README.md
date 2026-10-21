# DKT Sales Incentive Calculation & Dashboard System

A modular, production-ready Python Flask application for calculating sales incentives, bonuses, and privilege club qualifications across all field designations (SPO, ASM, RSM, TE) and teams (DO, TOUCH, Overlapping, BLISS, GSM).

---

## 📁 Project Architecture & File Organization

The project has been refactored into a clean, layered architecture separating core computation logic, dataset loading, and the Flask web layer:

```
incentive_website/
│
├── core/                           # 🧠 Core Business Logic & Calculations
│   ├── __init__.py                 # Exports calculation engine & data loaders
│   ├── config.py                   # Central configuration: product groups, criteria thresholds, slabs
│   ├── db_loader.py                # PostgreSQL provider for staff, targets, and sales
│   ├── employee_service.py         # Employee lookup, team/designation resolution, ASM/RSM territory rollups
│   ├── engine.py                   # Master calculation engine orchestrating all evaluators and bonuses
│   │
│   ├── evaluators/                 # 🎯 Role & Team Evaluation Logic
│   │   ├── __init__.py             # Module exports
│   │   ├── base.py                 # Base helper for criteria calculations
│   │   ├── do_evaluator.py         # DO Team SPO & ASM evaluations
│   │   ├── touch_evaluator.py      # TOUCH Team SPO & ASM evaluations
│   │   ├── overlapping_evaluator.py# Overlapping SPO & ASM evaluations
│   │   ├── bliss_evaluator.py      # BLISS Team SPO & ASM evaluations
│   │   └── rsm_evaluator.py        # Regional Sales Manager (RSM) 7-criteria evaluations
│   │
│   └── bonuses/                    # 🎁 Bonus & Add-on Calculators
│       ├── __init__.py             # Module exports
│       ├── ucc.py                  # Universal Coverage Criteria (UCC) calculation
│       └── privilege_club.py       # SPO, ASM, and RSM Privilege Club qualification
│
├── templates/                      # 🎨 UI Templates
│   └── index.html                  # Responsive modern dashboard interface
│
├── static/                         # 💅 Static Assets
│   ├── style.css                   # Custom styling & glassmorphic UI components
│   └── header_metrics_icon.png     # Dashboard UI assets
│
├── docs/                           # 📄 Documentation & Reference Policies
│   ├── Trade Scheme Jan 2026.pdf
│   ├── Bliss Scheme Jan 2026.pdf
│   ├── FMCG Policy Jan 2026.pdf
│   └── ...
│
├── tests/                          # 🧪 Test Suite
│   └── test_engine.py              # Automated tests verifying calculations against ground truth
│
├── server.py                       # 🚀 Single Application Entry Point & Web Backend (runs Flask server)
├── requirements.txt                # 📦 Python Dependencies
└── README.md                       # 📖 Project Documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites & Installation

Make sure your Python environment is active, then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Running the Web Dashboard

Start the application with:

```bash
python server.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

Run the test suite to verify calculation accuracy across SPOs, ASMs, and RSMs:

```bash
python tests/test_engine.py
```

---

## 🔍 Key Evaluator Details

1. **SPO Teams (`do_evaluator.py`, `touch_evaluator.py`, `overlapping_evaluator.py`, `bliss_evaluator.py`)**:
   - Calculates target vs. achievement across product categories, brands, and bottom-line figures.
   - Evaluates UCC (Universal Coverage Criteria) bonus and tier qualification.
   - Evaluates Privilege Club eligibility.

2. **ASM Roles**:
   - Aggregates child territory sales and targets under the ASM.
   - Applies ASM-level criteria formulas, bottom-line gates, UCC, and Privilege Club rewards.

3. **RSM Roles (`rsm_evaluator.py`)**:
   - 7 National Criteria: DO Street, TOUCH Street, Trade Bottom-Line, WS Sathi 4s, WS TOUCH, Condom Bottom-Line (DO + TOUCH Street + Trade + WS), and BLISS Bottom-Line.
   - Sathi 4s and TOUCH Bottom-Line target lookup mapped to `WS - SATHI 4S` and `WS - TOUCH`.
   - Privilege Club with 4-out-of-7 minimum qualification gate.
