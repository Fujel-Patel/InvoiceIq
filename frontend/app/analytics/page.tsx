"use client";

import { useQuery, QueryClient, QueryClientProvider, useIsFetching } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  BarChart3,
  RefreshCw,
  AlertCircle,
  Wallet,
  TrendingUp,
  TrendingDown,
  Receipt,
  Landmark,
  Percent,
  Store,
  Scale,
  Inbox,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { getAnalytics, AnalyticsPeriod, AnalyticsVendor, AnalyticsBill } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const queryClient = new QueryClient();

function compactCurrency(value: number, currency: string): string {
  const symbol = currencySymbol(currency);
  const abs = Math.abs(value);
  if (abs >= 1000000) return `${symbol}${(abs / 1000000).toFixed(1)}M`;
  if (abs >= 1000) return `${symbol}${(abs / 1000).toFixed(abs >= 100000 ? 0 : 1)}k`;
  return `${symbol}${abs.toFixed(0)}`;
}

function PaymentBadge({ status }: { status: string }) {
  if (status === "paid") {
    return <Badge className="bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-300">Paid</Badge>;
  }
  if (status === "partial") {
    return <Badge variant="secondary">Partial</Badge>;
  }
  return <Badge variant="outline">Unpaid</Badge>;
}

function currencySymbol(currency: string): string {
  try {
    const part = new Intl.NumberFormat("en-US", { style: "currency", currency })
      .formatToParts(0)
      .find((p) => p.type === "currency");
    return part?.value ?? "";
  } catch {
    return "";
  }
}

