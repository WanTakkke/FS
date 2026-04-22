import { create } from "zustand";

import type { CurrentUser, TokenResponse } from "../types/rbac";

const TOKEN_STORAGE_KEY = "rbac_tokens";
const USER_STORAGE_KEY = "rbac_current_user";

interface AuthTokens {
  accessToken: string;
  refreshToken?: string | null;
}

interface AuthState {
  tokens: AuthTokens | null;
  currentUser: CurrentUser | null;
  isAuthenticated: boolean;
  setTokens: (tokenData: TokenResponse) => void;
  setCurrentUser: (user: CurrentUser | null) => void;
  logout: () => void;
}

function loadTokens(): AuthTokens | null {
  const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthTokens;
  } catch {
    return null;
  }
}

function loadCurrentUser(): CurrentUser | null {
  const raw = localStorage.getItem(USER_STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as CurrentUser;
  } catch {
    return null;
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  tokens: loadTokens(),
  currentUser: loadCurrentUser(),
  isAuthenticated: Boolean(loadTokens()?.accessToken),
  setTokens: (tokenData) => {
    const nextTokens: AuthTokens = {
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token ?? null,
    };
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(nextTokens));
    set({ tokens: nextTokens, isAuthenticated: true });
  },
  setCurrentUser: (user) => {
    if (!user) {
      localStorage.removeItem(USER_STORAGE_KEY);
      set({ currentUser: null });
      return;
    }
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    set({ currentUser: user });
  },
  logout: () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    set({ tokens: null, currentUser: null, isAuthenticated: false });
  },
}));
