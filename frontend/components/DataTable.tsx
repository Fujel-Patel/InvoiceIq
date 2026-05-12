'use client';

interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

interface ExtractionData {
  vendor_name: string;
  date: string;
  line_items: LineItem[];
  tax: number;
  total_amount: number;
  currency: string;
}

interface DataTableProps {
  data: ExtractionData;
}

export default function DataTable({ data }: DataTableProps) {
  return (
    <div className="space-y-6">
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-medium mb-2">Vendor Information</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Vendor Name:</span>
            <span className="font-medium">{data.vendor_name}</span>
          </div>
          <div>
            <span className="text-gray-500">Date:</span>
            <span className="font-medium">{new Date(data.date).toLocaleDateString()}</span>
          </div>
          <div>
            <span className="text-gray-500">Currency:</span>
            <span className="font-medium">{data.currency}</span>
          </div>
        </div>
      </div>

      {data.line_items.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-2">Line Items</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unit Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.line_items.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {data.currency} {item.unit_price.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {data.currency} {item.total.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50">
                <tr>
                  <td className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                    Subtotal
                  </td>
                  <td className="px-6 py-4 text-left text-sm text-gray-500" colSpan={2}></td>
                  <td className="px-6 py-4 text-left text-sm text-gray-500">
                    {data.currency} {data.line_items.reduce((sum, item) => sum + item.total, 0).toFixed(2)}
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                    Tax
                  </td>
                  <td className="px-6 py-4 text-left text-sm text-gray-500" colSpan={2}></td>
                  <td className="px-6 py-4 text-left text-sm text-gray-500">
                    {data.currency} {data.tax.toFixed(2)}
                  </td>
                </tr>
                <tr className="font-bold">
                  <td className="px-6 py-4 text-left text-sm text-gray-900">
                    Total
                  </td>
                  <td className="px-6 py-4 text-left text-sm text-gray-500" colSpan={2}></td>
                  <td className="px-6 py-4 text-left text-sm text-gray-900">
                    {data.currency} {data.total_amount.toFixed(2)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}