import pytest
from pydantic import ValidationError

from app.schemas.profile import ProfileUpsert, RiskAssessmentAnswers
from app.services.risk_scoring import calculate_risk_assessment


def test_conservative_profile_is_scored_correctly():
    result = calculate_risk_assessment(
        RiskAssessmentAnswers(
            investment_horizon=1,
            market_drop_reaction=1,
            income_stability=1,
            dependents=5,
            investment_experience=1,
        )
    )
    assert result.risk_score == 5
    assert result.risk_category == "conservative"


def test_aggressive_profile_is_scored_correctly():
    result = calculate_risk_assessment(
        RiskAssessmentAnswers(
            investment_horizon=5,
            market_drop_reaction=5,
            income_stability=5,
            dependents=1,
            investment_experience=5,
        )
    )
    assert result.risk_score == 25
    assert result.risk_category == "aggressive"


def test_profile_rejects_unsustainable_expenses():
    with pytest.raises(ValidationError, match="Monthly expenses cannot exceed annual income"):
        ProfileUpsert(
            age=30,
            annual_income=600_000,
            monthly_expenses=60_000,
            investment_horizon_years=10,
            risk_tolerance_answers=RiskAssessmentAnswers(
                investment_horizon=3,
                market_drop_reaction=3,
                income_stability=3,
                dependents=3,
                investment_experience=3,
            ),
        )
