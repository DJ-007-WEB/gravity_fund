"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { api, UserProfile, MarketStatus } from "@/lib/api";
import {
  ShieldCheck,
  TrendingUp,
  DollarSign,
  Calendar,
  BarChart3,
  ArrowRight,
  PieChart,
  Activity,
  CheckCircle,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, email, fullName, profile, refreshProfile, isLoading: authLoading } = useAuth();
  
  const [marketStatuses, setMarketStatuses] = useState<MarketStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }

    const loadData = async () => {
      try {
        await refreshProfile();
        const statuses = await api.getMarketStatus();
        setMarketStatuses(statuses);
      } catch {
        // Handle silently
      } finally {
        setLoading(false);
      }
    };

    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated, authLoading, router, refreshProfile]);

  if (authLoading || loading) {
    return (
      <div style={{ padding: "100px 0", textAlign: "center", color: "var(--text-secondary)" }}>
        <Activity size={32} className="pulse-dot online" style={{ margin: "0 auto 16px auto" }} />
        <p>Loading your financial dashboard...</p>
      </div>
    );
  }

  const annualIncome = profile?.annual_income || 0;
  const monthlyExpenses = profile?.monthly_expenses || 0;
  const annualExpenses = monthlyExpenses * 12;
  const annualSavings = Math.max(0, annualIncome - annualExpenses);
  const savingsRate = annualIncome > 0 ? Math.round((annualSavings / annualIncome) * 100) : 0;

  const totalPricesIngested = marketStatuses.reduce(
    (acc, item) => acc + (item.total_records || 0),
    0
  );

  return (
    <div style={{ padding: "40px 0 60px 0" }}>
      <div className="container">
        
        {/* Top Greeting Header */}
        <div style={{ marginBottom: "32px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <h1 style={{ fontSize: "2rem", fontWeight: 800 }} className="font-heading">
              Financial <span className="text-gradient-blue">Dashboard</span>
            </h1>
            <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", marginTop: "4px" }}>
              Welcome back, <strong>{fullName ? fullName.split(" ")[0] : email}</strong>
            </p>
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <Link href="/profile" className="btn-secondary">
              <ShieldCheck size={16} color="var(--accent-blue)" />
              <span>Update Risk Profile</span>
            </Link>
            <Link href="/market" className="btn-primary">
              <BarChart3 size={16} />
              <span>View Market Charts</span>
            </Link>
          </div>
        </div>

        {/* Profile Warning / Callout if Profile Missing */}
        {!profile ? (
          <div
            className="glass-panel glass-panel-glow"
            style={{
              padding: "32px",
              marginBottom: "32px",
              textAlign: "center",
            }}
          >
            <ShieldCheck size={40} color="var(--accent-blue)" style={{ margin: "0 auto 16px auto" }} />
            <h3 style={{ fontSize: "1.4rem", fontWeight: 700, marginBottom: "8px" }}>
              Complete Your Risk Profile Questionnaire
            </h3>
            <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", maxWidth: "550px", margin: "0 auto 24px auto" }}>
              You haven&apos;t completed your financial profile yet. Answer 5 quick questions to discover your risk category and suggested asset allocation range.
            </p>
            <Link href="/profile" className="btn-primary" style={{ padding: "12px 24px" }}>
              <span>Start Risk Assessment</span>
              <ArrowRight size={18} />
            </Link>
          </div>
        ) : (
          /* Main Dashboard Grid */
          <>
            {/* Risk Suitability Card */}
            <div className="grid-3" style={{ marginBottom: "32px" }}>
              
              <div className="glass-panel" style={{ padding: "28px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Risk Category
                  </span>
                  <span
                    className={`badge ${
                      profile.risk_category === "aggressive"
                        ? "badge-amber"
                        : profile.risk_category === "moderate"
                        ? "badge-blue"
                        : "badge-green"
                    }`}
                  >
                    {profile.risk_category}
                  </span>
                </div>

                <div style={{ fontSize: "2rem", fontWeight: 800, textTransform: "capitalize", marginBottom: "8px" }} className="font-heading">
                  {profile.risk_category} Risk
                </div>

                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  Suitability Score: <strong>{profile.risk_score} / 25</strong>
                </p>

                <div style={{ marginTop: "20px", paddingTop: "16px", borderTop: "1px solid var(--border-glass)" }}>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Suggested Equity Band</div>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--accent-cyan)", marginTop: "4px" }}>
                    {profile.risk_category === "aggressive"
                      ? "70 - 90% Equity"
                      : profile.risk_category === "moderate"
                      ? "40 - 60% Equity"
                      : "20 - 30% Equity"}
                  </div>
                </div>
              </div>

              {/* Savings & Cashflow */}
              <div className="glass-panel" style={{ padding: "28px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Annual Cashflow
                  </span>
                  <DollarSign size={20} color="var(--accent-green)" />
                </div>

                <div style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "8px" }} className="font-heading">
                  ₹{(annualIncome / 100000).toFixed(1)} Lakhs
                </div>

                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  Annual Income • Monthly Expenses: ₹{(monthlyExpenses).toLocaleString("en-IN")}
                </p>

                <div style={{ marginTop: "20px", paddingTop: "16px", borderTop: "1px solid var(--border-glass)", display: "flex", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Savings Rate</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--accent-green)", marginTop: "4px" }}>
                      {savingsRate}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Est. Annual Surplus</div>
                    <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-primary)", marginTop: "4px" }}>
                      ₹{(annualSavings / 100000).toFixed(1)}L
                    </div>
                  </div>
                </div>
              </div>

              {/* Horizon & Strategy */}
              <div className="glass-panel" style={{ padding: "28px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600 }}>
                    Investment Horizon
                  </span>
                  <Calendar size={20} color="var(--accent-purple)" />
                </div>

                <div style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "8px" }} className="font-heading">
                  {profile.investment_horizon_years} Years
                </div>

                <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  Age: {profile.age} • Planned Accumulation Window
                </p>

                <div style={{ marginTop: "20px", paddingTop: "16px", borderTop: "1px solid var(--border-glass)" }}>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Optimization Status</div>
                  <div style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--accent-blue)", marginTop: "4px", display: "flex", alignItems: "center", gap: "6px" }}>
                    <CheckCircle size={14} color="#3b82f6" /> Model Ready for Asset Allocation
                  </div>
                </div>
              </div>

            </div>
          </>
        )}

        {/* Market Data Cache Summary */}
        <div className="glass-panel" style={{ padding: "32px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
            <div>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700 }} className="font-heading">
                Market Data Ingestion Pipeline Status
              </h3>
              <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", marginTop: "2px" }}>
                Live daily price series cached in PostgreSQL (`historical_prices`)
              </p>
            </div>
            <span className="badge badge-blue">{marketStatuses.length} Monitored Assets</span>
          </div>

          <div className="grid-4" style={{ marginBottom: "24px" }}>
            {marketStatuses.slice(0, 4).map((item) => (
              <div
                key={item.ticker}
                style={{
                  background: "rgba(30, 41, 59, 0.5)",
                  border: "1px solid var(--border-glass)",
                  borderRadius: "var(--radius-md)",
                  padding: "16px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontWeight: 700, color: "var(--accent-cyan)", fontSize: "0.95rem" }}>
                    {item.ticker}
                  </span>
                  <span className="badge badge-green" style={{ fontSize: "0.65rem" }}>
                    {item.asset_class}
                  </span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "8px" }}>
                  {item.name}
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  {item.total_records} daily prices • Latest: {item.latest_date || "N/A"}
                </div>
              </div>
            ))}
          </div>

          <div style={{ textAlign: "right" }}>
            <Link href="/market" className="btn-ghost" style={{ fontSize: "0.9rem", color: "var(--accent-blue)" }}>
              View All Market Analytics →
            </Link>
          </div>

        </div>

      </div>
    </div>
  );
}
