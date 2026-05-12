'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function HistoryPage() {
  const [history, setHistory] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch extraction history from backend
    fetch('/api/v1/history/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch history');
        }
        return response.json();
      })
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('History fetch error:', err);
        setError('Failed to load history. Please try again later.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 flex items-center justify-center">
        <div className="animate-spin rounded-full border-4 border-b-2 border-blue-500 w-12 h-12"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold">Extraction History</h1>
          <p className="text-gray-600 mt-2">
            View your past invoice extractions.
          </p>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No extractions found. Upload an invoice to get started.</p>
            <Button
              asChild
              href="/"
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Upload Invoice
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {history.map((item, index) => (
              <div key={item.id || index} className="bg-white rounded-lg shadow-md p-4 border">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{item.vendor_name}</h3>
                    <p className="text-sm text-gray-500">
                      {new Date(item.date).toLocaleDateString()} •
                      {item.currency} {item.total_amount.toFixed(2)}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      // In a real app, we would navigate to a detail view
                      alert(`View details for extraction #${item.id}`);
                    }}
                  >
                    View
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}