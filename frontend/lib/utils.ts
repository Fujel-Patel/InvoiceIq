import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines clsx and tailwind-merge to handle conditional className merging.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Formats a number as currency. Returns "N/A" if amount is invalid.
 * Falls back to INR if currency code is invalid.
 */
export function formatCurrency(
  amount: number | null | undefined,
  currency: string = "INR"
): string {
  if (amount == null) return "N/A";
  try {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: currency,
    }).format(amount);
  } catch {
    // Fallback to INR if currency code is invalid
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
    }).format(amount);
  }
}

/**
 * Formats a date string to a human-readable format.
 */
export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return "Invalid Date";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

/**
 * Returns a status label and color mapping based on status string.
 */
export function formatStatus(status: string): { label: string; color: string } {
  switch (status.toLowerCase()) {
    case "success":
      return { label: "Success", color: "green" };
    case "partial":
      return { label: "Partial", color: "yellow" };
    case "failed":
      return { label: "Failed", color: "red" };
    default:
      return { label: "Unknown", color: "gray" };
  }
}
