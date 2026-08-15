from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


RiskCategory = Literal["conservative", "moderate", "aggressive"]


class RiskAssessmentAnswers(BaseModel):
    """Normalised answers where 1 is least risk-taking and 5 is most risk-taking."""

    investment_horizon: int = Field(ge=1, le=5)
    market_drop_reaction: int = Field(ge=1, le=5)
    income_stability: int = Field(ge=1, le=5)
    dependents: int = Field(ge=1, le=5)
    investment_experience: int = Field(ge=1, le=5)


class ProfileUpsert(BaseModel):
    age: int = Field(ge=18, le=100)
    annual_income: float = Field(gt=0, le=1_000_000_000)
    monthly_expenses: float = Field(ge=0, le=100_000_000)
    investment_horizon_years: int = Field(ge=1, le=60)
    risk_tolerance_answers: RiskAssessmentAnswers

    @model_validator(mode="after")
    def expenses_must_fit_income(self):
        if self.monthly_expenses * 12 > self.annual_income:
            raise ValueError("Monthly expenses cannot exceed annual income.")
        return self


class RiskAssessmentResult(BaseModel):
    risk_score: int = Field(ge=5, le=25)
    risk_category: RiskCategory
    suggested_equity_allocation_range: str


class UserProfileResponse(ProfileUpsert, RiskAssessmentResult):
    model_config = ConfigDict(from_attributes=True)
