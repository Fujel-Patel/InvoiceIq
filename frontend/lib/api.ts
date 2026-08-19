import axios from 'axios';
import { supabase } from "./supabaseClient";

// Interfaces
export interface LineItem {
  description: string;
  quantity: number | null;
  unit_price: number | null;
  total: number | null;
}

export interface ExtractedInvoice {
  vendor_name: string | null;
  invoice_number: string | null;
  invoice_date: string | null;
  due_date: string | null;
  line_items: LineItem[];
  subtotal: number | null;
  tax: number | null;
  total_amount: number | null;
  currency: string | null;
  entry_type: "debit" | "credit" | null;
  amount_paid: number | null;
}

export interface ExtractionResponse {
  extraction_id: string;
  status: "success" | "partial" | "failed";
  data: ExtractedInvoice;
  raw_text: string | null;
}

export interface HistoryItem {
  extraction_id: string;
  filename: string;
  extracted_at: string;
  vendor_name: string | null;
  total_amount: number | null;
  amount_paid: number | null;
  balance_due: number | null;
  status: string;
}

// Analytics Interfaces
export interface AnalyticsSummary {
  total_invoices: number;
  total_debit: number;
  total_credit: number;
  combined_total: number;
  net_total: number;
  total_tax: number;
  avg_amount: number;
  unique_vendors: number;
  currency: string;
  total_collected: number;
  total_outstanding: number;
  paid_bills: number;
  outstanding_bills: number;
}

export interface AnalyticsPeriod {
  period: string;
  total: number;
  count: number;
}

export interface AnalyticsVendor {
  vendor: string;
  total: number;
  count: number;
}

export interface AnalyticsBill {
  extraction_id: string;
  filename: string;
  vendor_name: string | null;
  invoice_number: string | null;
  invoice_date: string | null;
  due_date: string | null;
  subtotal: number | null;
  tax: number | null;
  total_amount: number | null;
  currency: string | null;
  entry_type: "debit" | "credit" | null;
  amount_paid: number | null;
  balance_due: number;
  payment_status: string;
  status: string;
  extracted_at: string;
}

export interface AnalyticsResponse {
  summary: AnalyticsSummary;
  monthly: AnalyticsPeriod[];
  weekly: AnalyticsPeriod[];
  vendors: AnalyticsVendor[];
  bills: AnalyticsBill[];
}

// LLM Config Interfaces
interface LLMConfig {
  provider: string;
  model: string;
  api_key: string;
}

export interface LLMConfigResponse {
  provider: string;
  model: string;
  is_valid: boolean;
  masked_api_key: string;
  user_id: string;
}

interface VerifyLLMRequest {
  provider: string;
  api_key: string;
  model: string;
}

export interface VerifyLLMResponse {
  is_valid: boolean;
  message: string;
  provider: string;
}

// Axios Instance
const api = axios.create({
  baseURL:
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    (process.env.NODE_ENV === 'production'
      ? 'https://invoiceiq-7wec.onrender.com/api/v1'
      : 'http://localhost:8765/api/v1'),
});

api.interceptors.request.use(async (config) => {
  try {
    const { data: session } = await supabase.auth.getSession();
    const token = session?.session?.access_token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch {
    // Supabase unreachable — backend uses dev auth bypass
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Clear any stored dev session and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('invoiceiq-dev-session')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
);

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const first = detail[0];
      if (first && typeof first === "object" && "msg" in first) {
        const msg = (first as { msg?: unknown }).msg;
        if (typeof msg === "string") return msg;
      }
    }
    if (detail && typeof detail === "object" && "msg" in detail) {
      const msg = (detail as { msg?: unknown }).msg;
      if (typeof msg === "string") return msg;
    }
    return error.message;
  }
  return error instanceof Error ? error.message : "";
}

export interface ApiFieldError {
  loc: string[];
  msg: string;
}

