"use client";

import React, { useEffect, useState } from "react";
import { api, Asset, HistoricalPrice, MarketStatus } from "@/lib/api";
import {
  BarChart3,
  RefreshCw,
  TrendingUp,
  Activity,
  Calendar,
  Database,
  Search,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function MarketPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [marketStatuses, setMarketStatuses] = useState<MarketStatus[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string>("NIFTYBEES.NS");
  const [prices, setPrices] = useState<HistoricalPrice[]>([]);
  
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [loadingChart, setLoadingChart] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState<string | null>(null);

  const [timeframe, setTimeframe] = useState<"1M" | "6M" | "1Y" | "5Y">("5Y");

  // Load Assets and Status on Mount
  useEffect(() => {
    const initData = async () => {
      try {
        const [assetList, statusList] = await Promise.all([
          api.getAssets(),
          api.getMarketStatus(),
        ]);
        setAssets(assetList);
        setMarketStatuses(statusList);
      } catch {
        // Handle silently
      } finally {
        setLoadingStatus(false);
      }
    };

    initData();
  }, []);

  // Fetch prices whenever selected ticker changes
  useEffect(() => {
    if (!selectedTicker) return;

    const loadPrices = async () => {
      setLoadingChart(true);
      try {
        const data = await api.getPrices(selectedTicker, 1250);
        setPrices(data);
      } catch {
        setPrices([]);
      } finally {
        setLoadingChart(false);
      }
    };

    loadPrices();
  }, [selectedTicker]);

  const handleIngestTrigger = async () => {
    setIngesting(true);
    setIngestMsg(null);
    try {
      const res = await api.triggerIngest("5y");
      setIngestMsg(`Ingestion completed! Inserted ${res.inserted_records} prices across ${res.processed_assets} assets.`);
      const statusList = await api.getMarketStatus();
      setMarketStatuses(statusList);
    } catch {
      setIngestMsg("Ingestion trigger failed.");
    } finally {
      setIngesting(false);
    }
  };

  // Filter prices by selected timeframe
  const getFilteredPrices = () => {
    if (!prices.length) return [];
    if (timeframe === "5Y") return prices;

    const totalDays = timeframe === "1M" ? 30 : timeframe === "6M" ? 180 : 365;
    return prices.slice(-totalDays);
  };

  const filteredPrices = getFilteredPrices();

  // Performance Stats
  const firstPrice = filteredPrices.length ? filteredPrices[0].close : 0;
  const lastPrice = filteredPrices.length ? filteredPrices[filteredPrices.length - 1].close : 0;
  const priceChange = lastPrice - firstPrice;
  const percentageChange = firstPrice > 0 ? ((priceChange / firstPrice) * 100).toFixed(2) : "0.00";

  return (
    <div style={{ padding: "40px 0 60px 0" }}>
      <div className="container">
        
        {/* Header */}
        <div style={{ marginBottom: "32px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          <div>
            <h1 style={{ fontSize: "2.4rem", fontWeight: 800 }} className="font-heading">
              Market Data <span className="text-gradient-blue">Analytics & Charts</span>
            </h1>
            <p style={{ fontSize: "0.95rem", color: "var(--text-secondary)", marginTop: "4px" }}>
              Daily price series ingested from Indian ETF markets & Nifty 50 benchmark
            </p>
          </div>

          <button
            onClick={handleIngestTrigger}
            disabled={ingesting}
            className="btn-secondary"
          >
            <RefreshCw size={16} className={ingesting ? "pulse-dot online" : ""} />
            <span>{ingesting ? "Ingesting Daily Prices..." : "Refresh Market Ingestion"}</span>
          </button>
        </div>

        {ingestMsg && (
          <div
            style={{
              background: "rgba(16, 185, 129, 0.15)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              padding: "12px 16px",
              borderRadius: "var(--radius-md)",
              color: "#34d399",
              fontSize: "0.875rem",
              marginBottom: "24px",
            }}
          >
            {ingestMsg}
          </div>
        )}

        {/* Top Interactive Chart Area */}
        <div className="glass-panel glass-panel-glow" style={{ padding: "32px", marginBottom: "40px" }}>
          
          {/* Chart Controls Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px", marginBottom: "28px" }}>
            
            {/* Ticker Selector */}
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <label style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 600 }}>
                SELECT TICKER:
              </label>
              <select
                className="form-select"
                style={{ width: "220px", fontWeight: 700, color: "var(--accent-cyan)" }}
                value={selectedTicker}
                onChange={(e) => setSelectedTicker(e.target.value)}
              >
                {assets.map((ast) => (
                  <option key={ast.ticker} value={ast.ticker}>
                    {ast.ticker} — {ast.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Timeframe Filter Buttons */}
            <div style={{ display: "flex", gap: "6px", background: "rgba(15, 23, 42, 0.9)", padding: "4px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-glass)" }}>
              {(["1M", "6M", "1Y", "5Y"] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: "var(--radius-sm)",
                    border: "none",
                    fontSize: "0.8rem",
                    fontWeight: timeframe === tf ? 700 : 500,
                    color: timeframe === tf ? "#ffffff" : "var(--text-secondary)",
                    background: timeframe === tf ? "rgba(59, 130, 246, 0.3)" : "transparent",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  {tf}
                </button>
              ))}
            </div>

          </div>

          {/* Performance Summary Pill */}
          <div style={{ display: "flex", gap: "32px", marginBottom: "24px", paddingBottom: "20px", borderBottom: "1px solid var(--border-glass)" }}>
            <div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Latest Price</div>
              <div style={{ fontSize: "1.6rem", fontWeight: 800, marginTop: "2px" }} className="font-heading">
                ₹{lastPrice ? lastPrice.toFixed(2) : "—"}
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{timeframe} Return</div>
              <div
                style={{
                  fontSize: "1.4rem",
                  fontWeight: 700,
                  marginTop: "4px",
                  color: Number(percentageChange) >= 0 ? "var(--accent-green)" : "#ef4444",
                }}
              >
                {Number(percentageChange) >= 0 ? "+" : ""}{percentageChange}%
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Ingested Observations</div>
              <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--accent-blue)", marginTop: "4px" }}>
                {filteredPrices.length} Daily Rows
              </div>
            </div>
          </div>

          {/* Recharts Price Area Chart */}
          <div style={{ width: "100%", height: 380 }}>
            {loadingChart ? (
              <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-secondary)" }}>
                <Activity size={24} className="pulse-dot online" style={{ marginRight: "8px" }} />
                <span>Rendering price chart...</span>
              </div>
            ) : filteredPrices.length === 0 ? (
              <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)" }}>
                No price records found for {selectedTicker}
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={filteredPrices}>
                  <defs>
                    <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis domain={["auto", "auto"]} stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      background: "rgba(15, 23, 42, 0.95)",
                      border: "1px solid rgba(255,255,255,0.15)",
                      borderRadius: "8px",
                      color: "#fff",
                      fontSize: "0.85rem",
                    }}
                    formatter={(value: any) => [
                      `₹${Number(value || 0).toFixed(2)}`,
                      "Close Price",
                    ]}
                  />
                  <Area
                    type="monotone"
                    dataKey="close"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorClose)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

        </div>

        {/* Dataset Ingestion Coverage Table */}
        <div className="glass-panel" style={{ padding: "32px" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "16px" }} className="font-heading">
            Monitored ETF Universe Status
          </h3>

          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Asset Name</th>
                  <th>Class</th>
                  <th>Ingested Rows</th>
                  <th>Earliest Date</th>
                  <th>Latest Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {marketStatuses.map((item) => (
                  <tr key={item.ticker}>
                    <td style={{ fontWeight: 700, color: "var(--accent-cyan)" }}>{item.ticker}</td>
                    <td>{item.name}</td>
                    <td>
                      <span className="badge badge-blue" style={{ fontSize: "0.65rem" }}>
                        {item.asset_class}
                      </span>
                    </td>
                    <td><strong>{item.total_records}</strong> prices</td>
                    <td style={{ color: "var(--text-secondary)" }}>{item.earliest_date || "—"}</td>
                    <td style={{ color: "var(--text-secondary)" }}>{item.latest_date || "—"}</td>
                    <td>
                      <span className={`badge ${item.is_stale ? "badge-amber" : "badge-green"}`}>
                        {item.is_stale ? "Stale" : "Up-To-Date"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>

      </div>
    </div>
  );
}
