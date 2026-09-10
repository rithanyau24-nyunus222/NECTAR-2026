"""
CPF Gravity Engine - FastAPI Backend
Provides REST endpoints for Singapore CPF multi-year simulation,
interest compounding, wage ceilings, and housing downpayment liquidity assessments.
"""

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.cpf_engine import simulate_cpf_trajectory, DEFAULT_OW_CEILING

app = FastAPI(
    title="CPF Gravity Engine API",
    description="Singapore CPF Liquidity & Wealth Maximizer Prototype",
    version="1.0.0",
)

# Enable CORS for local dev / frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    age: int = Field(..., ge=16, le=100, description="Current age in years")
    monthly_salary: float = Field(..., ge=0.0, description="Monthly gross ordinary salary in SGD")
    current_oa: float = Field(..., ge=0.0, description="Current Ordinary Account (OA) balance")
    current_sa: float = Field(..., ge=0.0, description="Current Special Account (SA) balance")
    current_ma: Optional[float] = Field(0.0, ge=0.0, description="Current Medisave Account (MA) balance")
    simulation_years: Optional[int] = Field(5, ge=1, le=40, description="Projection horizon in years")
    annual_salary_increment: Optional[float] = Field(0.0, ge=0.0, le=0.5, description="Annual wage growth rate (e.g. 0.03 for 3%)")
    ow_ceiling: Optional[float] = Field(DEFAULT_OW_CEILING, ge=0.0, description="CPF Ordinary Wage monthly ceiling in SGD")
    property_price: Optional[float] = Field(None, ge=0.0, description="Target residential property price in SGD")
    downpayment_pct: Optional[float] = Field(0.20, ge=0.0, le=1.0, description="Required downpayment percentage (e.g., 0.20 for HDB)")
    purchase_year: Optional[int] = Field(None, ge=1, le=40, description="Year of property purchase in simulation timeline")
    monthly_mortgage_oa: Optional[float] = Field(0.0, ge=0.0, description="Projected monthly mortgage payable from OA")
    retain_oa_buffer: Optional[float] = Field(20000.0, ge=0.0, description="Target OA buffer to preserve to earn extra 1% bonus interest")


class YearlyProjection(BaseModel):
    year: int
    age: int
    monthly_salary: float
    oa_balance: float
    sa_balance: float
    ma_balance: float
    total_cpf: float
    annual_contrib_oa: float
    annual_contrib_sa: float
    annual_interest_oa: float
    annual_interest_sa: float
    annual_bonus_interest: float


class HousingAssessment(BaseModel):
    is_applicable: bool
    property_price: float
    downpayment_pct: float
    required_downpayment: float
    projected_oa: float
    usable_oa: float
    retained_buffer: float
    shortfall: float
    surplus: float
    status: str
    recommendation: str


class SimulationSummary(BaseModel):
    initial_total_cpf: float
    final_oa_balance: float
    final_sa_balance: float
    final_ma_balance: float
    final_total_cpf: float
    total_contributions: float
    total_interest_earned: float
    total_bonus_interest_earned: float
    housing_downpayment_paid: float
    total_mortgage_paid: float
    simulation_years: int
    buffer_metrics: Optional[Dict[str, float]] = None


class SimulationResponse(BaseModel):
    summary: SimulationSummary
    milestones: Optional[Dict[str, Any]] = None
    yearly_projections: List[YearlyProjection]
    housing_assessment: HousingAssessment



from fastapi.staticfiles import StaticFiles

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    try:
        result = simulate_cpf_trajectory(
            age=req.age,
            monthly_salary=req.monthly_salary,
            current_oa=req.current_oa,
            current_sa=req.current_sa,
            current_ma=req.current_ma or 0.0,
            simulation_years=req.simulation_years or 5,
            annual_salary_increment=req.annual_salary_increment or 0.0,
            ow_ceiling=req.ow_ceiling or DEFAULT_OW_CEILING,
            property_price=req.property_price,
            downpayment_pct=req.downpayment_pct if req.downpayment_pct is not None else 0.20,
            purchase_year=req.purchase_year,
            monthly_mortgage_oa=req.monthly_mortgage_oa or 0.0,
            retain_oa_buffer=req.retain_oa_buffer if req.retain_oa_buffer is not None else 20000.0,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount the frontend directory to serve UI at root (http://127.0.0.1:8000/)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