export function getApiFieldErrors(error: unknown): ApiFieldError[] {
  if (!axios.isAxiosError(error)) return [];
  const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;
  if (!Array.isArray(detail)) return [];
  return detail
    .filter(
      (item): item is { loc: string[]; msg: string } =>
        typeof item === "object" &&
        item !== null &&
        Array.isArray((item as { loc?: unknown }).loc) &&
        typeof (item as { msg?: unknown }).msg === "string"
    )
    .map((item) => ({ loc: item.loc, msg: item.msg }));
}

/**
 * Uploads an invoice file for extraction.
 */
export async function uploadInvoice(file: File): Promise<ExtractionResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<ExtractionResponse>('/extract/upload', formData);
  return response.data;
}

/**
 * Creates a direct bill manually without uploading a file.
 */
export async function createDirectBill(data: ExtractedInvoice): Promise<ExtractionResponse> {
  const response = await api.post<ExtractionResponse>('/extract/direct-bill', data);
  return response.data;
}

/**
 * Retrieves a specific extraction result by ID.
 */
export async function getExtraction(id: string): Promise<ExtractionResponse> {
  const response = await api.get<ExtractionResponse>(`/extract/${id}`);
  return response.data;
}

/**
 * Updates an extraction result with new data.
 */
export async function updateExtraction(id: string, data: Partial<ExtractedInvoice>): Promise<ExtractionResponse> {
  const response = await api.put<ExtractionResponse>(`/extract/${id}`, data);
  return response.data;
}

/**
 * Retrieves extraction history for a user.
 */
export async function getHistory(user_id?: string): Promise<HistoryItem[]> {
  const requestConfig = user_id !== undefined ? { params: { user_id } } : undefined;
  const response = await api.get<HistoryItem[]>('/history', requestConfig);
  return response.data;
}

/**
 * Retrieves aggregated analytics across all bills.
 */
export async function getAnalytics(): Promise<AnalyticsResponse> {
  const response = await api.get<AnalyticsResponse>('/analytics');
  return response.data;
}

/**
 * Exports extraction data to CSV or Excel.
 */
export async function exportExtraction(
  extraction_id: string,
  format: "csv" | "excel"
): Promise<void> {
  try {
    const response = await api.post('/export',
      { extraction_ids: [extraction_id], format },
      { responseType: 'blob' }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `invoice_export.${format === 'csv' ? 'csv' : 'xlsx'}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Export failed', error);
    throw error;
  }
}

// LLM Config Functions
export async function getLLMConfig(signal?: AbortSignal): Promise<LLMConfigResponse | null> {
  const response = await api.get<LLMConfigResponse | null>('/llm/config', { signal });
  return response.data;
}

export async function saveLLMConfig(config: LLMConfig): Promise<LLMConfigResponse> {
  const existing = await getLLMConfig();
  if (existing) {
    const response = await api.put<LLMConfigResponse>('/llm/config', config);
    return response.data;
  }
  const response = await api.post<LLMConfigResponse>('/llm/config', config);
  return response.data;
}

export async function verifyLLMConfig(config: VerifyLLMRequest): Promise<VerifyLLMResponse> {
  const response = await api.post<VerifyLLMResponse>('/llm/verify', config);
  return response.data;
}

export async function deleteLLMConfig(): Promise<void> {
  await api.delete('/llm/config');
}

// Auth Functions
export interface AuthUser {
  id: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export interface SignupResponse {
  user_id: string;
  email: string;
  email_confirmed: boolean;
  message: string;
}

export interface MeResponse {
  user_id: string;
  email: string | null;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>("/auth/login", { email, password });
  return response.data;
}

export async function signup(email: string, password: string): Promise<SignupResponse> {
  const response = await api.post<SignupResponse>("/auth/signup", { email, password });
  return response.data;
}

export async function forgotPassword(email: string): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/auth/forgot-password", { email });
  return response.data;
}

export async function resetPassword(password: string, token: string): Promise<{ message: string }> {
  const response = await api.post<{ message: string }>("/auth/reset-password", { password, token });
  return response.data;
}

export async function getMe(): Promise<MeResponse> {
  const response = await api.get<MeResponse>("/auth/me");
  return response.data;
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout');
}

export default api;
