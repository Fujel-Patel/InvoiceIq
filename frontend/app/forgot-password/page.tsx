"use client";

import React, { useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { CheckCircle2, Loader2, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import AuthLayout from "@/components/AuthLayout";
import { forgotPassword, getApiErrorMessage } from "@/lib/api";
import { isValidEmail } from "@/lib/validation";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!isValidEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await forgotPassword(email.trim().toLowerCase());
      setSubmitted(true);
      toast.success("Password reset link sent. Please check your email.");
    } catch (submitError) {
      toast.error(getApiErrorMessage(submitError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Reset your password"
      description="Enter your email and we'll send you a link to reset your password."
      showBack
    >
      {submitted ? (
        <div className="space-y-4 rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-5 text-left">
          <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-500">
            <CheckCircle2 className="h-5 w-5" />
            <p className="text-sm font-medium">Check your inbox</p>
          </div>
          <p className="text-sm text-muted-foreground">
            If an account exists for <span className="font-medium text-foreground">{email}</span>,
            we&apos;ve sent a password reset link. Follow the link to create a new password.
          </p>
          <Link
            href="/login"
            className="inline-block text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            Back to login
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                aria-invalid={Boolean(error)}
                className="pl-9"
              />
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
          </div>

          <Button type="submit" className="w-full" size="lg" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Send reset link
          </Button>
        </form>
      )}
    </AuthLayout>
  );
}