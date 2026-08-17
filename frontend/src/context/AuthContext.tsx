"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { api, UserProfile } from "@/lib/api";

interface AuthContextType {
  token: string | null;
  email: string | null;
  fullName: string | null;
  profile: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, email: string, fullName?: string) => void;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<UserProfile | null>;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  email: null,
  fullName: null,
  profile: null,
  isAuthenticated: false,
  isLoading: true,
  login: () => {},
  logout: async () => {},
  refreshProfile: async () => null,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [fullName, setFullName] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("gravity_auth_token");
    const savedEmail = localStorage.getItem("gravity_user_email");
    const savedFullName = localStorage.getItem("gravity_user_fullname");

    if (savedToken) {
      setToken(savedToken);
      setEmail(savedEmail);
      setFullName(savedFullName);
      api
        .getProfile()
        .then((prof) => setProfile(prof))
        .catch(() => {
          // Profile might not exist yet or token expired.
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = (newToken: string, newEmail: string, newFullName?: string) => {
    localStorage.setItem("gravity_auth_token", newToken);
    localStorage.setItem("gravity_user_email", newEmail);

    if (newFullName) {
      localStorage.setItem("gravity_user_fullname", newFullName);
    } else {
      localStorage.removeItem("gravity_user_fullname");
    }

    setToken(newToken);
    setEmail(newEmail);
    setFullName(newFullName ?? null);

    api
      .getProfile()
      .then((prof) => setProfile(prof))
      .catch(() => setProfile(null));
  };

  const logout = async () => {
    try {
      if (token) {
        await api.logout();
      }
    } catch {
      // Ignore network errors on logout.
    } finally {
      localStorage.removeItem("gravity_auth_token");
      localStorage.removeItem("gravity_user_email");
      localStorage.removeItem("gravity_user_fullname");
      setToken(null);
      setEmail(null);
      setFullName(null);
      setProfile(null);
    }
  };

  const refreshProfile = async (): Promise<UserProfile | null> => {
    try {
      const prof = await api.getProfile();
      setProfile(prof);
      return prof;
    } catch {
      setProfile(null);
      return null;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        email,
        fullName,
        profile,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
