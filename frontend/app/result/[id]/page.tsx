"use client";

import { useParams, useRouter } from "next/navigation";
import { useQuery, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowLeft, AlertCircle, RefreshCw, History, Zap } from "lucide-react";
import Link from "next/link";
import { getExtraction } from "@/lib/api";
import DataTable from "@/components/DataTable";
import ExportButtons from "@/components/ExportButtons";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Header } from "@/components/Header";

const queryClient = new QueryClient();

function ResultContent() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["extraction", id],
    queryFn: () => getExtraction(id),
    staleTime: 30000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  if (isError || !data) {
    // Check if this is an API key configuration error
    const isApiKeyError = error?.message?.includes('No API key configured') ||
                         error?.message?.includes('LLM configuration not found');

    if (isApiKeyError) {
      return (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex flex-col items-center justify-center p-12 text-center"
        >
          <AlertCircle className="w-12 h-12 text-destructive mb-4" />
          <h2 className="text-xl font-bold">API Key Not Configured</h2>
          <p className="text-muted-foreground mb-6">
            You need to configure your LLM provider and API key before extracting invoice data.
          </p>
          <Button
            onClick={() => router.push('/settings')}
            variant="default"
          >
            <Zap className="mr-2 h-4 w-4" /> Go to Settings
          </Button>
        </motion.div>
      );
    }

    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex flex-col items-center justify-center p-12 text-center"
      >
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold">Failed to load extraction</h2>
        <p className="text-muted-foreground mb-6">{error?.message || "Unknown error occurred"}</p>
        <Button onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" /> Retry
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <DataTable
        extractionId={id}
        data={data.data}
        status={data.status}
        filename={`Invoice_${id.substring(0, 8)}.pdf`}
      />
      <ExportButtons extractionId={id} />
    </motion.div>
  );
}

export default function ResultPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-muted/20">
        <Header />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <ResultContent />
        </main>
      </div>
    </QueryClientProvider>
  );
}
