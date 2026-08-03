"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, Plus, Trash2, Save, Loader2, FilePlus2 } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { createDirectBill, type ExtractedInvoice, type LineItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface EditableLineItem {
  description: string;
  quantity: string;
  unit_price: string;
}

const emptyLine: EditableLineItem = { description: "", quantity: "", unit_price: "" };

export default function DirectBillPage() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [vendorName, setVendorName] = useState("");
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [invoiceDate, setInvoiceDate] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [entryType, setEntryType] = useState<"debit" | "credit">("debit");
  const [tax, setTax] = useState("");
  const [lineItems, setLineItems] = useState<EditableLineItem[]>([emptyLine]);

  const updateLine = (index: number, field: keyof EditableLineItem, value: string) => {
    setLineItems((items) => items.map((item, i) => (i === index ? { ...item, [field]: value } : item)));
  };

  const addLine = () => setLineItems((items) => [...items, emptyLine]);
  const removeLine = (index: number) => {
    setLineItems((items) => (items.length > 1 ? items.filter((_, i) => i !== index) : [emptyLine]));
  };

  const subtotal = lineItems.reduce(
    (sum, item) => sum + (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0),
    0
  );
  const taxValue = parseFloat(tax) || 0;
  const total = subtotal + taxValue;

  const handleSave = async () => {
    if (!vendorName.trim()) {
      toast.error("Vendor name is required");
      return;
    }

    const validItems: LineItem[] = lineItems
      .filter((item) => item.description.trim())
      .map((item) => ({
        description: item.description.trim(),
        quantity: item.quantity ? parseFloat(item.quantity) : null,
        unit_price: item.unit_price ? parseFloat(item.unit_price) : null,
        total: item.quantity && item.unit_price
          ? parseFloat(item.quantity) * parseFloat(item.unit_price)
          : null,
      }));

    if (validItems.length === 0) {
      toast.error("Add at least one line item");
      return;
    }

    const invoice: ExtractedInvoice = {
      vendor_name: vendorName.trim(),
      invoice_number: invoiceNumber.trim() || null,
      invoice_date: invoiceDate || null,
      due_date: dueDate || null,
      line_items: validItems,
      subtotal,
      tax: taxValue || null,
      total_amount: total,
      currency: currency || null,
      entry_type: entryType,
      amount_paid: null,
    };

    setSaving(true);
    try {
      const result = await createDirectBill(invoice);
      toast.success("Direct bill created!");
      router.push(`/result/${result.extraction_id}`);
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || "";
      if (detail.includes("No API key configured") || detail.includes("LLM configuration")) {
        toast.error("Configure an LLM provider in Settings first");
        router.push("/settings");
      } else {
        toast.error("Failed to create bill. Try again.");
        console.error(error);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-muted/20">
      <nav className="border-b bg-background sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <Button variant="ghost" size="sm" onClick={() => router.push("/")}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back
          </Button>
          <h1 className="font-bold text-lg flex items-center gap-2">
            <FilePlus2 className="w-5 h-5 text-primary" /> Create Direct Bill
          </h1>
          <div className="w-20" />
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-6"
        >
          {/* Bill Details */}
          <Card>
            <CardHeader>
              <CardTitle>Bill Details</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="vendorName">Vendor Name *</Label>
                <Input
                  id="vendorName"
                  value={vendorName}
                  onChange={(e) => setVendorName(e.target.value)}
                  placeholder="Acme Corp"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoiceNumber">Invoice Number</Label>
                <Input
                  id="invoiceNumber"
                  value={invoiceNumber}
                  onChange={(e) => setInvoiceNumber(e.target.value)}
                  placeholder="INV-001"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoiceDate">Bill Date</Label>
                <Input
                  id="invoiceDate"
                  type="date"
                  value={invoiceDate}
                  onChange={(e) => setInvoiceDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dueDate">Due Date</Label>
                <Input
                  id="dueDate"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <Input
                  id="currency"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  placeholder="INR"
                />
              </div>
              <div className="space-y-2">
                <Label>Entry Type</Label>
                <div className="flex gap-2">
                  {(["debit", "credit"] as const).map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setEntryType(type)}
                      className={
                        "flex-1 rounded-md border px-3 py-2 text-sm font-medium capitalize transition-colors " +
                        (entryType === type
                          ? type === "credit"
                            ? "border-green-500 bg-green-500/10 text-green-600 dark:text-green-400"
                            : "border-primary bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-muted")
                      }
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Line Items */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Line Items</CardTitle>
              <Button variant="outline" size="sm" onClick={addLine}>
                <Plus className="w-4 h-4 mr-1" /> Add Item
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {lineItems.map((item, index) => (
                <div
                  key={index}
                  className="grid grid-cols-[1fr_80px_100px_40px] gap-3 items-center"
                >
                  <Input
                    value={item.description}
                    onChange={(e) => updateLine(index, "description", e.target.value)}
                    placeholder="Item description"
                    aria-label={`Item ${index + 1} description`}
                  />
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    value={item.quantity}
                    onChange={(e) => updateLine(index, "quantity", e.target.value)}
                    placeholder="Qty"
                    aria-label={`Item ${index + 1} quantity`}
                  />
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    value={item.unit_price}
                    onChange={(e) => updateLine(index, "unit_price", e.target.value)}
                    placeholder="Price"
                    aria-label={`Item ${index + 1} unit price`}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive"
                    onClick={() => removeLine(index)}
                    aria-label={`Remove item ${index + 1}`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}

              {/* Totals */}
              <div className="pt-4 border-t space-y-1.5 text-sm">
                <div className="flex justify-between text-muted-foreground">
                  <span>Subtotal</span>
                  <span>{subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Tax</span>
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    value={tax}
                    onChange={(e) => setTax(e.target.value)}
                    placeholder="0.00"
                    className="w-28 h-8 text-right"
                    aria-label="Tax amount"
                  />
                </div>
                <div className="flex justify-between font-semibold text-base pt-1">
                  <span>Total</span>
                  <span>{total.toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => router.push("/")}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Bill
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
