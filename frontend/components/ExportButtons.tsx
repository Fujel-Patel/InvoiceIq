"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { FileText, FileSpreadsheet, Loader2 } from "lucide-react";
import { exportExtraction } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ExportButtonsProps {
  extractionId: string;
}

export default function ExportButtons({ extractionId }: ExportButtonsProps) {
  const [csvLoading, setCsvLoading] = useState(false);
  const [excelLoading, setExcelLoading] = useState(false);

  const handleExport = async (format: "csv" | "excel") => {
    if (format === "csv") setCsvLoading(true);
    else setExcelLoading(true);

    try {
      await exportExtraction(extractionId, format);
      toast.success(`${format.toUpperCase()} downloaded!`);
    } catch {
      toast.error("Export failed. Try again.");
    } finally {
      if (format === "csv") setCsvLoading(false);
      else setExcelLoading(false);
    }
  };

  const isLoading = csvLoading || excelLoading;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Export Data</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              variant="outline"
              className="w-full h-auto flex flex-col items-start p-4 gap-1"
              onClick={() => handleExport("csv")}
              disabled={isLoading}
            >
              <div className="flex items-center gap-2 font-semibold">
                {csvLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileText className="h-4 w-4" />
                )}
                Export as CSV
              </div>
              <span className="text-xs text-muted-foreground">Comma separated values</span>
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              className="w-full h-auto flex flex-col items-start p-4 gap-1"
              onClick={() => handleExport("excel")}
              disabled={isLoading}
            >
              <div className="flex items-center gap-2 font-semibold">
                {excelLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FileSpreadsheet className="h-4 w-4" />
                )}
                Export as Excel
              </div>
              <span className="text-xs text-muted-foreground">Microsoft Excel format</span>
            </Button>
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