function TrendChart({ data, currency, accent }: { data: AnalyticsPeriod[]; currency: string; accent: string }) {
  if (data.length === 0) {
    return <p className="py-10 text-center text-sm text-muted-foreground">No data available yet.</p>;
  }
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
          <XAxis
            dataKey="period"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            interval="preserveStartEnd"
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            width={46}
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            tickFormatter={(v: number) => compactCurrency(v, currency)}
          />
          <Tooltip
            cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid hsl(var(--border))",
              background: "hsl(var(--card))",
              fontSize: 13,
            }}
            formatter={(value: unknown) => [formatCurrency(Number(value), currency), "Total"]}
            labelFormatter={(label: unknown) => `${String(label)} · ${data.find((d) => d.period === label)?.count ?? 0} bill(s)`}
          />
          <Bar dataKey="total" fill={accent} radius={[6, 6, 0, 0]} maxBarSize={48} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function VendorChart({ vendors, currency }: { vendors: AnalyticsVendor[]; currency: string }) {
  if (vendors.length === 0) {
    return <p className="py-10 text-center text-sm text-muted-foreground">No vendors yet.</p>;
  }
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={vendors} layout="vertical" margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
          <XAxis
            type="number"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            tickFormatter={(v: number) => compactCurrency(v, currency)}
          />
          <YAxis
            type="category"
            dataKey="vendor"
            width={110}
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          />
          <Tooltip
            cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid hsl(var(--border))",
              background: "hsl(var(--card))",
              fontSize: 13,
            }}
            formatter={(value: unknown) => [formatCurrency(Number(value), currency), "Total"]}
          />
          <Bar dataKey="total" fill="hsl(var(--primary))" radius={[0, 6, 6, 0]} maxBarSize={18} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function BillsTable({ bills, currency }: { bills: AnalyticsBill[]; currency: string }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle>All Bills</CardTitle>
        <Badge variant="secondary" className="w-fit">{bills.length}</Badge>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Bill</TableHead>
              <TableHead>Vendor</TableHead>
              <TableHead>Invoice #</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Due Date</TableHead>
              <TableHead>Subtotal</TableHead>
              <TableHead>Tax</TableHead>
              <TableHead className="text-right">Total</TableHead>
              <TableHead>Paid</TableHead>
              <TableHead className="text-right">Balance</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {bills.map((bill) => (
              <TableRow key={bill.extraction_id}>
                <TableCell className="max-w-[180px] truncate font-medium" title={bill.filename}>
                  {bill.filename}
                </TableCell>
                <TableCell>{bill.vendor_name || "Unknown"}</TableCell>
                <TableCell>{bill.invoice_number || "N/A"}</TableCell>
                <TableCell>{formatDate(bill.invoice_date)}</TableCell>
                <TableCell>{formatDate(bill.due_date)}</TableCell>
                <TableCell>{formatCurrency(bill.subtotal, bill.currency || currency)}</TableCell>
                <TableCell>{formatCurrency(bill.tax, bill.currency || currency)}</TableCell>
                <TableCell className="text-right font-semibold">
                  {formatCurrency(bill.total_amount, bill.currency || currency)}
                </TableCell>
                <TableCell className="text-green-600 dark:text-green-400">
                  {formatCurrency(bill.amount_paid ?? 0, bill.currency || currency)}
                </TableCell>
                <TableCell className={`text-right font-medium ${bill.balance_due > 0 ? "text-amber-600 dark:text-amber-400" : "text-muted-foreground"}`}>
                  {bill.balance_due > 0 ? formatCurrency(bill.balance_due, bill.currency || currency) : "—"}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={bill.entry_type === "credit" ? "secondary" : "default"}
                    className={
                      bill.entry_type === "credit"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                        : ""
                    }
                  >
                    {bill.entry_type === "credit" ? "Credit" : "Debit"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <PaymentBadge status={bill.payment_status} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function AnalyticsContent() {
  const router = useRouter();
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => getAnalytics(),
    staleTime: 10000,
    refetchOnWindowFocus: true,
  });
  const isFetching = useIsFetching({ queryKey: ["analytics"] });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32 w-full rounded-2xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {[1, 2].map((i) => (
            <Skeleton key={i} className="h-80 w-full rounded-2xl" />
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
        <h2 className="text-xl font-bold">Failed to load analytics</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Try reloading the data if the connection is unstable.
        </p>
        <Button className="mt-6" onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" /> Retry
        </Button>
      </motion.div>
    );
  }

  const analytics = data!;
  const s = analytics.summary;
  const currency = s.currency;
  const combinedLabel = `Combined: ${formatCurrency(s.combined_total, currency)}`;

  return (
    <>
      <nav className="sticky top-0 z-20 border-b border-border/60 bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <Button variant="ghost" size="sm" className="w-fit px-2 sm:px-3" onClick={() => router.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            <span className="hidden sm:inline">Back</span>
          </Button>
          <div className="flex items-center gap-3 sm:gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            <div>
              <h1 className="text-lg font-semibold leading-tight sm:text-xl">Bill Analytics</h1>
              <p className="text-sm text-muted-foreground">Debit, credit, and monthly trends across all bills.</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={() => queryClient.invalidateQueries({ queryKey: ["analytics"] })} disabled={isFetching > 0}>
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
        {analytics.bills.length === 0 ? (
          <div className="mx-auto flex max-w-2xl flex-col items-center justify-center rounded-3xl border border-dashed bg-background/80 p-10 text-center shadow-sm backdrop-blur">
            <Inbox className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold">No bills yet</h3>
            <p className="mb-6 text-sm text-muted-foreground">Upload an invoice or create a direct bill to see analytics.</p>
            <div className="flex gap-3">
              <Button onClick={() => router.push("/")}>Upload Invoice</Button>
              <Button variant="outline" onClick={() => router.push("/direct-bill")}>Create Direct Bill</Button>
            </div>
          </div>
        ) : (
          <>
            <motion.section
              initial={{ opacity: 0, y: -16 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4"
            >
              <StatCard icon={<Receipt className="h-5 w-5 text-primary" />} label="Total Bills" value={String(s.total_invoices)} sub={`${s.unique_vendors} unique vendor(s)`} accent />
              <StatCard
                icon={<TrendingUp className="h-5 w-5 text-red-500" />}
                label="Total Debit (Spend)"
                value={formatCurrency(s.total_debit, currency)}
                sub={combinedLabel}
              />
              <StatCard
                icon={<TrendingDown className="h-5 w-5 text-green-500" />}
                label="Total Credit (Income)"
                value={formatCurrency(s.total_credit, currency)}
                sub={combinedLabel}
              />
              <StatCard icon={<Landmark className="h-5 w-5 text-primary" />} label="Combined Total" value={formatCurrency(s.combined_total, currency)} sub={`${s.total_invoices} bill(s) total`} accent />
              <StatCard icon={<Scale className="h-5 w-5 text-amber-500" />} label="Net (Debit − Credit)" value={formatCurrency(s.net_total, currency)} sub="Spend after credits" />
              <StatCard icon={<Percent className="h-5 w-5 text-violet-500" />} label="Total Tax" value={formatCurrency(s.total_tax, currency)} sub={`Avg bill ${formatCurrency(s.avg_amount, currency)}`} />
              <StatCard icon={<Store className="h-5 w-5 text-sky-500" />} label="Unique Vendors" value={String(s.unique_vendors)} sub={`${s.total_invoices} invoice(s)`} />
              <StatCard
                icon={<Wallet className="h-5 w-5 text-green-500" />}
                label="Total Collected"
                value={formatCurrency(s.total_collected, currency)}
                sub={`${s.paid_bills} bill(s) paid`}
              />
              <StatCard
                icon={<TrendingUp className="h-5 w-5 text-amber-500" />}
                label="Total Outstanding"
                value={formatCurrency(s.total_outstanding, currency)}
                sub={`${s.outstanding_bills} bill(s) pending`}
              />
            </motion.section>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <Card className="border-border/60 bg-card/90 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle>Monthly Breakdown</CardTitle>
                  <p className="text-sm text-muted-foreground">Total per month</p>
                </CardHeader>
                <CardContent>
                  <TrendChart data={analytics.monthly} currency={currency} accent="hsl(var(--primary))" />
                </CardContent>
              </Card>
              <Card className="border-border/60 bg-card/90 shadow-sm">
                <CardHeader className="pb-2">
                  <CardTitle>Weekly Breakdown</CardTitle>
                  <p className="text-sm text-muted-foreground">Total per week (ISO week)</p>
                </CardHeader>
                <CardContent>
                  <TrendChart data={analytics.weekly} currency={currency} accent="hsl(217 91% 60%)" />
                </CardContent>
              </Card>
            </div>

            <Card className="border-border/60 bg-card/90 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle>Top Vendors</CardTitle>
                <p className="text-sm text-muted-foreground">Total billed per vendor</p>
              </CardHeader>
              <CardContent>
                <VendorChart vendors={analytics.vendors} currency={currency} />
              </CardContent>
            </Card>

            <BillsTable bills={analytics.bills} currency={currency} />
          </>
        )}
      </motion.div>
    </>
  );
}

function StatCard({
  icon,
  label,
  value,
  sub,
  accent = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  accent?: boolean;
}) {
  return (
    <motion.div whileHover={{ scale: 1.01 }}>
      <Card className="h-full overflow-hidden border-border/60 bg-card/90 shadow-sm transition-shadow hover:shadow-md">
        <CardContent className="flex h-full flex-col justify-between p-6">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm text-muted-foreground">{label}</p>
            <div className={accent ? "rounded-xl bg-primary/10 p-2 text-primary" : ""}>{icon}</div>
          </div>
          <p className={accent ? "mt-3 text-2xl font-semibold tracking-tight text-primary" : "mt-3 text-2xl font-semibold tracking-tight"}>
            {value}
          </p>
          {sub ? <p className="mt-1 text-xs text-muted-foreground">{sub}</p> : null}
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default function AnalyticsPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
        <AnalyticsContent />
      </div>
    </QueryClientProvider>
  );
}
