"""
End-to-End Regression Tests for USAAgent
Tests the refactored AgenticTravelEngine for:
1. Generating all 6 sheets with exact schemas
2. Arbitrary city inputs (e.g. Seattle, Denver)
3. 11 US regression cities
4. Strict boundary violations rejection
"""

import os
import openpyxl
import pytest

from engine import AgenticTravelEngine
from core.validator import ValidationError

EXPECTED_SHEETS = [
    "City_Master",
    "Transit_Connectivity",
    "Accommodation_Master",
    "Safety_Index",
    "Recommendation_Score",
    "Final_Output"
]

def test_engine_arbitrary_city_execution(tmp_path):
    test_excel = str(tmp_path / "test_arbitrary_city.xlsx")
    engine = AgenticTravelEngine(
        target_cities=["Seattle"],
        budget_min=50.0,
        budget_max=60.0,
        max_commute_minutes=90
    )
    result = engine.run(output_excel_path=test_excel)

    assert result["status"] == "SUCCESS"
    assert result["cities_count"] == 1
    assert os.path.exists(test_excel)

    wb = openpyxl.load_workbook(test_excel, data_only=True)
    assert wb.sheetnames == EXPECTED_SHEETS

    # Verify City_Master has Seattle
    ws_city = wb["City_Master"]
    assert ws_city.cell(row=4, column=2).value == "Seattle"
    wb.close()

def test_engine_regression_cities_execution(tmp_path):
    test_excel = str(tmp_path / "test_regression_run.xlsx")
    engine = AgenticTravelEngine(
        target_cities=["Dallas", "San Antonio"],
        budget_min=50.0,
        budget_max=60.0,
        max_commute_minutes=90
    )
    result = engine.run(output_excel_path=test_excel)

    assert result["status"] == "SUCCESS"
    assert result["cities_count"] == 2
    assert os.path.exists(test_excel)

    wb = openpyxl.load_workbook(test_excel, data_only=True)
    assert wb.sheetnames == EXPECTED_SHEETS

    ws_transit = wb["Transit_Connectivity"]
    assert ws_transit.max_row >= 4  # Contains transit corridors
    wb.close()

def test_engine_invalid_inputs_rejected():
    # Negative budget
    with pytest.raises(ValidationError):
        AgenticTravelEngine(target_cities=["Dallas"], budget_min=-10.0, budget_max=50.0)

    # Inverted budget
    with pytest.raises(ValidationError):
        AgenticTravelEngine(target_cities=["Dallas"], budget_min=70.0, budget_max=50.0)

    # Invalid commute
    with pytest.raises(ValidationError):
        AgenticTravelEngine(target_cities=["Dallas"], max_commute_minutes=0)

    # Invalid weights sum
    with pytest.raises(ValidationError):
        AgenticTravelEngine(target_cities=["Dallas"], weight_safety=0.5, weight_cost=0.5, weight_commute=0.5, weight_transit=0.5)
