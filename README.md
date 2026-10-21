# DKT Sales Incentive Calculation & Dashboard System

A modular, production-ready FastAPI application for calculating sales incentives, bonuses, and privilege club qualifications across all field designations (SPO, ASM, RSM, TE) and teams (DO, TOUCH, Overlapping, BLISS, GSM).

---

## ðŸ“ Project Architecture & File Organization

The project has been refactored into a clean, layered architecture separating core computation logic, dataset loading, and the FastAPI web layer:

```
incentive_website/
â”‚
â”œâ”€â”€ core/                           # ðŸ§  Core Business Logic & Calculations
â”‚   â”œâ”€â”€ __init__.py                 # Exports calculation engine & data loaders
â”‚   â”œâ”€â”€ config.py                   # Central configuration: product groups, criteria thresholds, slabs
â”‚   â”œâ”€â”€ db_loader.py                # PostgreSQL provider for staff, targets, and sales
â”‚   â”œâ”€â”€ employee_service.py         # Employee lookup, team/designation resolution, ASM/RSM territory rollups
â”‚   â”œâ”€â”€ engine.py                   # Master calculation engine orchestrating all evaluators and bonuses
â”‚   â”‚
â”‚   â”œâ”€â”€ evaluators/                 # ðŸŽ¯ Role & Team Evaluation Logic
â”‚   â”‚   â”œâ”€â”€ __init__.py             # Module exports
â”‚   â”‚   â”œâ”€â”€ base.py                 # Base helper for criteria calculations
â”‚   â”‚   â”œâ”€â”€ do_evaluator.py         # DO Team SPO & ASM evaluations
â”‚   â”‚   â”œâ”€â”€ touch_evaluator.py      # TOUCH Team SPO & ASM evaluations
â”‚   â”‚   â”œâ”€â”€ overlapping_evaluator.py# Overlapping SPO & ASM evaluations
â”‚   â”‚   â”œâ”€â”€ bliss_evaluator.py      # BLISS Team SPO & ASM evaluations
â”‚   â”‚   â””â”€â”€ rsm_evaluator.py        # Regional Sales Manager (RSM) 7-criteria evaluations
â”‚   â”‚
â”‚   â””â”€â”€ bonuses/                    # ðŸŽ Bonus & Add-on Calculators
â”‚       â”œâ”€â”€ __init__.py             # Module exports
â”‚       â”œâ”€â”€ ucc.py                  # Universal Coverage Criteria (UCC) calculation
â”‚       â””â”€â”€ privilege_club.py       # SPO, ASM, and RSM Privilege Club qualification
â”‚
â”œâ”€â”€ templates/                      # ðŸŽ¨ UI Templates
â”‚   â””â”€â”€ index.html                  # Responsive modern dashboard interface
â”‚
â”œâ”€â”€ static/                         # ðŸ’… Static Assets
â”‚   â”œâ”€â”€ style.css                   # Custom styling & glassmorphic UI components
â”‚   â””â”€â”€ header_metrics_icon.png     # Dashboard UI assets
â”‚
â”œâ”€â”€ docs/                           # ðŸ“„ Documentation & Reference Policies
â”‚   â”œâ”€â”€ Trade Scheme Jan 2026.pdf
â”‚   â”œâ”€â”€ Bliss Scheme Jan 2026.pdf
â”‚   â”œâ”€â”€ FMCG Policy Jan 2026.pdf
â”‚   â””â”€â”€ ...
â”‚
â”œâ”€â”€ tests/                          # ðŸ§ª Test Suite
â”‚   â””â”€â”€ test_engine.py              # Automated tests verifying calculations against ground truth
â”‚
â”œâ”€â”€ server.py                       # ðŸš€ Single Application Entry Point & Web Backend (runs FastAPI with Uvicorn)
â”œâ”€â”€ requirements.txt                # ðŸ“¦ Python Dependencies
â””â”€â”€ README.md                       # ðŸ“– Project Documentation
```

---

## ðŸš€ Getting Started

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

## ðŸ§ª Running Automated Tests

Run the test suite to verify calculation accuracy across SPOs, ASMs, and RSMs:

```bash
python tests/test_engine.py
```

---

## ðŸ” Key Evaluator Details

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
