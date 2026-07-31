"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { UploadCloud, X, Loader2, FileText, Image as ImageIcon, File } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { uploadInvoice } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function Uploader({ hasLLMConfig = true }: { hasLLMConfig?: boolean }) {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    if (fileRejections.length > 0) {
      const error = fileRejections[0].errors[0];
      if (error.code === "file-too-large") {
        toast.error("File must be under 10MB");
      } else if (error.code === "file-invalid-type") {
        toast.error("Only JPG, PNG, PDF allowed");
      } else {
        toast.error(error.message);
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [],
      "image/png": [],
      "application/pdf": [],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled: !hasLLMConfig,
  });

  const handleUpload = async () => {
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
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || "";
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

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return <ImageIcon className="w-8 h-8 text-primary" />;
    if (type === "application/pdf") return <FileText className="w-8 h-8 text-destructive" />;
    return <File className="w-8 h-8 text-muted-foreground" />;
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardContent className="pt-6">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {!file ? (
            <div
              {...getRootProps()}
              className={cn(
                "border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center text-center transition-colors",
                !hasLLMConfig
                  ? "border-muted-foreground/10 bg-muted/30 cursor-not-allowed opacity-60"
                  : isDragActive
                    ? "border-primary bg-primary/10 cursor-pointer"
                    : "border-muted-foreground/25 hover:border-primary/50 cursor-pointer"
              )}
            >
              <input {...getInputProps()} />
              <UploadCloud className="w-10 h-10 text-muted-foreground mb-4" />
              <p className="text-lg font-medium text-foreground">
                {hasLLMConfig ? "Drag & drop your invoice here" : "Configure an LLM provider to upload"}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                {hasLLMConfig ? "or click to browse" : "Go to Settings to add an API key"}
              </p>
              <p className="text-xs text-muted-foreground mt-4">JPG, PNG, PDF up to 10MB</p>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <div className="flex items-center gap-4 p-4 border rounded-lg bg-muted/50">
                {getFileIcon(file.type)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setFile(null)}
                  disabled={isUploading}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              <Button
                className="w-full"
                onClick={handleUpload}
                disabled={isUploading || !hasLLMConfig}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Extracting...
                  </>
                ) : (
                  "Extract Data"
                )}
              </Button>
            </motion.div>
          )}
        </motion.div>
      </CardContent>
    </Card>
  );
}
