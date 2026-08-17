const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  age: number;
  annual_income: number;
  monthly_expenses: number;
  investment_horizon_years: number;
  risk_tolerance_answers: {
    investment_horizon: number;
    market_drop_reaction: number;
    income_stability: number;
    dependents: number;
    investment_experience: number;
  };
  risk_score: number;
  risk_category: "conservative" | "moderate" | "aggressive";
  suggested_equity_allocation_range: string;
}

export interface Asset {
  id: number;
  ticker: string;
  name: string;
  asset_class: string;
}

export interface HistoricalPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  adj_close: number;
  volume: number;
}

export interface MarketStatus {
  ticker: string;
  name: string;
  asset_class: string;
  total_records: number;
  earliest_date: string | null;
  latest_date: string | null;
  is_stale: boolean;
}

export interface IngestionResponse {
  status: string;
  processed_assets: number;
  inserted_records: number;
  failed_assets: string[];
}

interface ApiErrorResponse {
  detail?: string;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const error = (await response.json()) as ApiErrorResponse;
      if (error.detail) message = error.detail;
    } catch {
      // Keep the generic HTTP error when the response is not JSON.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

function authHeaders(): HeadersInit {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("gravity_auth_token")
      : null;

  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  async getReadiness(): Promise<{ status: string }> {
    return request<{ status: string }>("/ready");
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);

    return request<TokenResponse>("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body.toString(),
    });
  },

  async requestOTP(
    email: string,
    password: string,
    fullName: string
  ): Promise<{ message: string }> {
    return request<{ message: string }>("/auth/request-otp", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    });
  },

  async verifyOTPAndSignup(
    email: string,
    password: string,
    otpCode: string,
    fullName: string
  ): Promise<TokenResponse> {
    return request<TokenResponse>("/auth/verify-otp-and-signup", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
        otp_code: otpCode,
        full_name: fullName,
      }),
    });
  },

  async logout(): Promise<{ message: string }> {
    return request<{ message: string }>("/auth/logout", {
      method: "POST",
      headers: authHeaders(),
    });
  },

  async getMe(): Promise<{
    id: number;
    email: string;
    full_name: string | null;
    is_active: boolean;
    created_at: string;
  }> {
    return request("/auth/me", {
      headers: authHeaders(),
    });
  },

  async getProfile(): Promise<UserProfile> {
    return request<UserProfile>("/profile", {
      headers: authHeaders(),
    });
  },

  async updateProfile(profile: Omit<UserProfile, "risk_score" | "risk_category" | "suggested_equity_allocation_range">): Promise<UserProfile> {
    return request<UserProfile>("/profile", {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(profile),
    });
  },

  async getAssets(): Promise<Asset[]> {
    return request<Asset[]>("/market/assets");
  },

  async getPrices(ticker: string, limit = 1000): Promise<HistoricalPrice[]> {
    return request<HistoricalPrice[]>(
      `/market/prices/${encodeURIComponent(ticker)}?limit=${limit}`
    );
  },

  async getMarketStatus(): Promise<MarketStatus[]> {
    return request<MarketStatus[]>("/market/status");
  },

  async triggerIngest(period = "5y"): Promise<IngestionResponse> {
    return request<IngestionResponse>("/market/ingest", {
      method: "POST",
      body: JSON.stringify({ period }),
      headers: authHeaders(),
    });
  },
};
