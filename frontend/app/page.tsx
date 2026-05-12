'use client';

import { useState } from 'react';
import Uploader from '@/components/Uploader';
import { Button } from '@/components/ui/button';

export default function Home() {
  const [extractionResult, setExtractionResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/v1/extract/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      setExtractionResult(result);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          InvoiceIQ - AI Invoice Extractor
        </h1>

        <div className="bg-white rounded-lg shadow-md p-6">
          <Uploader onUpload={handleUpload} loading={loading} />

          {extractionResult && (
            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-4">Extracted Data</h2>
              <div className="space-y-4">
                <p><strong>Vendor:</strong> {extractionResult.vendor_name}</p>
                <p><strong>Date:</strong> {extractionResult.date}</p>
                <p><strong>Currency:</strong> {extractionResult.currency}</p>
                <p><strong>Tax:</strong> {extractionResult.tax}</p>
                <p><strong>Total Amount:</strong> {extractionResult.total_amount}</p>

                <h3 className="text-lg font-medium mb-2">Line Items:</h3>
                <ul className="list-disc pl-5 space-y-2">
                  {extractionResult.line_items.map((item, index) => (
                    <li key={index}>
                      {item.description} - {item.quantity} × {item.unit_price} = {item.total}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}