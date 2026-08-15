import type { AxiosError } from "axios";
import axios from "axios";
import { API_CONFIG, ENV } from "@/constants/config";

/** Shape of a single FastAPI 422 validation error detail item */
interface FastAPIValidationDetail {
  loc?: (string | number)[];
  msg: string;
  type?: string;
}

/**
 * Structured API Error class representing FastAPI / network error responses.
 */
export class ApiError extends Error {
  status?: number;
  code?: string;
  detail?: string | FastAPIValidationDetail[];
  isNetworkError: boolean;
  isTimeout: boolean;

  constructor({
    message,
    status,
    code,
    detail,
    isNetworkError = false,
    isTimeout = false,
  }: {
    message: string;
    status?: number;
    code?: string;
    detail?: string | FastAPIValidationDetail[];
    isNetworkError?: boolean;
    isTimeout?: boolean;
  }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.detail = detail;
    this.isNetworkError = isNetworkError;
    this.isTimeout = isTimeout;
  }
}

/**
 * Shared, centralized Axios API client.
 */
export const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Request Interceptor: Logging in Development
apiClient.interceptors.request.use(
  (config) => {
    if (ENV.IS_DEV) {
      // Optional debug logging in development mode
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Centralized FastAPI Error Parsing
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string | FastAPIValidationDetail[]; message?: string }>) => {
    const isNetworkError = !error.response && Boolean(error.request);
    const isTimeout =
      error.code === "ECONNABORTED" || error.message.toLowerCase().includes("timeout");

    let message = "An unexpected error occurred.";
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    if (isTimeout) {
      message = `Request timed out after ${API_CONFIG.TIMEOUT_MS / 1000}s. Please check backend response time.`;
    } else if (isNetworkError) {
      message = `Cannot connect to API at ${API_CONFIG.BASE_URL}. Ensure the FastAPI server is running.`;
    } else if (typeof detail === "string") {
      message = detail;
    } else if (Array.isArray(detail) && detail.length > 0) {
      // FastAPI 422 Validation Error
      message = (detail as FastAPIValidationDetail[])
        .map((d) => `${d.loc?.slice(1)?.join(".") ?? "field"}: ${d.msg}`)
        .join("; ");
    } else if (error.response?.data?.message) {
      message = error.response.data.message;
    } else if (error.message) {
      message = error.message;
    }

    const apiError = new ApiError({
      message,
      status,
      code: error.code,
      detail,
      isNetworkError,
      isTimeout,
    });

    return Promise.reject(apiError);
  }
);
