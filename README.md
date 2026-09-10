# 🍯 NECTAR'26 — Singapore CPF Liquidity & Wealth Engine

> A cute, human-friendly fintech prototype that turns bureaucratic Singapore Central Provident Fund (CPF) statutory rules into a high-precision wealth and housing liquidity optimization engine.

![NECTAR'26 Cute Singapore CPF Simulator](frontend/assets/stickers/merlion_sticker.svg)

---

## 💡 What It Does
In Singapore, up to **37% of monthly income** is locked into the Central Provident Fund (CPF). While it's the largest forced-savings vehicle for citizens, young home-buyers frequently fall into the **"OA Wipeout Trap"**—emptying their Ordinary Account to $0 for home downpayments and unknowingly sacrificing **$3,750 to $8,200+** in government bonus interest.

**NECTAR'26** models exact statutory allocation rules, multi-year compounding, and housing downpayment liquidity in real-time, helping users protect their capital while avoiding surprise cash shortfalls for BTO and resale flats.

---

## 🛠️ Technical Architecture & Approach

- **Discrete-Time Simulation Engine**:
  Built with **Python 3.14** and **NumPy**, the engine models month-by-month cashflow iterations over a 1-to-20 year projection horizon. It simulates statutory employee/employer wage deductions, Ordinary Wage (OW) ceiling caps (calibrated to the 2026 $8,000 statutory limit), and age-banded allocation schedules across OA, SA, and MA.

- **Dynamic Interest & Allocation Algorithm**:
  Implements the complex non-linear **1.0% extra bonus interest** protocol on the first $60,000 of combined CPF balances (capped at $20,000 for OA), factoring in monthly compounding, opportunity cost matrices, and automatic routing of bonus yield to the Special Account (SA).

- **Constrained Liquidity & Buffer Optimization**:
  Features a liquidity stress-testing module that evaluates downpayment requirements (20% HDB Concessionary vs. 25% Bank loans) against projected usable OA, computing the exact opportunity cost of draining vs. preserving the **$20,000 OA buffer** (earning 3.5% effective risk-free yield).

- **High-Performance Asynchronous REST API**:
  Built using **FastAPI** and **Pydantic v2** for strict schema validation, sub-millisecond endpoint responses, and auto-generated OpenAPI documentation.

- **Human-Centric Client Experience**:
  Responsive multi-page single-page application (SPA) featuring custom HTML5 Canvas vector curves, real-time debounced simulation calls, and a whimsical scrapbook aesthetic inspired by modern creative studios with custom Singapore-themed vector stickers.

---

## 🚀 Quickstart

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/nectar-sg-2026.git
cd nectar-sg-2026

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Run the Application
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
- **Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📁 Repository Structure

```
NECTAR SG 2026/
├── backend/
│   ├── cpf_engine.py       # Core mathematical formulas & simulation logic
│   ├── main.py             # FastAPI backend with REST endpoints & static mount
│   ├── requirements.txt    # Python dependencies
│   └── test_api.py         # Automated integration test script
├── frontend/
│   ├── assets/             # Generated stickers and visuals
│   ├── index.html          # Multi-page scrapbook layout
│   ├── style.css           # Cute pastel design system & washi tape styles
│   └── app.js              # Client-side router, debounced calls & canvas chart
├── .gitignore              # Ignores venv and temporary files
└── README.md               # Project documentation
```

---

## 📜 License
MIT License. Built for Singapore CPF education and wealth planning.
