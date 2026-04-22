import axios from "axios";
import { message } from "antd";

import { useUiStore } from "../store/uiStore";
import type { ApiResponse } from "../types/common";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";

export const http = axios.create({
  baseURL,
  timeout: 20000,
});

http.interceptors.request.use(
  (config) => {
    useUiStore.getState().increasePending();
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
  (error) => {
    useUiStore.getState().decreasePending();
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
