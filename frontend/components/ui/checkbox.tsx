import * as React from "react"
import { Check } from "lucide-react"

import { cn } from "@/lib/utils"

interface CheckboxProps
  extends Omit<React.ComponentProps<"input">, "type" | "checked" | "onChange"> {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  label?: React.ReactNode
}

function Checkbox({ className, checked, onCheckedChange, label, ...props }: CheckboxProps) {
  return (
    <label className={cn("inline-flex cursor-pointer select-none items-center gap-2", className)}>
      <span
        aria-checked={checked}
        role="checkbox"
        className={cn(
          "inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-sm border border-input bg-transparent transition-colors focus-within:ring-3 focus-within:ring-ring/50",
          checked && "border-primary bg-primary"
        )}
      >
        {checked && <Check className="h-3 w-3 text-primary-foreground" />}
        <input
          type="checkbox"
          className="sr-only"
          checked={checked}
          onChange={(event) => onCheckedChange(event.target.checked)}
          {...props}
        />
      </span>
      {label}
    </label>
  )
}

export { Checkbox }
