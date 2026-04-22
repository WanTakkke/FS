import axios, { AxiosError } from "axios";
import type { AxiosRequestConfig } from "axios";
import { message } from "antd";

import { useUiStore } from "../store/uiStore";
import { useAuthStore } from "../store/authStore";
import type { ApiResponse } from "../types/common";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";

export const http = axios.create({
  baseURL,
  timeout: 20000,
});

const refreshClient = axios.create({
  baseURL,
  timeout: 20000,
});

let refreshPromise: Promise<string | null> | null = null;
type RetriableRequest = AxiosRequestConfig & {
  _retry?: boolean;
};

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;
  const refreshToken = useAuthStore.getState().tokens?.refreshToken;
  if (!refreshToken) return null;
  refreshPromise = refreshClient
    .post("/api/user/refresh", { refresh_token: refreshToken })
    .then((res) => {
      const payload = res.data as ApiResponse<{
        access_token: string;
        refresh_token?: string | null;
        token_type: string;
        expires_in?: number | null;
      }>;
      if (payload.code !== 200 || !payload.data?.access_token) {
        return null;
      }
      useAuthStore.getState().setTokens(payload.data);
      return payload.data.access_token;
    })
    .catch(() => null)
    .finally(() => {
      refreshPromise = null;
    });
  return refreshPromise;
}

http.interceptors.request.use(
  (config) => {
    useUiStore.getState().increasePending();
    const accessToken = useAuthStore.getState().tokens?.accessToken;
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    useUiStore.getState().decreasePending();
    return Promise.reject(error);
  },
);

http.interceptors.response.use(
  (response) => {
    useUiStore.getState().decreasePending();
    return response;
  },
  async (error) => {
    useUiStore.getState().decreasePending();
    const axiosError = error as AxiosError;
    const originalRequest = axiosError?.config as RetriableRequest | undefined;
    if (error?.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      const nextAccessToken = await refreshAccessToken();
      if (nextAccessToken) {
        originalRequest.headers = originalRequest.headers ?? {};
        (originalRequest.headers as Record<string, string>).Authorization = `Bearer ${nextAccessToken}`;
        return http(originalRequest);
      }
      useAuthStore.getState().logout();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    const errorMessage =
      error?.response?.data?.message ??
      error?.message ??
      "请求失败，请稍后重试";
    message.error(errorMessage);
    return Promise.reject(error);
  },
);

export async function unwrapResponse<T>(promise: Promise<{ data: ApiResponse<T> }>) {
  const response = await promise;
  const payload = response.data;
  if (payload.code !== 200) {
    const businessError = payload.message || "业务请求失败";
    message.error(businessError);
    throw new Error(businessError);
  }
  return payload.data;
}
