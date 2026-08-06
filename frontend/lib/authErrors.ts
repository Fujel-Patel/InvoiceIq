import axios from "axios";
import { getApiErrorMessage } from "./api";

export function getAuthErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    switch (error.response?.status) {
      case 401:
        return "Invalid email or password.";
      case 403:
        return "Please verify your email address before signing in.";
      case 409:
        return "An account with this email already exists. Please log in instead.";
      case 429:
        return "Too many attempts. Please wait a moment and try again.";
      case 502:
      case 503:
        return "Authentication service is temporarily unavailable. Please try again.";
      default:
        break;
    }
  }
  return getApiErrorMessage(error) || "An unexpected error occurred. Please try again.";
}
