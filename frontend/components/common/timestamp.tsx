"use client";

import { format, formatDistanceToNow } from "date-fns";

interface TimestampProps {
  date: string | Date;
  format?: "relative" | "absolute" | "datetime" | "date" | "time";
  className?: string;
}

export function Timestamp({ date, format: formatType = "relative", className }: TimestampProps) {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  let displayText = "";

  switch (formatType) {
    case "relative":
      displayText = formatDistanceToNow(dateObj, { addSuffix: true });
      break;
    case "absolute":
      displayText = format(dateObj, "MMM dd, yyyy HH:mm:ss");
      break;
    case "datetime":
      displayText = format(dateObj, "MMM dd, yyyy HH:mm");
      break;
    case "date":
      displayText = format(dateObj, "MMM dd, yyyy");
      break;
    case "time":
      displayText = format(dateObj, "HH:mm:ss");
      break;
  }

  return (
    <time dateTime={dateObj.toISOString()} className={className}>
      {displayText}
    </time>
  );
}

