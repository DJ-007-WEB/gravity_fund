"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { api, UserProfile } from "@/lib/api";
import {
  ShieldCheck,
  Save,
  CheckCircle,
  AlertCircle,
  Activity,
  ArrowRight,
} from "lucide-react";

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated, profile, refreshProfile, isLoading: authLoading } = useAuth();

  // Financial Demographics
  const [age, setAge] = useState<number>(28);
  const [annualIncome, setAnnualIncome] = useState<number>(1500000);
  const [monthlyExpenses, setMonthlyExpenses] = useState<number>(45000);
  const [horizonYears, setHorizonYears] = useState<number>(7);

  // Questionnaire Answers
  const [horizonScore, setHorizonScore] = useState<number>(5);
  const [marketDropScore, setMarketDropScore] = useState<number>(3);
  const [incomeStabilityScore, setIncomeStabilityScore] = useState<number>(4);
  const [dependents, setDependents] = useState<number>(1);
  const [experienceScore, setExperienceScore] = useState<number>(3);

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }

    if (profile) {
      setAge(profile.age || 28);
      setAnnualIncome(profile.annual_income || 1500000);
      setMonthlyExpenses(profile.monthly_expenses || 45000);
      setHorizonYears(profile.investment_horizon_years || 7);

      const q = profile.risk_tolerance_answers;
      if (q) {
        setHorizonScore(q.investment_horizon || 5);
        setMarketDropScore(q.market_drop_reaction || 3);
        setIncomeStabilityScore(q.income_stability || 4);
        setDependents(q.dependents || 1);
        setExperienceScore(q.investment_experience || 3);
      }
    }
  }, [profile, isAuthenticated, authLoading, router]);

  // Real-time client-side calculation matching backend risk_scoring.py
  const calculateLocalScore = () => {
    return horizonScore + marketDropScore + incomeStabilityScore + (6 - dependents) + experienceScore;
  };

  const currentScore = calculateLocalScore();
  const currentCategory =
    currentScore <= 10
      ? "conservative"
      : currentScore <= 18
      ? "moderate"
      : "aggressive";

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);

    try {
      await api.updateProfile({
        age: Number(age),
        annual_income: Number(annualIncome),
        monthly_expenses: Number(monthlyExpenses),
        investment_horizon_years: Number(horizonYears),
        risk_tolerance_answers: {
          investment_horizon: Number(horizonScore),
          market_drop_reaction: Number(marketDropScore),
          income_stability: Number(incomeStabilityScore),
          dependents: Number(dependents),
          investment_experience: Number(experienceScore),
        },
      });

      await refreshProfile();
      setSuccessMsg("Risk profile updated successfully! Suitability score persisted.");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg("Failed to save profile.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (authLoading) {
    return (
      <div style={{ padding: "100px 0", textAlign: "center", color: "var(--text-secondary)" }}>
        <Activity size={32} className="pulse-dot online" style={{ margin: "0 auto 16px auto" }} />
        <p>Loading your risk questionnaire...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "40px 0 60px 0" }}>
      <div className="container" style={{ maxWidth: "880px" }}>
        
        {/* Title */}
        <div style={{ marginBottom: "32px", textAlign: "center" }}>
          <span className="badge badge-blue" style={{ marginBottom: "12px" }}>
            <ShieldCheck size={12} /> Deterministic Suitability Calculator
          </span>
          <h1 style={{ fontSize: "2.4rem", fontWeight: 800 }} className="font-heading">
            Risk Profile & <span className="text-gradient-blue">Suitability Questionnaire</span>
          </h1>
          <p style={{ fontSize: "1rem", color: "var(--text-secondary)", marginTop: "8px", maxWidth: "600px", margin: "8px auto 0 auto" }}>
            Your answers calculate a transparent suitability score that determines your target equity vs debt allocation range.
          </p>
        </div>

        {/* Live Score Preview Header */}
        <div
          className="glass-panel glass-panel-glow"
          style={{
            padding: "24px 32px",
            marginBottom: "36px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "20px",
          }}
        >
          <div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
              Calculated Category
            </div>
            <div style={{ fontSize: "1.8rem", fontWeight: 800, textTransform: "capitalize", color: "#ffffff" }} className="font-heading">
              {currentCategory} Risk Profile
            </div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "4px" }}>
              Total Score: <strong>{currentScore} / 25</strong>
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>Suggested Equity Allocation</div>
            <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--accent-cyan)", marginTop: "4px" }}>
              {currentCategory === "aggressive"
                ? "70% – 90% Equity"
                : currentCategory === "moderate"
                ? "40% – 60% Equity"
                : "20% – 30% Equity"}
            </div>
          </div>
        </div>

        {/* Success/Error Alerts */}
        {successMsg && (
          <div
            style={{
              background: "rgba(16, 185, 129, 0.15)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              padding: "14px 20px",
              borderRadius: "var(--radius-md)",
              color: "#34d399",
              fontSize: "0.9rem",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "28px",
            }}
          >
            <CheckCircle size={20} style={{ flexShrink: 0 }} />
            <span>{successMsg}</span>
          </div>
        )}

        {errorMsg && (
          <div
            style={{
              background: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              padding: "14px 20px",
              borderRadius: "var(--radius-md)",
              color: "#f87171",
              fontSize: "0.9rem",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "28px",
            }}
          >
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSave}>
          
          {/* Section 1: Financial Demographics */}
          <div className="glass-panel" style={{ padding: "32px", marginBottom: "32px" }}>
            <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "20px", color: "var(--accent-blue)" }} className="font-heading">
              1. Financial Demographics & Cashflow
            </h3>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Current Age (Years)</label>
                <input
                  type="number"
                  min={18}
                  max={100}
                  className="form-input"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Annual Income (₹)</label>
                <input
                  type="number"
                  step={50000}
                  className="form-input"
                  value={annualIncome}
                  onChange={(e) => setAnnualIncome(Number(e.target.value))}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Monthly Expenses (₹)</label>
                <input
                  type="number"
                  step={5000}
                  className="form-input"
                  value={monthlyExpenses}
                  onChange={(e) => setMonthlyExpenses(Number(e.target.value))}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Investment Horizon (Years)</label>
                <input
                  type="number"
                  min={1}
                  max={40}
                  className="form-input"
                  value={horizonYears}
                  onChange={(e) => setHorizonYears(Number(e.target.value))}
                />
              </div>
            </div>
          </div>

          {/* Section 2: 5-Question Questionnaire */}
          <div className="glass-panel" style={{ padding: "32px", marginBottom: "32px" }}>
            <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "24px", color: "var(--accent-cyan)" }} className="font-heading">
              2. Suitability Assessment Questions
            </h3>

            {/* Q1 */}
            <div className="form-group">
              <label className="form-label">Q1. When will you need to withdraw this capital?</label>
              <select
                className="form-select"
                value={horizonScore}
                onChange={(e) => setHorizonScore(Number(e.target.value))}
              >
                <option value={1}>Short-term (less than 2 years)</option>
                <option value={3}>Medium-term (3 to 5 years)</option>
                <option value={5}>Long-term (more than 5 years)</option>
              </select>
            </div>

            {/* Q2 */}
            <div className="form-group">
              <label className="form-label">Q2. How do you react if your portfolio drops 20% in a market pull-back?</label>
              <select
                className="form-select"
                value={marketDropScore}
                onChange={(e) => setMarketDropScore(Number(e.target.value))}
              >
                <option value={1}>Sell all investments immediately to prevent further loss</option>
                <option value={3}>Hold position and wait for recovery</option>
                <option value={5}>Buy more at lower valuation prices</option>
              </select>
            </div>

            {/* Q3 */}
            <div className="form-group">
              <label className="form-label">Q3. How stable is your primary source of income?</label>
              <select
                className="form-select"
                value={incomeStabilityScore}
                onChange={(e) => setIncomeStabilityScore(Number(e.target.value))}
              >
                <option value={1}>Variable / Commission / High risk</option>
                <option value={3}>Moderate stability / Freelance / Business</option>
                <option value={5}>Highly stable / Tenured salaried employment</option>
              </select>
            </div>

            {/* Q4 */}
            <div className="form-group">
              <label className="form-label">Q4. How many financial dependents rely on you?</label>
              <select
                className="form-select"
                value={dependents}
                onChange={(e) => setDependents(Number(e.target.value))}
              >
                <option value={1}>0 to 1 dependent (Highest risk absorption capacity)</option>
                <option value={2}>2 dependents</option>
                <option value={3}>3 dependents</option>
                <option value={4}>4 or more dependents (Lower capacity for drawdown risk)</option>
              </select>
            </div>

            {/* Q5 */}
            <div className="form-group">
              <label className="form-label">Q5. What is your prior investment experience with equities & market instruments?</label>
              <select
                className="form-select"
                value={experienceScore}
                onChange={(e) => setExperienceScore(Number(e.target.value))}
              >
                <option value={1}>Beginner (Fixed deposits / Savings only)</option>
                <option value={3}>Intermediate (Mutual funds / Some stock experience)</option>
                <option value={5}>Experienced (Active portfolio management / ETFs / Derivatives)</option>
              </select>
            </div>

          </div>

          {/* Submit Action Bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <button
              type="submit"
              disabled={saving}
              className="btn-primary"
              style={{ padding: "14px 32px", fontSize: "1rem" }}
            >
              <Save size={18} />
              <span>{saving ? "Saving Profile..." : "Save & Calculate Suitability"}</span>
            </button>

            <button
              type="button"
              onClick={() => router.push("/dashboard")}
              className="btn-secondary"
            >
              <span>Go to Dashboard</span>
              <ArrowRight size={16} />
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
