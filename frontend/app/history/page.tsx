"use client";

import { useQuery, QueryClient, QueryClientProvider, useIsFetching } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { ArrowLeft, History, RefreshCw, AlertCircle } from "lucide-react";
import { getHistory } from "@/lib/api";
import HistoryList from "@/components/HistoryList";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const queryClient = new QueryClient();

function HistoryContent() {
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["history"],
    queryFn: () => getHistory(),
    staleTime: 10000,
    refetchOnWindowFocus: true,
  });
  const isFetching = useIsFetching({ queryKey: ["history"] });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28 w-full rounded-2xl" />
          ))}
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-24 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="mx-auto flex max-w-xl flex-col items-center justify-center rounded-3xl border bg-background/80 p-10 text-center shadow-sm backdrop-blur"
      >
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-xl font-bold">Failed to load history</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Try reloading the data if the connection is unstable.
        </p>
        <Button className="mt-6" onClick={() => refetch()}>
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
    <>
      <nav className="sticky top-0 z-20 border-b border-border/60 bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <Button variant="ghost" size="sm" className="w-fit px-2 sm:px-3" onClick={() => router.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">Back</span>
          </Button>
          <div className="flex items-center gap-3 sm:gap-2">
            <History className="w-5 h-5 text-primary" />
            <div>
              <h1 className="text-lg font-semibold leading-tight sm:text-xl">Extraction History</h1>
              <p className="text-sm text-muted-foreground">Review every invoice extraction in one place.</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => queryClient.invalidateQueries({ queryKey: ["history"] })} disabled={isFetching > 0}>
            <motion.div whileTap={{ scale: 0.9 }}>
              <RefreshCw className={'h-4 w-4 ' + (isFetching ? 'animate-spin' : '')} />
            </motion.div>
          </Button>
        </div>
      </nav>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-6 lg:px-8"
      >
        <motion.section
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3"
        >
          {[
            { label: "Total Extractions", value: stats.total, valueClassName: "text-foreground" },
            { label: "Successful", value: stats.successful, valueClassName: "text-green-600" },
            { label: "Failed", value: stats.failed, valueClassName: "text-red-600" },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              whileHover={{ scale: 1.01 }}
              className={isFetching ? "opacity-80" : ""}
            >
              <Card className="h-full overflow-hidden border-border/60 bg-card/90 shadow-sm transition-shadow hover:shadow-md">
                <CardContent className="flex h-full flex-col justify-between p-6">
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className={`mt-2 text-3xl font-semibold tracking-tight ${stat.valueClassName}`}>
                    {stat.value}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.section>

        <HistoryList items={items} />
    </motion.div>
    </>
  );
}

export default function HistoryPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
        <HistoryContent />
      </div>
    </QueryClientProvider>
  );
}
