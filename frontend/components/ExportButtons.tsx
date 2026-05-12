'use client';

interface ExtractionData {
  vendor_name: string;
  date: string;
  line_items: Array<{
    description: string;
    quantity: number;
    unit_price: number;
    total: number;
  }>;
  tax: number;
  total_amount: number;
  currency: string;
}

interface ExportButtonsProps {
  data: ExtractionData;
}

export default function ExportButtons({ data }: ExportButtonsProps) {
  const handleExportCSV = () => {
    // Create CSV content
    const headers = ['Description', 'Quantity', 'Unit Price', 'Total'];
    const rows = data.line_items.map(item => [
      item.description,
      item.quantity,
      `${data.currency} ${item.unit_price.toFixed(2)}`,
      `${data.currency} ${item.total.toFixed(2)}`
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(',')),
      '', // Empty row
      ['Subtotal', '', '', `${data.currency} ${data.line_items.reduce((sum, item) => sum + item.total, 0).toFixed(2)}`].join(','),
      ['Tax', '', '', `${data.currency} ${data.tax.toFixed(2)}`].join(','),
      ['Total Amount', '', '', `${data.currency} ${data.total_amount.toFixed(2)}`].join(',')
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `invoice_${data.date.replace(/-/g, '')}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportExcel = () => {
    // For simplicity, we'll create a CSV and treat it as Excel
    // In a real app, you might use a library like SheetJS or xlsx
    const headers = ['Description', 'Quantity', 'Unit Price', 'Total'];
    const rows = data.line_items.map(item => [
      item.description,
      item.quantity,
      `${data.currency} ${item.unit_price.toFixed(2)}`,
      `${data.currency} ${item.total.toFixed(2)}`
    ]);

    const csvContent = [
      headers.join('\t'), // Tab-separated for better Excel compatibility
      ...rows.map(row => row.join('\t')),
      '', // Empty row
      ['Subtotal', '', '', `${data.currency} ${data.line_items.reduce((sum, item) => sum + item.total, 0).toFixed(2)}`].join('\t'),
      ['Tax', '', '', `${data.currency} ${data.tax.toFixed(2)}`].join('\t'),
      ['Total Amount', '', '', `${data.currency} ${data.total_amount.toFixed(2)}`].join('\t')
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `invoice_${data.date.replace(/-/g, '')}.xlsx`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col sm:flex-row sm:space-x-3 mt-4">
      <button
        onClick={handleExportCSV}
        className="w-full sm:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Export as CSV
      </button>
      <button
        onClick={handleExportExcel}
        className="w-full sm:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
      >
        Export as Excel
      </button>
    </div>
  );
}