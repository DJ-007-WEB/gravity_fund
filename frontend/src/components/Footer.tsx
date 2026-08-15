"use client";

import React from "react";
import Link from "next/link";
import { Shield, ExternalLink, Code } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer style={{
      marginTop: "80px",
      borderTop: "1px solid var(--border-glass)",
      background: "rgba(8, 11, 17, 0.95)",
      padding: "40px 0 24px 0",
    }}>
      <div className="container">
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: "40px", marginBottom: "40px" }}>
          
          {/* Platform Info */}
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "12px" }} className="font-heading">
              Gravity<span className="text-gradient-blue">Fund</span>
            </h3>
            <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.6, maxWidth: "450px" }}>
              Quantitative Retail Wealth Optimization Platform. Backed by deterministic suitability rules, modern portfolio theory, and automated market data pipelines.
            </p>
          </div>

          {/* Core Routes */}
          <div>
            <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "16px", letterSpacing: "0.05em" }}>
              Navigation
            </h4>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.9rem", color: "var(--text-secondary)" }}>
              <li><Link href="/">Platform Overview</Link></li>
              <li><Link href="/dashboard">User Dashboard</Link></li>
              <li><Link href="/profile">Risk Questionnaire</Link></li>
              <li><Link href="/market">Market Analytics</Link></li>
            </ul>
          </div>

          {/* System Links */}
          <div>
            <h4 style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "16px", letterSpacing: "0.05em" }}>
              Developer API
            </h4>
            <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "10px", fontSize: "0.9rem", color: "var(--text-secondary)" }}>
              <li>
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
                  <span>Swagger API Docs</span>
                  <ExternalLink size={12} color="var(--text-muted)" />
                </a>
              </li>
              <li>
                <a href="http://localhost:8000/api/v1/ready" target="_blank" rel="noreferrer" style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
                  <span>Backend Health Probe</span>
                  <ExternalLink size={12} color="var(--text-muted)" />
                </a>
              </li>
            </ul>
          </div>

        </div>

        {/* Regulatory Disclaimer Banner */}
        <div style={{
          background: "rgba(15, 23, 42, 0.6)",
          border: "1px solid var(--border-glass)",
          borderRadius: "var(--radius-md)",
          padding: "16px 20px",
          display: "flex",
          alignItems: "center",
          gap: "14px",
          marginBottom: "24px",
        }}>
          <Shield size={24} color="var(--accent-amber)" style={{ flexShrink: 0 }} />
          <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
            <strong>Regulatory Boundary Notice:</strong> Gravity Fund operates strictly as an educational analytics and portfolio-planning platform. It does not provide personalized security-level buy/sell instructions, promise investment returns, or execute automated trades.
          </p>
        </div>

        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderTop: "1px solid rgba(255, 255, 255, 0.05)",
          paddingTop: "20px",
          fontSize: "0.8rem",
          color: "var(--text-muted)",
        }}>
          <span>© 2026 Gravity Fund. All rights reserved.</span>
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Code size={14} /> FastAPI + Next.js Stack
          </span>
        </div>

      </div>
    </footer>
  );
};
