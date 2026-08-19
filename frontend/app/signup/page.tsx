"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Eye, EyeOff, Loader2, Lock, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import AuthLayout from "@/components/AuthLayout";
import PasswordStrength from "@/components/PasswordStrength";
import { signup, getApiErrorMessage, getApiFieldErrors } from "@/lib/api";
import { isValidEmail } from "@/lib/validation";
import { useAuthStore } from "@/store/useAuthStore";

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}

export default function SignupPage() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const handleSignup = async (event: React.FormEvent) => {
    event.preventDefault();

    const nextErrors: FormErrors = {};
    if (!isValidEmail(email)) nextErrors.email = "Please enter a valid email address.";
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
    if (!acceptedTerms) {
      toast.error("Please accept the Terms & Privacy Policy to continue.");
      return;
    }
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setLoading(true);
    try {
      const data = await signup(email.trim().toLowerCase(), password);
      setUser({
        id: data.user_id,
        email: data.email,
        emailConfirmed: data.email_confirmed,
      });
      toast.success(data.message);
      router.replace("/");
    } catch (error) {
      const fieldErrors = getApiFieldErrors(error);
      if (fieldErrors.length > 0) {
        const inlineErrors: FormErrors = {};
        for (const fieldError of fieldErrors) {
          const field = fieldError.loc[fieldError.loc.length - 1];
          if (field === "email") inlineErrors.email = fieldError.msg;
          if (field === "password") inlineErrors.password = fieldError.msg;
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
    <AuthLayout
      title="Create your account"
      description="Sign up in seconds — no credit card required."
    >
      <form onSubmit={handleSignup} className="space-y-4" noValidate>
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
              aria-invalid={Boolean(errors.email)}
              className="pl-9"
            />
          </div>
          {errors.email && <p className="text-xs text-destructive">{errors.email}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password">Password</Label>
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
          <Label htmlFor="confirm-password">Confirm password</Label>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="confirm-password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Re-enter your password"
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

        <Checkbox
          id="terms"
          checked={acceptedTerms}
          onCheckedChange={setAcceptedTerms}
          label={
            <span className="text-sm text-muted-foreground">
              I agree to the{" "}
              <a href="#" className="font-medium text-primary underline-offset-4 hover:underline">
                Terms of Service
              </a>{" "}
              and{" "}
              <a href="#" className="font-medium text-primary underline-offset-4 hover:underline">
                Privacy Policy
              </a>
            </span>
          }
        />

        <Button
          type="submit"
          className="w-full"
          size="lg"
          disabled={loading || !acceptedTerms}
        >
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Create Account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary underline-offset-4 hover:underline">
          Login
        </Link>
      </p>
    </AuthLayout>
  );
}