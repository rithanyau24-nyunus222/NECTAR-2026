"""
CPF Gravity Engine - Core Singapore CPF Simulation & Optimization Logic.
Formulas modeled:
- Ordinary Account (OA): 2.5% per annum
- Special Account (SA): 4.0% per annum
- Extra bonus interest: +1.0% on first $60,000 combined CPF balances (max $20,000 from OA)
- Statutory monthly Ordinary Wage (OW) ceiling enforcement (default $8,000 in 2026)
- Age-banded CPF contribution and allocation schedules
- Housing downpayment liquidity, buffer preservation, and shortfall analysis
"""

from typing import Dict, Any, List, Optional
import numpy as np


# Singapore CPF Base Annual Interest Rates
OA_BASE_RATE: float = 0.025
SA_BASE_RATE: float = 0.040
MA_BASE_RATE: float = 0.040
BONUS_INTEREST_RATE: float = 0.010

# Extra bonus interest caps
BONUS_COMBINED_CAP: float = 60000.0
BONUS_OA_CAP: float = 20000.0

# 2026 Ordinary Wage (OW) Monthly Ceiling in SGD
DEFAULT_OW_CEILING: float = 8000.0


def get_cpf_allocation_rates(age: int) -> Dict[str, float]:
    """
    Returns Singapore statutory CPF employee + employer total contribution rate
    and allocation rates to OA, SA, and MA as a percentage of monthly wage.
    Based on standard CPF Board contribution tables.
    """
    if age <= 35:
        return {
            "total_rate": 0.37,
            "oa_rate": 0.23,
            "sa_rate": 0.06,
            "ma_rate": 0.08,
            "employee_share": 0.20,
            "employer_share": 0.17,
        }
    elif age <= 45:
        return {
            "total_rate": 0.37,
            "oa_rate": 0.21,
            "sa_rate": 0.07,
            "ma_rate": 0.09,
            "employee_share": 0.20,
            "employer_share": 0.17,
        }
    elif age <= 50:
        return {
            "total_rate": 0.37,
            "oa_rate": 0.19,
            "sa_rate": 0.08,
            "ma_rate": 0.10,
            "employee_share": 0.20,
            "employer_share": 0.17,
        }
    elif age <= 55:
        return {
            "total_rate": 0.37,
            "oa_rate": 0.15,
            "sa_rate": 0.115,
            "ma_rate": 0.105,
            "employee_share": 0.20,
            "employer_share": 0.17,
        }
    elif age <= 60:
        return {
            "total_rate": 0.325,
            "oa_rate": 0.12,
            "sa_rate": 0.095,
            "ma_rate": 0.11,
            "employee_share": 0.17,
            "employer_share": 0.155,
        }
    elif age <= 65:
        return {
            "total_rate": 0.235,
            "oa_rate": 0.035,
            "sa_rate": 0.085,
            "ma_rate": 0.115,
            "employee_share": 0.115,
            "employer_share": 0.12,
        }
    elif age <= 70:
        return {
            "total_rate": 0.165,
            "oa_rate": 0.01,
            "sa_rate": 0.045,
            "ma_rate": 0.11,
            "employee_share": 0.075,
            "employer_share": 0.09,
        }
    else:
        return {
            "total_rate": 0.125,
            "oa_rate": 0.01,
            "sa_rate": 0.01,
            "ma_rate": 0.105,
            "employee_share": 0.05,
            "employer_share": 0.075,
        }


def calculate_monthly_bonus_interest(oa_balance: float, sa_balance: float) -> float:
    """
    Calculates the 1% p.a. extra bonus interest for the current month on the first $60,000
    of combined balances (capped at $20,000 for OA).
    Per CPF policy, this bonus interest is credited to the Special Account (SA) for members below 55.
    """
    oa_eligible = min(max(oa_balance, 0.0), BONUS_OA_CAP)
    remaining_cap = max(0.0, BONUS_COMBINED_CAP - oa_eligible)
    sa_eligible = min(max(sa_balance, 0.0), remaining_cap)
    
    total_eligible = oa_eligible + sa_eligible
    monthly_bonus = total_eligible * (BONUS_INTEREST_RATE / 12.0)
    return monthly_bonus


