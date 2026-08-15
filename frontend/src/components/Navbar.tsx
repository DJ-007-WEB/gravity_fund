"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { Activity, BarChart3, ShieldCheck, User, LogOut, LayoutDashboard, Cpu } from "lucide-react";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { isAuthenticated, email, logout } = useAuth();
  const [systemStatus, setSystemStatus] = useState<"online" | "offline">("offline");

  useEffect(() => {
    const checkSystem = async () => {
      try {
        const res = await api.getReadiness();
        if (res.status === "ready" || res.status === "ok") {
          setSystemStatus("online");
        } else {
          setSystemStatus("offline");
        }
      } catch {
        setSystemStatus("offline");
      }
    };

    checkSystem();
    const interval = setInterval(checkSystem, 15000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { name: "Overview", href: "/", icon: Activity },
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Risk Profile", href: "/profile", icon: ShieldCheck },
    { name: "Market Data", href: "/market", icon: BarChart3 },
  ];

  return (
    <nav style={{
      position: "sticky",
      top: 0,
      zIndex: 50,
      background: "rgba(8, 11, 17, 0.85)",
      backdropFilter: "blur(20px)",
      WebkitBackdropFilter: "blur(20px)",
      borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
      padding: "16px 0",
    }}>
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        
        {/* Brand Logo */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "12px", textDecoration: "none" }}>
          <div style={{
            width: "38px",
            height: "38px",
            borderRadius: "10px",
            background: "linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 15px rgba(59, 130, 246, 0.4)",
          }}>
            <Cpu size={22} color="#ffffff" />
          </div>
          <div>
            <span style={{ fontSize: "1.25rem", fontWeight: 800, letterSpacing: "-0.02em" }} className="font-heading">
              Gravity<span className="text-gradient-blue">Fund</span>
            </span>
            <span className="badge badge-blue" style={{ marginLeft: "8px", fontSize: "0.65rem", padding: "2px 8px" }}>
              QUANT MVP
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "8px 16px",
                  borderRadius: "8px",
                  fontSize: "0.9rem",
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? "#ffffff" : "var(--text-secondary)",
                  background: isActive ? "rgba(59, 130, 246, 0.15)" : "transparent",
                  border: isActive ? "1px solid rgba(59, 130, 246, 0.3)" : "1px solid transparent",
                  transition: "all 0.2s ease",
                }}
              >
                <Icon size={16} color={isActive ? "#3b82f6" : "var(--text-muted)"} />
                {link.name}
              </Link>
            );
          })}
        </div>

        {/* Right Section: System Indicator & Auth */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          
          {/* Live System Status Dot */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            background: "rgba(15, 23, 42, 0.8)",
            padding: "6px 12px",
            borderRadius: "9999px",
            border: "1px solid var(--border-glass)",
            fontSize: "0.75rem",
            color: "var(--text-secondary)",
          }}>
            <div className={`pulse-dot ${systemStatus}`} />
            <span>API {systemStatus === "online" ? "Ready" : "Offline"}</span>
          </div>

          {/* User Auth Section */}
          {isAuthenticated ? (
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                <User size={16} color="var(--accent-blue)" />
                <span>{email}</span>
              </div>
              <button
                onClick={() => logout()}
                className="btn-ghost"
                style={{ display: "flex", alignItems: "center", gap: "6px", padding: "6px 12px" }}
                title="Logout"
              >
                <LogOut size={16} color="#ef4444" />
                <span style={{ fontSize: "0.85rem", color: "#ef4444" }}>Logout</span>
              </button>
            </div>
          ) : (
            <Link href="/login" className="btn-primary" style={{ padding: "8px 18px", fontSize: "0.875rem" }}>
              Sign In
            </Link>
          )}

        </div>

      </div>
    </nav>
  );
};
