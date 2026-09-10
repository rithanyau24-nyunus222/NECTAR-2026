<div align="center">

# 🪐 CPF Gravity Engine (NECTAR 2026)
### Quantitative CPF OA $\rightarrow$ SA Yield & Housing Liquidity Optimizer

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Launch_Application-10b981?style=for-the-badge)](https://rithanyau24-nyunus222.github.io/NECTAR-2026/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

### [👉 Click Here to Launch the Live Web App](https://rithanyau24-nyunus222.github.io/NECTAR-2026/)

</div>

---

## 📌 Problem Overview

Singaporeans navigate a structural trade-off between retirement compounding and homeownership liquidity within the Central Provident Fund (CPF):

* **Ordinary Account (OA)** yields **2.5% p.a.** and funds HDB downpayments and monthly mortgage obligations.
* **Special Account (SA)** yields **4.0% p.a.** (plus tiered bonus interest) to accelerate retirement wealth.
* **The Constraint**: Transfers from OA to SA are strictly **irreversible**. Transferring too aggressively risks cash insolvency during property purchases or monthly loan servicing.

**NECTAR 2026 (CPF Gravity Engine)** implements constrained non-linear optimization to determine the exact annual transfer limit that maximizes wealth at age 55 without violating housing cash-flow solvency.

---

## ⚡ Key Highlights

* **Discrete-Event Simulation Engine**: Models monthly compounding, tiered extra interest ($1\%$ on the first $\$60\text{k}$ combined balances, capped at $\$20\text{k}$ for OA), salary ceilings ($\$8\text{,000}/\text{mo}$ OW cap), and statutory age contribution shifts.
* **Bounded Optimization**: Implements `scipy.optimize.minimize_scalar` with an asymptotic penalty barrier function ensuring OA balances remain strictly non-negative throughout housing amortisation.
* **High-Performance Architecture**: Built with a lightweight FastAPI REST API and a responsive front-end dashboard featuring real-time debounced simulation calls and dynamic vector visualizations.

---

## 🛠️ System Architecture & Tech Stack

| Layer | Technologies |
|---|---|
| **Mathematical Engine** | Python 3.11+, SciPy (`minimize_scalar`), NumPy, Pydantic v2 |
| **Backend REST API** | FastAPI, Uvicorn (ASGI) |
| **Frontend Client** | HTML5 Canvas, Modern ES6+ JavaScript (`app.js`), CSS3 (`style.css`) |
| **DevOps & Hosting** | GitHub Pages (Frontend), Docker-ready for Cloud Run |

---

## 🚀 Local Quickstart

### 1. Clone & Set Up Virtual Environment

```bash
git clone [https://github.com/rithanyau24-nyunus222/NECTAR-2026.git](https://github.com/rithanyau24-nyunus222/NECTAR-2026.git)
cd NECTAR-2026

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

