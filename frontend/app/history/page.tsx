"use client";

import { useQuery, QueryClient, QueryClientProvider, useIsFetching } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { AlertCircle, RefreshCw } from "lucide-react";
import { getHistory } from "@/lib/api";
import HistoryList from "@/components/HistoryList";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Header } from "@/components/Header";

const queryClient = new QueryClient();

function HistoryContent() {
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
      <Header />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-6 lg:px-8"
      >
        <motion.section
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {[
            { label: "Total Extractions", value: stats.total, valueClassName: "text-foreground" },
            { label: "Successful", value: stats.successful, valueClassName: "text-green-600 dark:text-green-400" },
            { label: "Failed", value: stats.failed, valueClassName: "text-red-600 dark:text-red-400" },
          ].map((stat) => (
            <motion.div
              key={stat.label}
              whileHover={{ scale: 1.01 }}
              className={isFetching ? "opacity-80" : ""}
            >
              <Card className="h-full overflow-hidden border-border/60 bg-card/90 shadow-sm transition-shadow hover:shadow-md">
                <CardContent className="flex h-full flex-col justify-between p-4 sm:p-6">
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className={`mt-2 text-2xl sm:text-3xl font-semibold tracking-tight ${stat.valueClassName}`}>
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
