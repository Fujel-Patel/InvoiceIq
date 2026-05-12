'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DataTable from '@/components/DataTable';
import ExportButtons from '@/components/ExportButtons';
import { Button } from '@/components/ui/button';

export default function ResultPage() {
  const router = useRouter();
  const [extractionData, setExtractionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // In a real app, we'd get this from URL params or state management
  // For now, we'll simulate getting data from localStorage or context
  useEffect(() => {
    // Simulate fetching extraction result
    const storedResult = localStorage.getItem('lastExtraction');
    if (storedResult) {
      setExtractionData(JSON.parse(storedResult));
      setLoading(false);
    } else {
      // If no data, redirect to home
      router.push('/');
    }
  }, [router]);

  const handleSave = async () => {
    if (!extractionData) return;

    setLoading(true);
    try {
      // Save to backend
      const response = await fetch('/api/v1/history/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(extractionData),
      });

      if (!response.ok) {
        throw new Error('Failed to save extraction');
      }

      alert('Extraction saved successfully!');
    } catch (err) {
      console.error('Save error:', err);
      setError('Failed to save extraction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 py-12 flex items-center justify-center">
      <div className="animate-spin rounded-full border-4 border-b-2 border-blue-500 w-12 h-12"></div>
    </div>;
  }

  if (!extractionData) {
    return <div className="min-h-screen bg-gray-50 py-12 flex items-center justify-center">
      <p className="text-red-500">No extraction data found. Please upload an invoice first.</p>
    </div>;
  }

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <Button variant="outline" onClick={() => router.push('/')}>
            ← Back to Upload
          </Button>
          <h1 className="text-2xl font-semibold mt-4">Extracted Invoice Data</h1>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-500">{error}</div>}

          <DataTable data={extractionData} />

          <div className="mt-6">
            <Button onClick={handleSave} loading={loading}>
              Save to History
            </Button>
            <ExportButtons data={extractionData} />
          </div>
        </div>
      </div>
    </main>
  );
}