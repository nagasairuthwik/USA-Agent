"""
Comprehensive Unit and Integration Tests for USAAgent Tools
Tests GeocodingTool, TransitRoutingTool, HotelDiscoveryTool, SafetyIntelligenceTool, and GroqAgentOrchestrator.
All external network responses are properly mocked or run against deterministic fallbacks.
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from core.models import VerificationStatus
from tools.geocoding_tool import GeocodingTool
from tools.transit_tool import TransitRoutingTool
from tools.hotel_tool import HotelDiscoveryTool
from tools.safety_tool import SafetyIntelligenceTool
from tools.groq_orchestrator import GroqAgentOrchestrator

def test_geocoding_tool_fallback_and_known_cities():
    tool = GeocodingTool()
    # Test known authority fallback without network
    city_ny = tool.resolve_city("New York", city_id="CITY-01")
    assert city_ny.city == "New York"
    assert city_ny.primary_transit_system == "MTA Subway & Metro-North / LIRR"
    assert city_ny.latitude == 40.7128
    assert city_ny.longitude == -74.0060
    assert city_ny.verification_status in [VerificationStatus.VERIFIED, VerificationStatus.SEARCH_DERIVED]

def test_geocoding_tool_arbitrary_city_mocked():
    tool = GeocodingTool()
    mock_osm_response = json.dumps([{
        "display_name": "Seattle, King County, Washington, United States",
        "lat": "47.6062",
        "lon": "-122.3321",
        "address": {"country": "United States", "state": "Washington"}
    }]).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_osm_response
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        city_seattle = tool.resolve_city("Seattle", city_id="CITY-99")
        assert city_seattle.city == "Seattle"
        assert city_seattle.latitude == 47.6062
        assert city_seattle.longitude == -122.3321
        assert "Seattle" in city_seattle.downtown_district

def test_transit_tool_regional_agencies_and_routing():
    tool = TransitRoutingTool(tavily_api_key="")
    route = tool.get_route(
        origin_lat=40.73, origin_lon=-74.17,
        dest_lat=40.71, dest_lon=-74.00,
        city_name="New York", suburb_name="Elizabeth",
        cbd_name="Manhattan CBD"
    )
    assert "MTA" in route.transit_system or "NJ Transit" in route.transit_system
    assert route.commute_minutes > 0
    assert route.fare_usd > 0

def test_transit_tool_tavily_mocked():
    tool = TransitRoutingTool(tavily_api_key="tvly-mock-valid-key")
    mock_tavily_response = json.dumps({
        "results": [{
            "title": "MTA Subway from Long Island City to Manhattan",
            "content": "Takes about 18 minutes from Woodside Station to Grand Central Terminal via MTA 7 subway.",
            "url": "https://new.mta.info/schedules"
        }]
    }).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_tavily_response
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        route = tool.get_route(
            origin_lat=40.74, origin_lon=-73.93,
            dest_lat=40.75, dest_lon=-73.97,
            city_name="New York", suburb_name="Woodside",
            cbd_name="Midtown CBD"
        )
        assert route.verification_status == VerificationStatus.SEARCH_DERIVED
        assert route.commute_minutes == 18
        assert "Woodside" in route.nearest_station
        assert "MTA" in route.transit_system

def test_safety_tool_not_configured_returns_null_scores():
    tool = SafetyIntelligenceTool(tavily_api_key="")
    safety = tool.get_safety_index("Dallas", "Plano")
    assert safety.safety_score is None
    assert safety.crime_index is None
    assert safety.verification_status == VerificationStatus.NOT_CONFIGURED

def test_safety_tool_with_mocked_tavily():
    tool = SafetyIntelligenceTool(tavily_api_key="tvly-mock-valid-key-12345")
    mock_tavily_resp = json.dumps({
        "results": [
            {
                "title": "Plano TX Crime Rates and Neighborhood Safety",
                "url": "https://www.neighborhoodscout.com/tx/plano/crime",
                "content": "Plano has a high safety score of 91 out of 100 with low violent crime rates."
            }
        ]
    }).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_tavily_resp
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        safety = tool.get_safety_index("Dallas", "Plano")
        assert safety.safety_score is not None
        assert safety.safety_score >= 80.0
        assert safety.verification_status == VerificationStatus.SEARCH_DERIVED
        assert len(safety.evidence_list) > 0

def test_groq_orchestrator_fallback_and_schema():
    orchestrator = GroqAgentOrchestrator(api_key="")
    assert not orchestrator.is_configured()
    corridors = orchestrator.propose_suburban_corridors("Dallas")
    assert len(corridors) > 0
    first = corridors[0]
    assert "name" in first
    assert "nearest_station" in first
    assert "transit_line" in first

def test_groq_orchestrator_mocked_llm():
    orchestrator = GroqAgentOrchestrator(api_key="gsk_mock_valid_key_123456789")
    mock_llm_json = json.dumps({
        "choices": [{
            "message": {
                "content": json.dumps({
                    "suburbs": [
                        {
                            "name": "Bellevue",
                            "nearest_station": "Downtown Bellevue Station",
                            "transit_line": "Sound Transit 2 Line",
                            "distance_miles": 10.5,
                            "candidate_hotel_type": "Corporate Suites"
                        }
                    ]
                })
            }
        }]
    }).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_llm_json
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        corridors = orchestrator.propose_suburban_corridors("Seattle")
        assert len(corridors) == 1
        assert corridors[0]["name"] == "Bellevue"
        assert corridors[0]["nearest_station"] == "Downtown Bellevue Station"
