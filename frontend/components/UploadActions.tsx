"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Camera, UploadCloud, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { uploadInvoice, getApiErrorMessage } from "@/lib/api";
import { cn } from "@/lib/utils";

interface UploadActionsProps {
  hasLLMConfig?: boolean;
}

/**
 * Camera + Upload Invoice action buttons shown side-by-side on the
 * homepage. Both trigger a hidden file input; the camera variant uses
 * `capture="environment"` so mobile browsers open the rear camera.
 * Selected files are uploaded through the same flow as the drag-drop
 * Uploader and redirect to the result page on success.
 */
export default function UploadActions({ hasLLMConfig = true }: UploadActionsProps) {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    if (!file) return;
    if (!hasLLMConfig) {
      toast.error("Configure an LLM provider in Settings first");
      router.push("/settings");
      return;
    }

    setIsUploading(true);
    try {
      const result = await uploadInvoice(file);
      toast.success("Extraction successful!");
      router.push(`/result/${result.extraction_id}`);
    } catch (error) {
      const detail = getApiErrorMessage(error);
      if (detail.includes("No API key configured") || detail.includes("LLM configuration")) {
        toast.error("Configure an LLM provider in Settings first");
        router.push("/settings");
      } else {
        toast.error("Extraction failed. Try again.");
        console.error(error);
      }
    } finally {
      setIsUploading(false);
    }
  };

  const buttonBase = cn(
    "h-32 flex flex-col items-center justify-center gap-3 rounded-xl border transition-all",
    "text-muted-foreground hover:bg-muted/50 active:scale-[0.98]",
    "disabled:pointer-events-none disabled:opacity-50",
  );

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Hidden file inputs */}
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUpload(file);
          e.target.value = "";
        }}
      />
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,application/pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleUpload(file);
          e.target.value = "";
        }}
      />

      <button
        type="button"
        className={cn(buttonBase, "border-muted-foreground/20 hover:border-primary/50")}
        onClick={() => cameraInputRef.current?.click()}
        disabled={isUploading || !hasLLMConfig}
        aria-label="Take a photo of your invoice"
      >
        <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center">
          <Camera className="w-6 h-6 text-secondary" />
        </div>
        <span className="text-sm font-medium">Camera</span>
      </button>

      <button
        type="button"
        className={cn(buttonBase, "border-muted-foreground/20 hover:border-primary/50")}
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading || !hasLLMConfig}
        aria-label="Upload an invoice file"
      >
        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
          {isUploading ? (
            <Loader2 className="w-6 h-6 text-primary animate-spin" />
          ) : (
            <UploadCloud className="w-6 h-6 text-primary" />
          )}
        </div>
        <span className="text-sm font-medium">Upload Invoice</span>
      </button>
    </div>
  );
}
