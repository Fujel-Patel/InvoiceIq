"use client";

import React, { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Eye, EyeOff, Loader2, Lock } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthLayout from "@/components/AuthLayout";
import PasswordStrength from "@/components/PasswordStrength";
import { resetPassword, getApiErrorMessage, getApiFieldErrors } from "@/lib/api";
import { isValidEmail } from "@/lib/validation";

interface FormErrors {
  password?: string;
  confirmPassword?: string;
}

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams?.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const handleReset = async (event: React.FormEvent) => {
    event.preventDefault();

    const nextErrors: FormErrors = {};
    if (password.length < 8) {
      nextErrors.password = "Password must be at least 8 characters.";
    }
    if (!/[A-Z]/.test(password)) {
      nextErrors.password = (nextErrors.password || "") + " Must contain an uppercase letter.";
    }
    if (!/[a-z]/.test(password)) {
      nextErrors.password = (nextErrors.password || "") + " Must contain a lowercase letter.";
    }
    if (!/[0-9]/.test(password)) {
      nextErrors.password = (nextErrors.password || "") + " Must contain a number.";
    }
    if (confirmPassword !== password) nextErrors.confirmPassword = "Passwords do not match.";
    if (!token) nextErrors.password = "This reset link is invalid or has expired.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setLoading(true);
    try {
      await resetPassword(password, token);
      toast.success("Password updated successfully. Please sign in.");
      router.replace("/login");
    } catch (error) {
      const fieldErrors = getApiFieldErrors(error);
      if (fieldErrors.length > 0) {
        const inlineErrors: FormErrors = {};
        for (const fieldError of fieldErrors) {
          if (fieldError.loc.includes("password")) inlineErrors.password = fieldError.msg;
        }
        if (Object.keys(inlineErrors).length > 0) {
          setErrors(inlineErrors);
          return;
        }
      }
      toast.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleReset} className="space-y-4" noValidate>
      <div className="space-y-1.5">
        <Label htmlFor="password">New password</Label>
        <div className="relative">
          <Lock className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Create a strong password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            aria-invalid={Boolean(errors.password)}
            className="pl-9 pr-9"
          />
          <button
            type="button"
            onClick={() => setShowPassword((current) => !current)}
            aria-label={showPassword ? "Hide password" : "Show password"}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-sm p-1 text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.password && <p className="text-xs text-destructive">{errors.password}</p>}
        <PasswordStrength password={password} />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="confirm-password">Confirm new password</Label>
        <div className="relative">
          <Lock className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            id="confirm-password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Re-enter your new password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            aria-invalid={Boolean(errors.confirmPassword)}
            className="pl-9"
          />
        </div>
        {errors.confirmPassword && (
          <p className="text-xs text-destructive">{errors.confirmPassword}</p>
        )}
      </div>

      <Button type="submit" className="w-full" size="lg" disabled={loading}>
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Reset password
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <AuthLayout title="Choose a new password" description="Loading…" showBack>
          <div className="space-y-4" />
        </AuthLayout>
      }
    >
      <AuthLayout
        title="Choose a new password"
        description="Your new password must be different from your previous passwords."
        showBack
      >
        <ResetPasswordForm />
      </AuthLayout>
    </Suspense>
  );
}