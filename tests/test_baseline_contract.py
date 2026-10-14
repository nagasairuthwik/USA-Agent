import os
import openpyxl
import pytest
from engine import AgenticTravelEngine

def test_baseline_engine_imports_and_instantiates():
    eng = AgenticTravelEngine(target_cities=["Dallas"], budget_min=50.0, budget_max=70.0)
    assert eng.budget_min == 50.0
    assert eng.budget_max == 70.0
    assert eng.target_cities == ["Dallas"]

def test_workbook_sheets_and_headers_contract():
    wb_path = os.path.join(os.path.dirname(__file__), "..", "Travel_Intelligence_Master_Workbook.xlsx")
    assert os.path.exists(wb_path), "Master workbook must exist"
    wb = openpyxl.load_workbook(wb_path)
    expected_sheets = [
        "City_Master",
        "Transit_Connectivity",
        "Accommodation_Master",
        "Safety_Index",
        "Recommendation_Score",
        "Final_Output"
    ]
    assert wb.sheetnames == expected_sheets

    # Verify sheet 1 headers
    s1_headers = [c.value for c in wb["City_Master"][3] if c.value is not None]
    assert "City_ID" in s1_headers
    assert "City" in s1_headers
    assert "Downtown_District" in s1_headers

    # Verify sheet 2 headers
    s2_headers = [c.value for c in wb["Transit_Connectivity"][3] if c.value is not None]
    assert "Commute_Minutes" in s2_headers
    assert "Nearest_Station" in s2_headers

    # Verify sheet 3 headers
    s3_headers = [c.value for c in wb["Accommodation_Master"][3] if c.value is not None]
    assert "Hotel_Name" in s3_headers
    assert "Base_Nightly_Rate_USD" in s3_headers

    # Verify sheet 4 headers
    s4_headers = [c.value for c in wb["Safety_Index"][3] if c.value is not None]
    assert "Safety_Score" in s4_headers
    assert "Crime_Index" in s4_headers

    # Verify sheet 5 headers
    s5_headers = [c.value for c in wb["Recommendation_Score"][3] if c.value is not None]
    assert "Overall_Score" in s5_headers
    assert "Rank" in s5_headers

    # Verify sheet 6 headers
    s6_headers = [c.value for c in wb["Final_Output"][3] if c.value is not None]
    assert "Recommended_Locality" in s6_headers
    assert "Overall_Score" in s6_headers
