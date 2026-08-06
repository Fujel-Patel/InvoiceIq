"use client";

import { CheckCircle2, Circle } from "lucide-react";

import { getPasswordRequirements, getPasswordStrength } from "@/lib/validation";
import { cn } from "@/lib/utils";

interface PasswordStrengthProps {
  password: string;
}

const LABELS = ["Weak", "Fair", "Good", "Strong"];
const COLORS = ["bg-destructive", "bg-amber-500", "bg-yellow-500", "bg-emerald-500"];

export default function PasswordStrength({ password }: PasswordStrengthProps) {
  const requirements = getPasswordRequirements(password);
  const strength = getPasswordStrength(password);
  const level = Math.min(strength, 4) - 1;
  const label = password.length === 0 ? "" : LABELS[Math.max(level, 0)];

  return (
    <div className="space-y-2">
      {password.length > 0 && (
        <div className="flex items-center gap-1.5">
          {[0, 1, 2, 3].map((bar) => (
            <div
              key={bar}
              className={cn(
                "h-1 flex-1 rounded-full bg-border",
                bar <= level && COLORS[Math.max(level, 0)]
              )}
            />
          ))}
          <span className="ml-1 text-xs text-muted-foreground">{label}</span>
        </div>
      )}

      <ul className="grid grid-cols-2 gap-x-3 gap-y-1">
        {requirements.map((requirement) => (
          <li
            key={requirement.label}
            className={cn(
              "flex items-center gap-1.5 text-xs",
              requirement.met ? "text-emerald-600 dark:text-emerald-500" : "text-muted-foreground"
            )}
          >
            {requirement.met ? (
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
            ) : (
              <Circle className="h-3.5 w-3.5 shrink-0" />
            )}
            {requirement.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
