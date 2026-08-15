from app.schemas.profile import RiskAssessmentAnswers, RiskAssessmentResult


def calculate_risk_assessment(answers: RiskAssessmentAnswers) -> RiskAssessmentResult:
    """Calculate a transparent, version-one suitability score.

    Dependents is reverse-scored: more dependents means lower capacity to absorb
    investment risk. The mapping is deliberately deterministic and can be audited.
    """
    score = (
        answers.investment_horizon
        + answers.market_drop_reaction
        + answers.income_stability
        + (6 - answers.dependents)
        + answers.investment_experience
    )

    if score <= 10:
        return RiskAssessmentResult(
            risk_score=score,
            risk_category="conservative",
            suggested_equity_allocation_range="20-30%",
        )
    if score <= 18:
        return RiskAssessmentResult(
            risk_score=score,
            risk_category="moderate",
            suggested_equity_allocation_range="40-60%",
        )
    return RiskAssessmentResult(
        risk_score=score,
        risk_category="aggressive",
        suggested_equity_allocation_range="70-90%",
    )
