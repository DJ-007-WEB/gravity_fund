"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { Lock, Mail, ArrowRight, ShieldCheck, AlertCircle, KeyRound, CheckCircle, RefreshCw } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();

  const [mode, setMode] = useState<"login" | "signup">("login");
  const [signupStep, setSignupStep] = useState<"credentials" | "otp">("credentials");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [otpCode, setOtpCode] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [successInfo, setSuccessInfo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Handle Login Submit
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await api.login(email, password);
      login(res.access_token, email, fullName);
      router.push("/dashboard");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Invalid email or password.");
      }
    } finally {
      setLoading(false);
    }
  };

  // Step 1: Request OTP
  const handleRequestOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessInfo(null);
    setLoading(true);

    try {
      const res = await api.requestOTP(email, password, fullName);
      setSuccessInfo(res.message || "Verification code sent to your email!");
      setSignupStep("otp");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to send verification code.");
      }
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify OTP & Complete Signup
  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessInfo(null);
    setLoading(true);

    try {
      const res = await api.verifyOTPAndSignup(email, password, otpCode, fullName);
      login(res.access_token, email, fullName);
      router.push("/profile");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Invalid or expired verification code.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "60px 0", minHeight: "calc(100vh - 200px)", display: "flex", alignItems: "center" }}>
      <div className="container" style={{ maxWidth: "460px" }}>

        <div className="glass-panel" style={{ padding: "40px" }}>

          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: "32px" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                background: "rgba(59, 130, 246, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 16px auto",
                border: "1px solid rgba(59, 130, 246, 0.3)",
              }}
            >
              <ShieldCheck size={24} color="#3b82f6" />
            </div>

            <h2 style={{ fontSize: "1.8rem", fontWeight: 700 }} className="font-heading">
              {mode === "login"
                ? "Welcome Back"
                : signupStep === "credentials"
                  ? "Create Account"
                  : "Verify Your Email"}
            </h2>
            <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginTop: "6px" }}>
              {mode === "login"
                ? "Sign in to access your wealth optimization dashboard"
                : signupStep === "credentials"
                  ? "Step 1 of 2: Enter your email and password"
                  : "Step 2 of 2: Enter the 6-digit code sent to your inbox"}
            </p>
          </div>

          {/* Mode Switcher Tabs */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              background: "rgba(15, 23, 42, 0.9)",
              borderRadius: "var(--radius-md)",
              padding: "4px",
              marginBottom: "28px",
              border: "1px solid var(--border-glass)",
            }}
          >
            <button
              onClick={() => {
                setMode("login");
                setSignupStep("credentials");
                setError(null);
                setSuccessInfo(null);
              }}
              style={{
                padding: "8px",
                borderRadius: "var(--radius-sm)",
                border: "none",
                fontSize: "0.875rem",
                fontWeight: mode === "login" ? 600 : 500,
                color: mode === "login" ? "#ffffff" : "var(--text-secondary)",
                background: mode === "login" ? "rgba(59, 130, 246, 0.25)" : "transparent",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              Sign In
            </button>
            <button
              onClick={() => {
                setMode("signup");
                setSignupStep("credentials");
                setError(null);
                setSuccessInfo(null);
              }}
              style={{
                padding: "8px",
                borderRadius: "var(--radius-sm)",
                border: "none",
                fontSize: "0.875rem",
                fontWeight: mode === "signup" ? 600 : 500,
                color: mode === "signup" ? "#ffffff" : "var(--text-secondary)",
                background: mode === "signup" ? "rgba(59, 130, 246, 0.25)" : "transparent",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              Register
            </button>
          </div>

          {/* Success Info Banner */}
          {successInfo && (
            <div
              style={{
                background: "rgba(16, 185, 129, 0.15)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                padding: "12px 16px",
                borderRadius: "var(--radius-md)",
                color: "#34d399",
                fontSize: "0.875rem",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "20px",
              }}
            >
              <CheckCircle size={18} style={{ flexShrink: 0 }} />
              <span>{successInfo}</span>
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div
              style={{
                background: "rgba(239, 68, 68, 0.15)",
                border: "1px solid rgba(239, 68, 68, 0.3)",
                padding: "12px 16px",
                borderRadius: "var(--radius-md)",
                color: "#f87171",
                fontSize: "0.875rem",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "20px",
              }}
            >
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {/* FORM 1: LOGIN */}
          {mode === "login" && (
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="email"
                    required
                    className="form-input"
                    style={{ width: "100%", paddingLeft: "42px" }}
                    placeholder="investor@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                  <Mail size={18} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "14px" }} />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: "28px" }}>
                <label className="form-label">Password</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="password"
                    required
                    className="form-input"
                    style={{ width: "100%", paddingLeft: "42px" }}
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <Lock size={18} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "14px" }} />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn-primary" style={{ width: "100%", justifyContent: "center", padding: "14px" }}>
                <span>{loading ? "Authenticating..." : "Sign In"}</span>
                <ArrowRight size={18} />
              </button>
            </form>
          )}

          {/* FORM 2: SIGNUP STEP 1 (Credentials -> Request OTP) */}
          {mode === "signup" && signupStep === "credentials" && (
            <form onSubmit={handleRequestOTP}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="text"
                    required
                    minLength={2}
                    className="form-input"
                    style={{ width: "100%", paddingLeft: "42px" }}
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                  <ShieldCheck size={18} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "14px" }} />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Email Address</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="email"
                    required
                    className="form-input"
                    style={{ width: "100%", paddingLeft: "42px" }}
                    placeholder="investor@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                  <Mail size={18} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "14px" }} />
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: "28px" }}>
                <label className="form-label">Password (Min 6 Characters)</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="password"
                    required
                    minLength={6}
                    className="form-input"
                    style={{ width: "100%", paddingLeft: "42px" }}
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <Lock size={18} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "14px" }} />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn-primary" style={{ width: "100%", justifyContent: "center", padding: "14px" }}>
                <span>{loading ? "Sending Code..." : "Send Verification Code"}</span>
                <ArrowRight size={18} />
              </button>
            </form>
          )}

          {/* FORM 3: SIGNUP STEP 2 (Verify OTP & Complete Registration) */}
          {mode === "signup" && signupStep === "otp" && (
            <form onSubmit={handleVerifyOTP}>
              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "20px" }}>
                Enter the 6-digit code sent to <strong>{email}</strong>
              </div>

              <div className="form-group" style={{ marginBottom: "24px" }}>
                <label className="form-label">6-Digit Verification Code</label>
                <div style={{ position: "relative" }}>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    pattern="\d{6}"
                    className="form-input"
                    style={{
                      width: "100%",
                      paddingLeft: "42px",
                      fontSize: "1.25rem",
                      letterSpacing: "6px",
                      fontWeight: 700,
                      color: "var(--accent-cyan)",
                    }}
                    placeholder="123456"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                  />
                  <KeyRound size={18} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "16px" }} />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn-primary" style={{ width: "100%", justifyContent: "center", padding: "14px", marginBottom: "16px" }}>
                <span>{loading ? "Verifying..." : "Verify & Complete Registration"}</span>
                <CheckCircle size={18} />
              </button>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                <button
                  type="button"
                  onClick={() => setSignupStep("credentials")}
                  className="btn-ghost"
                  style={{ padding: 0, fontSize: "0.8rem" }}
                >
                  ← Edit Email/Password
                </button>
                <button
                  type="button"
                  onClick={handleRequestOTP}
                  disabled={loading}
                  className="btn-ghost"
                  style={{ padding: 0, fontSize: "0.8rem", color: "var(--accent-blue)" }}
                >
                  Resend Code
                </button>
              </div>
            </form>
          )}

        </div>

      </div>
    </div>
  );
}