def assess_housing_liquidity(
    projected_oa_at_purchase: float,
    property_price: Optional[float],
    downpayment_pct: float = 0.20,
    retain_oa_buffer: float = 20000.0,
) -> Dict[str, Any]:
    """
    Performs liquidity and downpayment check against projected CPF OA.
    Includes analysis on retaining up to $20k OA buffer to preserve 3.5% effective interest.
    """
    if property_price is None or property_price <= 0:
        return {
            "is_applicable": False,
            "property_price": 0.0,
            "downpayment_pct": downpayment_pct,
            "required_downpayment": 0.0,
            "projected_oa": round(projected_oa_at_purchase, 2),
            "usable_oa": round(projected_oa_at_purchase, 2),
            "retained_buffer": 0.0,
            "shortfall": 0.0,
            "surplus": round(projected_oa_at_purchase, 2),
            "status": "NO_HOUSING_GOAL",
            "recommendation": "No property purchase goal configured.",
        }

    required_downpayment = property_price * downpayment_pct
    usable_oa_with_buffer = max(0.0, projected_oa_at_purchase - retain_oa_buffer)

    if usable_oa_with_buffer >= required_downpayment:
        surplus = usable_oa_with_buffer - required_downpayment
        status = "SUFFICIENT_OA_WITH_BUFFER"
        recommendation = (
            f"You comfortably meet the downpayment of ${required_downpayment:,.2f} via CPF OA "
            f"while preserving a ${retain_oa_buffer:,.2f} buffer earning 3.5% effective interest. "
            f"Remaining OA surplus: ${surplus:,.2f}."
        )
        shortfall = 0.0
    elif projected_oa_at_purchase >= required_downpayment:
        buffer_used = retain_oa_buffer - (projected_oa_at_purchase - required_downpayment)
        status = "SUFFICIENT_OA_BUFFER_SACRIFICED"
        recommendation = (
            f"You can cover the downpayment of ${required_downpayment:,.2f} in full with CPF OA, "
            f"but you will tap into your ${retain_oa_buffer:,.2f} buffer by ${buffer_used:,.2f}, "
            "reducing the 1% bonus interest yield on your OA balance."
        )
        shortfall = 0.0
        surplus = projected_oa_at_purchase - required_downpayment
    else:
        shortfall = required_downpayment - projected_oa_at_purchase
        status = "CASH_SHORTFALL"
        recommendation = (
            f"Projected OA balance (${projected_oa_at_purchase:,.2f}) falls short of "
            f"the required ${required_downpayment:,.2f} downpayment by ${shortfall:,.2f}. "
            "Prepare cash top-ups or explore co-borrower CPF combinations."
        )
        surplus = 0.0

    return {
        "is_applicable": True,
        "property_price": round(property_price, 2),
        "downpayment_pct": downpayment_pct,
        "required_downpayment": round(required_downpayment, 2),
        "projected_oa": round(projected_oa_at_purchase, 2),
        "usable_oa": round(usable_oa_with_buffer, 2),
        "retained_buffer": round(retain_oa_buffer, 2),
        "shortfall": round(shortfall, 2),
        "surplus": round(surplus, 2),
        "status": status,
        "recommendation": recommendation,
    }


