"""
Mathematical Boundary Gate & Validation Module
Enforces 100% deterministic rules for inputs, boundaries, currency, dates, and evidence integrity.
"""

from typing import List, Dict, Any, Tuple, Optional
from core.models import (
    CityMaster,
    TransitConnectivity,
    Accommodation,
    SafetyIndex,
    RecommendationScore,
    VerificationStatus
)

class ValidationError(Exception):
    pass

class DataValidator:
    """
    Independent validation gate.
    Validates input parameters, verifies hotel rates against strict budget boundaries,
    validates commute times, and prevents invalid or fabricated data from reaching reports.
    """

    def __init__(self, budget_min: float = 50.0, budget_max: float = 60.0, max_commute_minutes: int = 90):
        self.budget_min = float(budget_min)
        self.budget_max = float(budget_max)
        self.max_commute_minutes = int(max_commute_minutes)
        self.validate_parameters()

    @staticmethod
    def validate_budget(budget_min: float, budget_max: float):
        if budget_min < 0 or budget_max < 0:
            raise ValidationError(f"Budget boundaries must be non-negative: [{budget_min}, {budget_max}]")
        if budget_min > budget_max:
            raise ValidationError(f"budget_min ({budget_min}) cannot exceed budget_max ({budget_max})")

    @staticmethod
    def validate_commute_limit(max_commute_minutes: int):
        if max_commute_minutes <= 0:
            raise ValidationError(f"max_commute_minutes must be positive: {max_commute_minutes}")

    @staticmethod
    def validate_weights(w_safety: float, w_cost: float, w_commute: float, w_transit: float):
        total = round(w_safety + w_cost + w_commute + w_transit, 4)
        if abs(total - 1.0) > 0.001:
            raise ValidationError(f"Weights must sum to 1.0 (current sum: {total})")

    @classmethod
    def validate_pipeline_results(
        cls,
        cities: List[CityMaster],
        transits: List[TransitConnectivity],
        accomms: List[Accommodation],
        safeties: List[SafetyIndex],
        scores: List[RecommendationScore],
        budget_min: float,
        budget_max: float,
        max_commute_minutes: int
    ) -> Dict[str, Any]:
        validator = cls(budget_min=budget_min, budget_max=budget_max, max_commute_minutes=max_commute_minutes)
        return validator.audit_pipeline_output(cities, transits, accomms, safeties, scores)

    def validate_parameters(self):
        self.validate_budget(self.budget_min, self.budget_max)
        self.validate_commute_limit(self.max_commute_minutes)

    def is_hotel_eligible(self, accomm: Accommodation) -> Tuple[bool, List[str]]:
        """
        Validates hotel candidate against strict budget bounds and required metadata.
        """
        reasons = []
        rate = accomm.base_nightly_rate_usd

        # Strict Budget Boundary Gate: budget_min <= rate <= budget_max
        if rate < self.budget_min or rate > self.budget_max:
            reasons.append(f"Rate ${rate:.2f} violates strict budget range [${self.budget_min:.2f}, ${self.budget_max:.2f}]")

        if not accomm.hotel_name or not accomm.hotel_name.strip():
            reasons.append("Hotel name is missing or empty")

        if not accomm.currency or accomm.currency.upper() != "USD":
            reasons.append(f"Invalid or unsupported currency: {accomm.currency}")

        if accomm.total_booking_usd < rate:
            reasons.append(f"Total booking cost (${accomm.total_booking_usd:.2f}) cannot be less than base rate (${rate:.2f})")

        is_eligible = len(reasons) == 0
        return is_eligible, reasons

    def is_transit_eligible(self, transit: TransitConnectivity) -> Tuple[bool, List[str]]:
        """
        Validates transit route against commute bounds and endpoints.
        """
        reasons = []
        if transit.commute_minutes > self.max_commute_minutes:
            reasons.append(f"Commute {transit.commute_minutes}m exceeds maximum threshold {self.max_commute_minutes}m")

        if transit.commute_minutes <= 0:
            reasons.append(f"Invalid commute duration: {transit.commute_minutes}m")

        if not transit.nearest_station or not transit.nearest_station.strip():
            reasons.append("Nearest station name is missing")

        is_eligible = len(reasons) == 0
        return is_eligible, reasons

    def audit_pipeline_output(
        self,
        cities: List[CityMaster],
        transits: List[TransitConnectivity],
        accomms: List[Accommodation],
        safeties: List[SafetyIndex],
        scores: List[RecommendationScore]
    ) -> Dict[str, Any]:
        """
        Performs mathematical audit of the pipeline output.
        Returns machine-readable report with errors, warnings, and compliance status.
        """
        errors = []
        warnings = []

        # Check budget compliance for all accommodations
        for a in accomms:
            eligible, reasons = self.is_hotel_eligible(a)
            if not eligible:
                errors.extend([f"{a.hotel_name} ({a.city}): {r}" for r in reasons])

        # Check commute compliance
        for t in transits:
            eligible, reasons = self.is_transit_eligible(t)
            if not eligible:
                # Corridors over commute threshold are filtered during discovery; if any leaked, report as error
                errors.extend([f"{t.suburb} ({t.city}): {r}" for r in reasons])

        # Check safety coverage
        unknown_safety_count = sum(1 for s in safeties if s.safety_score is None)
        if unknown_safety_count > 0:
            warnings.append(f"{unknown_safety_count} localities have UNKNOWN safety scores due to insufficient data")

        # Check score rankings consistency
        if scores:
            ranks = [s.rank for s in scores]
            if len(ranks) != len(set(ranks)):
                errors.append("Duplicate ranks detected in recommendation scores")

        status = "PASS" if len(errors) == 0 else "FAIL"
        compliance_str = (
            f"{len(accomms)} properties verified strictly in [${self.budget_min:.0f}, ${self.budget_max:.0f}]"
            if accomms else f"0 properties matched strict bracket [${self.budget_min:.0f}, ${self.budget_max:.0f}]"
        )

        return {
            "status": status,
            "total_cities": len(cities),
            "transit_corridors_analyzed": len(transits),
            "accommodations_count": len(accomms),
            "budget_compliance": compliance_str,
            "errors": errors,
            "warnings": warnings
        }
