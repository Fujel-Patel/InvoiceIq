'use client';

import { useState } from 'react';

interface UploaderProps {
  onUpload: (file: File) => Promise<void>;
  loading?: boolean;
}

export default function Uploader({ onUpload, loading = false }: UploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleUpload = async () => {
    if (!file) return;
    await onUpload(file);
  };

  const acceptTypes = ['image/jpeg', 'image/png', 'application/pdf'];

  return (
    <div className="border-2 border-dashed rounded-lg p-8 text-center transition-colors hover:border-gray-300">
      {dragOver && <div className="bg-blue-50"></div>}

      <div className="relative z-10">
        <input
          type="file"
          accept={acceptTypes.join(',')}
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="cursor-pointer">
          {file ? (
            <div className="mb-4">
              <p className="text-sm text-gray-600">Selected file:</p>
              <p className="font-medium">{file.name}</p>
            </div>
          ) : (
            <>
              <div className="mb-4">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16h4v2m0 0l-4-4m4 4l4-4m0 6H9a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <p className="text-sm text-gray-600">Click to upload or drag and drop</p>
              <p className="text-xs text-gray-500 mt-1">
                Supported formats: JPG, PNG, PDF
              </p>
            </>
          )}

          <button
            onClick={() => document.querySelector('input[type="file"]')?.click()}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
            disabled={loading || !file}
          >
            {loading ? 'Uploading...' : 'Upload and Extract'}
          </button>
        </div>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="absolute inset-0 pointer-events-none"
      />
    </div>
  );
}