"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  getLLMConfig,
  saveLLMConfig,
  deleteLLMConfig,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Label } from "@/components/ui/label";

const providers = [
  { value: "anthropic", label: "Anthropic (Claude)" },
  { value: "openai", label: "OpenAI" },
  { value: "gemini", label: "Google Gemini" },
  { value: "groq", label: "Groq" },
  { value: "openrouter", label: "OpenRouter" },
];

export default function LLMConfigPage() {
  const [provider, setProvider] = useState<string>("anthropic");
  const [apiKey, setApiKey] = useState<string>("");
  const [model, setModel] = useState<string>("");
  const [loading, setLoading] = useState(false);

  // Load existing config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      const cfg = await getLLMConfig();
      if (cfg) {
        setProvider(cfg.provider ?? "anthropic");
        setApiKey(cfg.masked_api_key ?? "");
        setModel(cfg.model ?? "");
      }
    };
    fetchConfig();
  }, []);

  const handleSave = async () => {
    if (!apiKey) {
      toast.error("API key is required");
      return;
    }
    setLoading(true);
    try {
      await saveLLMConfig({ provider, api_key: apiKey, model });
      toast.success("LLM configuration saved");
    } catch {
      toast.error("Failed to save LLM configuration");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await deleteLLMConfig();
      setProvider("anthropic");
      setApiKey("");
      setModel("");
      toast.success("LLM configuration deleted");
    } catch {
      toast.error("Failed to delete configuration");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col items-center p-8")}>
  <div className="w-full max-w-lg mb-4">
    <Link href="/" className="flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-primary">
      <ArrowLeft className="w-4 h-4" />
      Back
    </Link>
  </div>
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>LLM Provider Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
            <div>
              <Label htmlFor="provider" className="block mb-1">Provider</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger>
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                {providers.map(p => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">API Key</label>
            <Input
              type="password"
              placeholder="Enter API key"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Model (optional)</label>
            <Input
              placeholder="e.g., claude-opus-4-5-20251001"
              value={model}
              onChange={e => setModel(e.target.value)}
            />
          </div>
          <div className="flex space-x-2 pt-4">
            <Button onClick={handleSave} disabled={loading} className="flex-1">
              Save Configuration
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={loading}>
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
