"use client";

import { useQuery, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { ArrowLeft, History, RefreshCw, AlertCircle } from "lucide-react";
import { Toaster, toast } from "sonner";
import { getHistory } from "@/lib/api";
import HistoryList from "@/components/HistoryList";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

const queryClient = new QueryClient();

function HistoryContent() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["history", "test_user"],
    queryFn: () => getHistory("test_user"),
    staleTime: 10000,
    refetchOnWindowFocus: true,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
        {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-20 w-full" />)}
      </div>
    );
  }

  if (isError) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex flex-col items-center justify-center p-12 text-center"
      >
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold">Failed to load history</h2>
        <Button onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" /> Retry
        </Button>
      </motion.div>
    );
  }

  const items = data || [];
  const stats = {
    total: items.length,
    successful: items.filter((i) => i.status === "success").length,
    failed: items.filter((i) => i.status === "failed").length,
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-3 gap-4"
      >
        <Card><CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Total Extractions</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </CardContent></Card>
        <Card><CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Successful</p>
          <p className="text-2xl font-bold text-green-600">{stats.successful}</p>
        </CardContent></Card>
        <Card><CardContent className="p-6">
          <p className="text-sm text-muted-foreground">Failed</p>
          <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
        </CardContent></Card>
      </motion.div>

      <HistoryList items={items} />
    </motion.div>
  );
}

export default function HistoryPage() {
  const router = useRouter();

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-muted/20">
        <Toaster position="top-right" richColors />

        <nav className="border-b bg-background sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <Button variant="ghost" size="sm" onClick={() => router.push("/")}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Back
            </Button>
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-primary" />
              <h1 className="font-bold text-lg">Extraction History</h1>
            </div>
            <Button variant="ghost" size="icon" onClick={() => queryClient.invalidateQueries({ queryKey: ["history", "test_user"] })}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-6 py-8">
          <HistoryContent />
        </main>
      </div>
    </QueryClientProvider>
  );
}
