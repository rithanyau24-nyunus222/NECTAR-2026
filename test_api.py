"""
Integration test script for CPF Gravity Engine API.
"""

import json
import urllib.request


def test_simulate_endpoint():
    url = "http://127.0.0.1:8000/api/v1/simulate"
    payload = {
        "age": 30,
        "monthly_salary": 6500.0,
        "current_oa": 45000.0,
        "current_sa": 25000.0,
        "current_ma": 15000.0,
        "simulation_years": 5,
        "annual_salary_increment": 0.03,
        "property_price": 500000.0,
        "downpayment_pct": 0.20,
        "purchase_year": 2,
        "monthly_mortgage_oa": 1200.0,
        "retain_oa_buffer": 20000.0,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        assert "summary" in data
        assert "yearly_projections" in data
        assert "housing_assessment" in data
        assert len(data["yearly_projections"]) == 5
        print("API Test Passed Successfully!")
        print("Summary:")
        print(json.dumps(data["summary"], indent=2))
        print("Housing Assessment:")
        print(json.dumps(data["housing_assessment"], indent=2))


if __name__ == "__main__":
    test_simulate_endpoint()
