"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  getLLMConfig,
  saveLLMConfig,
  verifyLLMConfig,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, CheckCircle2, XCircle, Loader2, ArrowLeft, Sparkles, Zap, Shield, Brain } from "lucide-react";
import { Header } from "@/components/Header";

interface ProviderInfo {
  value: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  models: string[];
}

const providers: ProviderInfo[] = [
  {
    value: "anthropic",
    label: "Anthropic",
    icon: <Sparkles className="w-5 h-5" />,
    description: "Claude models for advanced AI capabilities",
    models: ["claude-opus-4-5-20251001", "claude-sonnet-4-5-20250929", "claude-3-5-haiku-20241022"],
  },
  {
    value: "openai",
    label: "OpenAI",
    icon: <Zap className="w-5 h-5" />,
    description: "GPT models for general purpose tasks",
    models: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
  },
  {
    value: "google",
    label: "Google",
    icon: <Shield className="w-5 h-5" />,
    description: "Gemini models for multimodal processing",
    models: ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
  },
  {
    value: "groq",
    label: "Groq",
    icon: <Brain className="w-5 h-5" />,
    description: "Ultra-fast inference with Llama models",
    models: ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
  },
];

interface LLMConfigResponse {
  provider: string;
  model: string;
  is_valid: boolean;
  masked_api_key: string;
  user_id: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [config, setConfig] = useState<LLMConfigResponse | null>(null);
  const [provider, setProvider] = useState("google");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("");
  const [isVerified, setIsVerified] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const cfg = await getLLMConfig();
        setConfig(cfg);
        if (cfg) {
          setProvider(cfg.provider);
          setModel(cfg.model);
          setApiKey("");
          setIsVerified(cfg.is_valid);
        }
      } finally {
        setLoading(false);
      }
    };
    fetchConfig();
  }, []);

  const handleVerify = async () => {
    if (!apiKey) {
      toast.error("API key is required to verify");
      return;
    }
    setVerifying(true);
    try {
      const result = await verifyLLMConfig({
        provider: provider as "anthropic" | "openai" | "google" | "groq",
        api_key: apiKey,
        model,
      });
      if (result.is_valid) {
        toast.success("API key verified successfully");
        setIsVerified(true);
      } else {
        toast.error(result.message || "Verification failed");
        setIsVerified(false);
      }
    } catch {
      toast.error("Verification failed. Please try again.");
      setIsVerified(false);
    } finally {
      setVerifying(false);
    }
  };

  const handleSave = async () => {
    if (!isVerified) {
      toast.error("Please verify your API key first");
      return;
    }
    setSaving(true);
    try {
      await saveLLMConfig({
        provider,
        api_key: apiKey,
        model,
      });
      toast.success("Configuration saved successfully");
      const updated = await getLLMConfig();
      setConfig(updated);
    } catch {
      toast.error("Failed to save configuration");
    } finally {
      setSaving(false);
    }
  };

  const selectedProvider = providers.find((p) => p.value === provider);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/20">
      <Header />

      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Back button in content area */}
        <div className="mb-6 sm:hidden">
          <Button variant="ghost" size="sm" onClick={() => router.back()} className="w-full justify-start">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </div>

        {/* SECTION 1: Current Config Status Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Current Configuration
            </CardTitle>
            <CardDescription>Active LLM provider status</CardDescription>
          </CardHeader>
          <CardContent>
            {config ? (
              <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex-1 space-y-3">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Provider</p>
                    <Badge variant="default" className="text-sm">
                      {providers.find((p) => p.value === config.provider)?.label || config.provider}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">API Key</p>
                    <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                      {config.masked_api_key}
                    </code>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Model</p>
                    <code className="text-sm font-mono">{config.model}</code>
                  </div>
                </div>
                <div>
                  <Badge
                    variant={config.is_valid ? "default" : "destructive"}
                    className="gap-1.5 text-sm px-3 py-1"
                  >
                    {config.is_valid ? (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Verified
                      </>
                    ) : (
                      <>
                        <XCircle className="w-3.5 h-3.5" />
                        Not Verified
                      </>
                    )}
                  </Badge>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No configuration set yet.</p>
            )}
          </CardContent>
        </Card>

        {/* SECTION 2: Provider Selection */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Select Provider</CardTitle>
            <CardDescription>Choose your preferred LLM provider</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {providers.map((p) => (
                <button
                  key={p.value}
                  onClick={() => {
                    setProvider(p.value);
                    setModel("");
                    setIsVerified(false);
                  }}
                  className={cn(
                    "flex flex-col items-start gap-3 p-4 rounded-lg border-2 transition-all text-left min-h-[140px]",
                    provider === p.value
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <span className={cn("text-primary", provider === p.value && "")}>{p.icon}</span>
                    <span className="font-medium">{p.label}</span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">{p.description}</p>
                  <div className="flex flex-wrap gap-1 mt-auto">
                    {p.models.map((m) => (
                      <Badge key={m} variant="outline" className="text-[10px] px-1.5 py-0 whitespace-nowrap">
                        {m}
                      </Badge>
                    ))}
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* SECTION 3: Configuration Form */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Enter your API key and select a model</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiKey">API Key</Label>
              <div className="relative">
                <Input
                  id="apiKey"
                  type={showApiKey ? "text" : "password"}
                  placeholder="Enter your API key"
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    if (isVerified) setIsVerified(false);
                  }}
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-muted-foreground">
                Get your API key from{" "}
                <a
                  href="https://console.anthropic.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  Anthropic Console
                </a>{" "}
                or{" "}
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  OpenAI Platform
                </a>
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select value={model} onValueChange={setModel}>
                <SelectTrigger id="model">
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  {selectedProvider?.models.map((m) => (
                    <SelectItem key={m} value={m}>
                      {m}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* SECTION 4: Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handleVerify}
            disabled={verifying || !apiKey}
            variant="outline"
            className="flex-1"
          >
            {verifying ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Verify API Key
              </>
            )}
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || !isVerified}
            className="flex-1"
          >
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Save Configuration
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
