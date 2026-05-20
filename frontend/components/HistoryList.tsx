"use client";

import { motion } from "motion/react";
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
      <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed rounded-xl bg-muted/20">
        <Inbox className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold">No extractions yet</h3>
        <p className="text-sm text-muted-foreground mb-6">Upload an invoice to get started</p>
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
      <div className="flex items-center gap-2">
        <h2 className="text-xl font-bold">Extraction History</h2>
        <Badge variant="secondary">{items.length}</Badge>
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
            className="cursor-pointer hover:bg-accent/50 transition-colors"
            onClick={() => router.push(`/result/${item.extraction_id}`)}
          >
            <CardContent className="flex items-center justify-between p-4 gap-4">
              <div className="flex items-center gap-4 min-w-0">
                <FileText className="w-8 h-8 text-primary shrink-0" />
                <div className="min-w-0">
                  <p className="font-medium truncate max-w-[200px] sm:max-w-[300px]">
                    {item.filename.length > 30 ? `${item.filename.substring(0, 30)}...` : item.filename}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                    <Building2 className="w-3 h-3" />
                    {item.vendor_name || "Unknown Vendor"}
                    <span className="mx-1">•</span>
                    <Clock className="w-3 h-3" />
                    {formatDate(item.extracted_at)}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="text-right">
                  <p className="font-semibold">{formatCurrency(item.total_amount)}</p>
                </div>
                <Badge variant={statusVariants[item.status] || "outline"} className="capitalize">
                  {item.status}
                </Badge>
                <ChevronRight className="w-5 h-5 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
