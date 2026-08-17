"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Edit2, X, Check } from "lucide-react";
import { ExtractedInvoice, updateExtraction } from "@/lib/api";
import { formatCurrency, formatDate, formatStatus, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

interface DataTableProps {
  extractionId: string;
  data: ExtractedInvoice;
  status: "success" | "partial" | "failed";
  filename: string;
}

const statusColors: Record<string, string> = {
  green: "bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-300",
  yellow: "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-900 dark:text-yellow-300",
  red: "bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900 dark:text-red-300",
  gray: "bg-gray-100 text-gray-800 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300",
};

function PaymentStatusBadge({ amountPaid, total }: { amountPaid: number | null; total: number | null }) {
  if (total == null) return null;
  const paid = amountPaid ?? 0;
  if (paid >= total) {
    return <Badge variant="default" className="bg-green-500 text-white dark:bg-green-600">Paid</Badge>;
  }
  if (paid > 0) {
    return <Badge variant="secondary">Partial</Badge>;
  }
  return <Badge variant="outline">Unpaid</Badge>;
}

function LineItemCard({ item, index, currency, isEditing, handleLineItemChange }: { item: ExtractedInvoice["line_items"][number]; index: number; currency: string; isEditing: boolean; handleLineItemChange: (index: number, field: keyof ExtractedInvoice["line_items"][number], value: string) => void }) {
  return (
    <Card key={index} className="p-4 space-y-3 border-border/60 bg-card/90">
      <div className="space-y-2">
        <Label className="text-xs text-muted-foreground">Description</Label>
        {isEditing ? (
          <Input value={item.description} onChange={(e) => handleLineItemChange(index, "description", e.target.value)} />
        ) : (
          <p className="font-medium">{item.description}</p>
        )}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Quantity</Label>
          {isEditing ? (
            <Input type="number" value={item.quantity ?? ""} onChange={(e) => handleLineItemChange(index, "quantity", e.target.value)} />
          ) : (
            <p>{item.quantity ?? "N/A"}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Unit Price</Label>
          {isEditing ? (
            <Input type="number" value={item.unit_price ?? ""} onChange={(e) => handleLineItemChange(index, "unit_price", e.target.value)} />
          ) : (
            <p>{formatCurrency(item.unit_price, currency)}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground">Total</Label>
          {isEditing ? (
            <Input type="number" value={item.total ?? ""} onChange={(e) => handleLineItemChange(index, "total", e.target.value)} />
          ) : (
            <p className="font-semibold">{formatCurrency(item.total, currency)}</p>
          )}
        </div>
      </div>
    </Card>
  );
}

export default function DataTable({ extractionId, data, status, filename }: DataTableProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState<ExtractedInvoice>(data);

  const statusInfo = formatStatus(status);

  const handleFieldChange = (field: keyof ExtractedInvoice, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: field.includes("amount") || field.includes("subtotal") || field.includes("tax") || field.includes("quantity") || field.includes("price")
        ? value === "" ? null : parseFloat(value)
        : value,
    }));
  };

  const handleLineItemChange = (index: number, field: keyof ExtractedInvoice["line_items"][number], value: string) => {
    setFormData((prev) => {
      const newLineItems = [...prev.line_items];
      newLineItems[index] = {
        ...newLineItems[index],
        [field]: field === "description" ? value : value === "" ? null : parseFloat(value),
      };
      return { ...prev, line_items: newLineItems };
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateExtraction(extractionId, formData);
      toast.success("Extraction updated successfully!");
      setIsEditing(false);
    } catch (error) {
      toast.error("Failed to update extraction.");
      console.error(error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData(data);
    setIsEditing(false);
  };

  const handleMarkPaid = async () => {
    if (formData.total_amount == null) return;
    setIsSaving(true);
    try {
      await updateExtraction(extractionId, { ...formData, amount_paid: formData.total_amount });
      setFormData((prev) => ({ ...prev, amount_paid: prev.total_amount }));
      toast.success("Marked as fully paid!");
    } catch (error) {
      toast.error("Failed to mark as paid.");
      console.error(error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-2 sm:space-y-0 pb-2">
          <div>
            <h2 className="text-xl font-bold">{filename}</h2>
            <Badge className={cn("mt-2", statusColors[statusInfo.color] || statusColors.gray)}>
              {statusInfo.label}
            </Badge>
          </div>
          <div className="flex gap-2 w-full sm:w-auto">
            {!isEditing ? (
              <Button variant="outline" onClick={() => setIsEditing(true)} className="flex-1 sm:flex-none">
                <Edit2 className="w-4 h-4 mr-2" /> Edit
              </Button>
            ) : (
              <>
                <Button variant="outline" onClick={handleCancel} disabled={isSaving} className="flex-1 sm:flex-none">
                  <X className="w-4 h-4 mr-2" /> Cancel
                </Button>
                <Button onClick={handleSave} disabled={isSaving} className="flex-1 sm:flex-none">
                  {isSaving ? "Saving..." : <><Check className="w-4 h-4 mr-2" /> Save</>}
                </Button>
              </>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Fields grid - responsive: 1 col on mobile, 2 on sm, 4 on lg */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {(["vendor_name", "invoice_number", "invoice_date", "due_date", "currency", "subtotal", "tax", "total_amount"] as const).map((field) => (
              <div key={field} className="space-y-2">
                <Label className="capitalize text-sm">{field.replace("_", " ")}</Label>
                {isEditing ? (
                  <Input
                    value={formData[field] ?? ""}
                    onChange={(e) => handleFieldChange(field, e.target.value)}
                  />
                ) : (
                  <div className={cn("text-sm", field.includes("amount") && "text-xl font-bold")}>
                    {field.includes("date")
                      ? formatDate(formData[field] as string)
                      : field.includes("amount") || field.includes("subtotal") || field.includes("tax")
                      ? formatCurrency(formData[field] as number, formData.currency || "USD")
                      : (formData[field] ?? "N/A")}
                  </div>
                )}
              </div>
            ))}
            <div className="space-y-2">
              <Label className="text-sm">Entry Type</Label>
              {isEditing ? (
                <div className="flex gap-2">
                  {(["debit", "credit"] as const).map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setFormData((prev) => ({ ...prev, entry_type: type }))}
                      className={cn(
                        "flex-1 rounded-md border px-3 py-2 text-sm font-medium capitalize transition-colors",
                        formData.entry_type === type
                          ? type === "credit"
                            ? "border-green-500 bg-green-500/10 text-green-700 dark:text-green-300"
                            : "border-primary bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-muted"
                      )}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-sm">
                  {formData.entry_type ? (
                    <Badge className={formData.entry_type === "credit" ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300" : ""}>
                      {formData.entry_type}
                    </Badge>
                  ) : (
                    <Badge>debit</Badge>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Payment section */}
          <div className="rounded-2xl border border-border/60 bg-muted/30 p-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">Payment</h3>
                <PaymentStatusBadge amountPaid={formData.amount_paid} total={formData.total_amount} />
              </div>
              {!isEditing && formData.total_amount != null && (formData.amount_paid ?? 0) < formData.total_amount && (
                <Button variant="outline" size="sm" onClick={handleMarkPaid} disabled={isSaving} className="w-full sm:w-auto">
                  {isSaving ? "Saving..." : <><Check className="w-4 h-4 mr-2" /> Mark as Paid</>}
                </Button>
              )}
            </div>
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">Total Amount</Label>
                <p className="text-lg font-semibold">{formatCurrency(formData.total_amount, formData.currency || "INR")}</p>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">Amount Paid</Label>
                {isEditing ? (
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    value={formData.amount_paid ?? ""}
                    onChange={(e) => setFormData((prev) => ({ ...prev, amount_paid: e.target.value === "" ? null : parseFloat(e.target.value) }))}
                  />
                ) : (
                  <p className="text-lg font-semibold text-green-600 dark:text-green-400">
                    {formatCurrency(formData.amount_paid ?? 0, formData.currency || "INR")}
                  </p>
                )}
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">Balance Due</Label>
                <p className="text-lg font-semibold text-amber-600 dark:text-amber-400">
                  {formatCurrency(
                    formData.total_amount != null ? Math.max(0, formData.total_amount - (formData.amount_paid ?? 0)) : null,
                    formData.currency || "INR"
                  )}
                </p>
              </div>
            </div>
          </div>

          <Separator />

          {/* Line Items - responsive: table on desktop, cards on mobile */}
          <div className="space-y-2">
            <h3 className="font-semibold">Line Items</h3>
            {/* Desktop Table */}
            <div className="hidden lg:block overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Description</TableHead>
                    <TableHead>Quantity</TableHead>
                    <TableHead>Unit Price</TableHead>
                    <TableHead>Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {formData.line_items.length > 0 ? (
                    formData.line_items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          {isEditing ? <Input value={item.description} onChange={(e) => handleLineItemChange(index, "description", e.target.value)} /> : item.description}
                        </TableCell>
                        <TableCell>
                          {isEditing ? <Input type="number" value={item.quantity ?? ""} onChange={(e) => handleLineItemChange(index, "quantity", e.target.value)} /> : item.quantity ?? "N/A"}
                        </TableCell>
                        <TableCell>
                          {isEditing ? <Input type="number" value={item.unit_price ?? ""} onChange={(e) => handleLineItemChange(index, "unit_price", e.target.value)} /> : formatCurrency(item.unit_price, formData.currency || "USD")}
                        </TableCell>
                        <TableCell>
                          {isEditing ? <Input type="number" value={item.total ?? ""} onChange={(e) => handleLineItemChange(index, "total", e.target.value)} /> : formatCurrency(item.total, formData.currency || "USD")}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center text-muted-foreground">No line items found</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
            {/* Mobile Card Layout */}
            <div className="lg:hidden space-y-3">
              {formData.line_items.length > 0 ? (
                formData.line_items.map((item, index) => (
                  <LineItemCard
                    key={`line-item-${index}`}
                    item={item}
                    index={index}
                    currency={formData.currency || "USD"}
                    isEditing={isEditing}
                    handleLineItemChange={handleLineItemChange}
                  />
                ))
              ) : (
                <Card className="p-6 text-center border-dashed border-border/60">
                  <p className="text-muted-foreground">No line items found</p>
                </Card>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
