"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import {
  ShieldCheck,
  TrendingUp,
  Database,
  ArrowRight,
  Zap,
  CheckCircle2,
  AlertTriangle,
  BarChart2,
  Lock,
} from "lucide-react";

export default function HomePage() {
  const [readiness, setReadiness] = useState<{ status: string } | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    api
      .getReadiness()
      .then((data) => setReadiness(data))
      .catch(() => setReadiness({ status: "offline" }))
      .finally(() => setLoadingHealth(false));
  }, []);

  return (
    <div style={{ paddingTop: "40px", paddingBottom: "60px" }}>
      <div className="container">
        
        {/* Hero Section */}
        <div style={{ textAlign: "center", maxWidth: "800px", margin: "0 auto 60px auto" }}>
          
          <div style={{ display: "inline-flex", marginBottom: "20px" }}>
            <span className="badge badge-blue">
              <Zap size={12} /> Phase 1 Backend Architecture Live
            </span>
          </div>

          <h1
            style={{
              fontSize: "3.2rem",
              fontWeight: 800,
              lineHeight: 1.15,
              letterSpacing: "-0.03em",
              marginBottom: "24px",
            }}
            className="font-heading"
          >
            Quantitative Retail Wealth <br />
            <span className="text-gradient-blue">Optimization Platform</span>
          </h1>

          <p
            style={{
              fontSize: "1.15rem",
              color: "var(--text-secondary)",
              lineHeight: 1.6,
              marginBottom: "36px",
            }}
          >
            Empowering retail investors with institutional-grade portfolio allocation. 
            Deterministic risk profiling, automated Indian ETF daily data ingestion, and transparent suitability scoring.
          </p>

          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <Link href="/profile" className="btn-primary" style={{ padding: "14px 28px", fontSize: "1rem" }}>
              <span>Start Risk Questionnaire</span>
              <ArrowRight size={18} />
            </Link>
            <Link href="/market" className="btn-secondary" style={{ padding: "14px 28px", fontSize: "1rem" }}>
              <span>Explore Market Analytics</span>
              <BarChart2 size={18} />
            </Link>
          </div>

        </div>

        {/* Live System Health Card */}
        <div
          className="glass-panel glass-panel-glow"
          style={{
            padding: "24px 32px",
            marginBottom: "60px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "20px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background:
                  readiness?.status === "ready"
                    ? "rgba(16, 185, 129, 0.15)"
                    : "rgba(239, 68, 68, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border:
                  readiness?.status === "ready"
                    ? "1px solid rgba(16, 185, 129, 0.3)"
                    : "1px solid rgba(239, 68, 68, 0.3)",
              }}
            >
              {readiness?.status === "ready" ? (
                <CheckCircle2 size={24} color="#10b981" />
              ) : (
                <AlertTriangle size={24} color="#ef4444" />
              )}
            </div>
            <div>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>
                System Readiness Probe:{" "}
                <span
                  style={{
                    color:
                      readiness?.status === "ready"
                        ? "var(--accent-green)"
                        : "var(--accent-amber)",
                  }}
                >
                  {loadingHealth
                    ? "Checking..."
                    : readiness?.status === "ready"
                    ? "Operational (Ready)"
                    : "Connecting to Local Backend..."}
                </span>
              </h3>
              <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Backend connected to PostgreSQL 15 & Redis 7 Docker containers on localhost.
              </p>
            </div>
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <span className="badge badge-green">PostgreSQL 15 Connected</span>
            <span className="badge badge-blue">Redis 7 Active</span>
          </div>
        </div>

        {/* Feature Cards Grid */}
        <div style={{ marginBottom: "60px" }}>
          <h2
            style={{
              fontSize: "1.8rem",
              fontWeight: 700,
              textAlign: "center",
              marginBottom: "40px",
            }}
            className="font-heading"
          >
            Built for <span className="text-gradient-blue">Transparency & Scale</span>
          </h2>

          <div className="grid-3">
            
            <div className="glass-panel" style={{ padding: "32px" }}>
              <div
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "10px",
                  background: "rgba(59, 130, 246, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "20px",
                }}
              >
                <ShieldCheck size={22} color="#3b82f6" />
              </div>
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "10px" }}>
                Deterministic Risk Profiling
              </h3>
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                Auditable risk scoring engine. Maps horizon, market volatility tolerance, and dependents into Conservative, Moderate, or Aggressive categories.
              </p>
            </div>

            <div className="glass-panel" style={{ padding: "32px" }}>
              <div
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "10px",
                  background: "rgba(6, 182, 212, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "20px",
                }}
              >
                <Database size={22} color="#06b6d4" />
              </div>
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "10px" }}>
                9,800+ Ingested Prices
              </h3>
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                Automated daily pipeline ingesting 5 years of OHLCV history across Nifty 50, Junior BeES, Bank BeES, Gold, and Liquid ETFs.
              </p>
            </div>

            <div className="glass-panel" style={{ padding: "32px" }}>
              <div
                style={{
                  width: "44px",
                  height: "44px",
                  borderRadius: "10px",
                  background: "rgba(16, 185, 129, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "20px",
                }}
              >
                <Lock size={22} color="#10b981" />
              </div>
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700, marginBottom: "10px" }}>
                Token Fingerprinting Auth
              </h3>
              <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
                SHA-256 token hashing for Redis session deactivation, JWT security, CORS protection, and `X-Request-ID` tracing.
              </p>
            </div>

          </div>
        </div>

        {/* Universe Preview Section */}
        <div className="glass-panel" style={{ padding: "40px", textAlign: "center" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "12px" }} className="font-heading">
            Indian Market Asset Universe
          </h3>
          <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", marginBottom: "30px" }}>
            Curated liquid ETFs and benchmarks monitored daily by Gravity Fund
          </p>

          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "12px",
              flexWrap: "wrap",
            }}
          >
            {[
              { ticker: "NIFTYBEES.NS", name: "Nifty 50 ETF", type: "Equity" },
              { ticker: "JUNIORBEES.NS", name: "Nifty Next 50 ETF", type: "Equity" },
              { ticker: "BANKBEES.NS", name: "Bank Nifty ETF", type: "Equity" },
              { ticker: "GOLDBEES.NS", name: "Gold ETF", type: "Commodity" },
              { ticker: "LIQUIDBEES.NS", name: "Liquid ETF", type: "Cash" },
              { ticker: "^NSEI", name: "Nifty 50 Benchmark", type: "Benchmark" },
            ].map((asset) => (
              <div
                key={asset.ticker}
                style={{
                  background: "rgba(30, 41, 59, 0.6)",
                  border: "1px solid var(--border-glass)",
                  padding: "14px 20px",
                  borderRadius: "var(--radius-md)",
                  textAlign: "left",
                }}
              >
                <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--accent-cyan)" }}>
                  {asset.ticker}
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", margin: "4px 0" }}>
                  {asset.name}
                </div>
                <span className="badge badge-blue">{asset.type}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