def simulate_cpf_trajectory(
    age: int,
    monthly_salary: float,
    current_oa: float,
    current_sa: float,
    current_ma: float = 0.0,
    simulation_years: int = 5,
    annual_salary_increment: float = 0.0,
    ow_ceiling: float = DEFAULT_OW_CEILING,
    property_price: Optional[float] = None,
    downpayment_pct: float = 0.20,
    purchase_year: Optional[int] = None,
    monthly_mortgage_oa: float = 0.0,
    retain_oa_buffer: float = 20000.0,
) -> Dict[str, Any]:
    """
    Simulates monthly progression of CPF accounts (OA, SA, MA) over a multi-year horizon.
    """
    months = simulation_years * 12
    purchase_month = (purchase_year * 12) if purchase_year and purchase_year > 0 else None

    # Trackers
    oa = current_oa
    sa = current_sa
    ma = current_ma
    current_age = age
    salary = monthly_salary

    total_contributions_oa = 0.0
    total_contributions_sa = 0.0
    total_contributions_ma = 0.0
    total_interest_oa = 0.0
    total_interest_sa = 0.0
    total_bonus_interest = 0.0
    housing_downpayment_paid = 0.0
    total_mortgage_paid = 0.0

    projected_oa_at_purchase = None
    yearly_snapshots = []

    # Annual accumulator
    yr_interest_oa = 0.0
    yr_interest_sa = 0.0
    yr_bonus_interest = 0.0
    yr_contrib_oa = 0.0
    yr_contrib_sa = 0.0

    for m in range(1, months + 1):
        # Annual wage adjustment & birthday progression
        if m > 1 and (m - 1) % 12 == 0:
            current_age += 1
            salary *= (1.0 + annual_salary_increment)

        # Statutory CPF Allocation
        capped_wage = min(salary, ow_ceiling)
        rates = get_cpf_allocation_rates(current_age)
        
        m_contrib_oa = capped_wage * rates["oa_rate"]
        m_contrib_sa = capped_wage * rates["sa_rate"]
        m_contrib_ma = capped_wage * rates["ma_rate"]

        oa += m_contrib_oa
        sa += m_contrib_sa
        ma += m_contrib_ma

        yr_contrib_oa += m_contrib_oa
        yr_contrib_sa += m_contrib_sa
        total_contributions_oa += m_contrib_oa
        total_contributions_sa += m_contrib_sa
        total_contributions_ma += m_contrib_ma

        # Housing Downpayment deduction at target month
        if purchase_month and m == purchase_month:
            projected_oa_at_purchase = oa
            if property_price and property_price > 0:
                required_downpayment = property_price * downpayment_pct
                # Max deduct what's available
                deduction = min(oa, required_downpayment)
                oa -= deduction
                housing_downpayment_paid = deduction

        # Ongoing Mortgage deduction from OA if after purchase month
        if purchase_month and m >= purchase_month and monthly_mortgage_oa > 0:
            mortgage_deduction = min(oa, monthly_mortgage_oa)
            oa -= mortgage_deduction
            total_mortgage_paid += mortgage_deduction

        # Monthly Interest Accrual
        # Base interest
        m_interest_oa = oa * (OA_BASE_RATE / 12.0)
        m_interest_sa = sa * (SA_BASE_RATE / 12.0)
        
        # Extra 1% Bonus Interest (credited to SA)
        m_bonus_interest = calculate_monthly_bonus_interest(oa, sa)

        oa += m_interest_oa
        sa += (m_interest_sa + m_bonus_interest)

        yr_interest_oa += m_interest_oa
        yr_interest_sa += m_interest_sa
        yr_bonus_interest += m_bonus_interest

        total_interest_oa += m_interest_oa
        total_interest_sa += m_interest_sa
        total_bonus_interest += m_bonus_interest

        # End of Year Snapshot
        if m % 12 == 0:
            year_num = m // 12
            yearly_snapshots.append({
                "year": year_num,
                "age": current_age,
                "monthly_salary": round(salary, 2),
                "oa_balance": round(oa, 2),
                "sa_balance": round(sa, 2),
                "ma_balance": round(ma, 2),
                "total_cpf": round(oa + sa + ma, 2),
                "annual_contrib_oa": round(yr_contrib_oa, 2),
                "annual_contrib_sa": round(yr_contrib_sa, 2),
                "annual_interest_oa": round(yr_interest_oa, 2),
                "annual_interest_sa": round(yr_interest_sa, 2),
                "annual_bonus_interest": round(yr_bonus_interest, 2),
            })
            yr_interest_oa = 0.0
            yr_interest_sa = 0.0
            yr_bonus_interest = 0.0
            yr_contrib_oa = 0.0
            yr_contrib_sa = 0.0

    # If purchase occurred or was evaluated
    if projected_oa_at_purchase is None:
        projected_oa_at_purchase = oa

    # Milestone checks (2026 CPF benchmarks: BRS ~$106.5k, FRS ~$213k, ERS ~$426k)
    brs_target = 106500.0
    frs_target = 213000.0
    ers_target = 426000.0

    brs_achieved_year = None
    frs_achieved_year = None
    ers_achieved_year = None

    for snap in yearly_snapshots:
        tot = snap["total_cpf"]
        if brs_achieved_year is None and tot >= brs_target:
            brs_achieved_year = snap["year"]
        if frs_achieved_year is None and tot >= frs_target:
            frs_achieved_year = snap["year"]
        if ers_achieved_year is None and tot >= ers_target:
            ers_achieved_year = snap["year"]

    milestones = {
        "brs_target": brs_target,
        "brs_achieved_year": brs_achieved_year,
        "frs_target": frs_target,
        "frs_achieved_year": frs_achieved_year,
        "ers_target": ers_target,
        "ers_achieved_year": ers_achieved_year,
    }

    housing_assessment = assess_housing_liquidity(
        projected_oa_at_purchase=projected_oa_at_purchase,
        property_price=property_price,
        downpayment_pct=downpayment_pct,
        retain_oa_buffer=retain_oa_buffer,
    )

    # Buffer Opportunity Cost (Compounding $20,000 at 3.5% effective yield)
    buffer_val = 20000.0
    eff_rate = 0.035
    buffer_gain_1yr = round(buffer_val * eff_rate, 2)
    buffer_gain_5yr = round(buffer_val * ((1.0 + eff_rate) ** 5 - 1.0), 2)
    buffer_gain_10yr = round(buffer_val * ((1.0 + eff_rate) ** 10 - 1.0), 2)

    return {



        "summary": {
            "initial_total_cpf": round(current_oa + current_sa + current_ma, 2),
            "final_oa_balance": round(oa, 2),
            "final_sa_balance": round(sa, 2),
            "final_ma_balance": round(ma, 2),
            "final_total_cpf": round(oa + sa + ma, 2),
            "total_contributions": round(
                total_contributions_oa + total_contributions_sa + total_contributions_ma, 2
            ),
            "total_interest_earned": round(
                total_interest_oa + total_interest_sa + total_bonus_interest, 2
            ),
            "total_bonus_interest_earned": round(total_bonus_interest, 2),
            "housing_downpayment_paid": round(housing_downpayment_paid, 2),
            "total_mortgage_paid": round(total_mortgage_paid, 2),
            "simulation_years": simulation_years,
            "buffer_metrics": {
                "annual_yield_preserved": buffer_gain_1yr,
                "five_year_yield_preserved": buffer_gain_5yr,
                "ten_year_yield_preserved": buffer_gain_10yr,
            },
        },
        "milestones": milestones,
        "yearly_projections": yearly_snapshots,
        "housing_assessment": housing_assessment,
    }

