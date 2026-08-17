"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  FileText,
  ChevronRight,
  Clock,
  Building2,
  Inbox
} from "lucide-react";
import { HistoryItem } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface HistoryListProps {
  items: HistoryItem[];
}

const statusVariants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  success: "default",
  partial: "secondary",
  failed: "destructive",
};

export default function HistoryList({ items }: HistoryListProps) {
  const router = useRouter();

  if (items.length === 0) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center justify-center rounded-3xl border border-dashed bg-background/80 p-10 text-center shadow-sm backdrop-blur">
        <Inbox className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold">No extractions yet</h3>
        <p className="mb-6 text-sm text-muted-foreground">Upload an invoice to get started</p>
        <Button onClick={() => router.push("/")}>Upload Invoice</Button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-xl font-bold">Recent Extractions</h2>
          <p className="text-sm text-muted-foreground">Tap any row to open its invoice details.</p>
        </div>
        <Badge variant="secondary" className="w-fit">{items.length}</Badge>
      </div>

      {items.map((item, index) => (
        <motion.div
          key={item.extraction_id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
          whileHover={{ scale: 1.01 }}
        >
          <Card
            className="group w-full cursor-pointer overflow-hidden border-border/60 bg-card/90 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
            onClick={() => router.push(`/result/${item.extraction_id}`)}
          >
            <CardContent className="grid gap-4 p-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
              <div className="flex min-w-0 items-start gap-3 sm:gap-4">
                <div className="rounded-xl bg-primary/10 p-2.5 text-primary shrink-0">
                  <FileText className="h-5 w-5 shrink-0" />
                </div>
                <div className="min-w-0 space-y-1.5">
                  <p className="truncate text-sm sm:text-base font-medium leading-tight">
                    {item.filename.length > 25 ? `${item.filename.substring(0, 25)}...` : item.filename}
                  </p>
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs sm:text-sm text-muted-foreground">
                    <span className="inline-flex min-w-0 items-center gap-1.5 truncate">
                      <Building2 className="h-3 w-3 shrink-0" />
                      <span className="truncate">{item.vendor_name || "Unknown Vendor"}</span>
                    </span>
                    <span className="hidden sm:inline">•</span>
                    <span className="inline-flex items-center gap-1.5">
                      <Clock className="h-3 w-3 shrink-0" />
                      {formatDate(item.extracted_at)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2 sm:gap-3 sm:justify-end">
                <div className="text-left sm:text-right">
                  <p className="text-xs text-muted-foreground">Amount</p>
                  <p className="font-semibold text-base">{formatCurrency(item.total_amount)}</p>
                  {item.balance_due != null && item.balance_due > 0 ? (
                    <p className="mt-0.5 text-xs font-medium text-amber-600 dark:text-amber-400">
                      Balance: {formatCurrency(item.balance_due)}
                    </p>
                  ) : item.balance_due === 0 && item.total_amount != null ? (
                    <p className="mt-0.5 text-xs font-medium text-green-600 dark:text-green-400">Paid</p>
                  ) : null}
                </div>
                <Badge variant={statusVariants[item.status] || "outline"} className="capitalize text-xs py-1 px-2">
                  {item.status}
                </Badge>
                <ChevronRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
