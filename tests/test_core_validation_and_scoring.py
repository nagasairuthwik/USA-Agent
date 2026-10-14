import pytest
from core.models import Accommodation, TransitConnectivity, SafetyIndex, RecommendationScore
from core.scoring import DeterministicScorer
from core.validator import DataValidator, ValidationError

def test_validator_parameter_bounds():
    with pytest.raises(ValidationError):
        DataValidator(budget_min=100.0, budget_max=50.0)

    with pytest.raises(ValidationError):
        DataValidator(budget_min=-10.0, budget_max=50.0)

    with pytest.raises(ValidationError):
        DataValidator(max_commute_minutes=0)

def test_strict_budget_boundary_enforcement():
    validator = DataValidator(budget_min=50.0, budget_max=60.0)

    # Exactly min: eligible
    a_min = Accommodation(city="Test", locality="Test", hotel_name="Min Hotel", address="123", base_nightly_rate_usd=50.0, total_booking_usd=57.0)
    eligible, reasons = validator.is_hotel_eligible(a_min)
    assert eligible is True
    assert reasons == []

    # Exactly max: eligible
    a_max = Accommodation(city="Test", locality="Test", hotel_name="Max Hotel", address="123", base_nightly_rate_usd=60.0, total_booking_usd=68.0)
    eligible, reasons = validator.is_hotel_eligible(a_max)
    assert eligible is True
    assert reasons == []

    # Under min: rejected
    a_under = Accommodation(city="Test", locality="Test", hotel_name="Cheap Hotel", address="123", base_nightly_rate_usd=49.99, total_booking_usd=55.0)
    eligible, reasons = validator.is_hotel_eligible(a_under)
    assert eligible is False
    assert any("violates strict budget" in r for r in reasons)

    # Over max: rejected
    a_over = Accommodation(city="Test", locality="Test", hotel_name="Pricey Hotel", address="123", base_nightly_rate_usd=60.01, total_booking_usd=70.0)
    eligible, reasons = validator.is_hotel_eligible(a_over)
    assert eligible is False
    assert any("violates strict budget" in r for r in reasons)

def test_commute_boundary_enforcement():
    validator = DataValidator(max_commute_minutes=90)

    t_valid = TransitConnectivity(city="C", downtown="D", suburb="S", transit_system="T", transit_mode="M", nearest_station="St", commute_minutes=90, transfers=0, fare_usd=2.5)
    eligible, reasons = validator.is_transit_eligible(t_valid)
    assert eligible is True

    t_invalid = TransitConnectivity(city="C", downtown="D", suburb="S", transit_system="T", transit_mode="M", nearest_station="St", commute_minutes=91, transfers=0, fare_usd=2.5)
    eligible, reasons = validator.is_transit_eligible(t_invalid)
    assert eligible is False
    assert any("exceeds maximum threshold" in r for r in reasons)

def test_deterministic_scoring_weights_validation():
    with pytest.raises(ValueError):
        DeterministicScorer(weight_safety=0.5, weight_cost=0.5, weight_commute=0.2, weight_transit=0.1)

def test_deterministic_scoring_calculation():
    scorer = DeterministicScorer(
        weight_safety=0.35,
        weight_cost=0.30,
        weight_commute=0.20,
        weight_transit=0.15,
        budget_min=50.0,
        budget_max=60.0,
        max_commute_minutes=90
    )
    a = Accommodation(city="Dallas", locality="Garland", hotel_name="Motel 6", address="123", base_nightly_rate_usd=55.0, total_booking_usd=63.0, rating=4.0)
    t = TransitConnectivity(city="Dallas", downtown="CBD", suburb="Garland", transit_system="DART", transit_mode="Rail", nearest_station="Station", commute_minutes=30, transfers=0, fare_usd=3.0)
    s = SafetyIndex(city="Dallas", locality="Garland", safety_score=90.0, crime_index=10.0, walkability=85, category="High Safety")

    score = scorer.score_candidate(a, t, s)
    assert score.cost_score > 0
    assert score.commute_score > 0
    assert score.transit_score > 0
    assert score.safety_score == 90.0
    assert score.overall_score > 0
    assert score.is_rankable is True
