import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format date to Indian Standard Time (IST)
 * @param dateStr - ISO date string or Date object
 * @param formatType - "datetime" (full), "date" (date only), "time" (time only), "short" (short datetime)
 */
export function formatIST(
  dateStr: string | Date | null | undefined, 
  formatType: "datetime" | "date" | "time" | "short" = "datetime"
): string {
  if (!dateStr) return "-";
  try {
    const date = typeof dateStr === "string" ? new Date(dateStr) : dateStr;
    if (isNaN(date.getTime())) return "-";
    
    const options: Intl.DateTimeFormatOptions = {
      timeZone: "Asia/Kolkata",
    };
    
    switch (formatType) {
      case "datetime":
        return date.toLocaleString("en-IN", {
          ...options,
          year: "numeric",
          month: "short",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
      case "date":
        return date.toLocaleString("en-IN", {
          ...options,
          year: "numeric",
          month: "short",
          day: "2-digit",
        });
      case "time":
        return date.toLocaleString("en-IN", {
          ...options,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        });
      case "short":
        return date.toLocaleString("en-IN", {
          ...options,
          month: "short",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        });
      default:
        return date.toLocaleString("en-IN", { ...options });
    }
  } catch {
    return "-";
  }
}

