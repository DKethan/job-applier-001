'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../lib/useAuth';
import { apiClient } from '../../lib/api';
import Link from 'next/link';

interface ProfileStatus {
  hasProfile: boolean;
  profileId?: string;
  profileCompleteness: {
    education: boolean;
    experience: boolean;
    skills: boolean;
    projects: boolean;
    publications: boolean;
  };
  profile?: any;
}

export default function DashboardPage() {
  const [profileStatus, setProfileStatus] = useState<ProfileStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    loadProfileStatus();
  }, [isAuthenticated, router]);

  const loadProfileStatus = async () => {
    try {
      setLoading(true);
      const status = await apiClient.get('/v1/profile/me');
      setProfileStatus(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile status');
    } finally {
      setLoading(false);
    }
  };

  const handleJobUrlSubmit = async (jobUrl: string) => {
    try {
      setLoading(true);

      // Ingest job
      const ingestResult = await apiClient.post('/v1/jobs/ingest', { url: jobUrl });

      // Tailor resume
      await apiClient.post('/v1/tailor', {
        job_id: ingestResult.job_posting.id,
        profile_id: profileStatus?.profileId,
      });

      // Navigate to results
      router.push(`/job?jobUrl=${encodeURIComponent(jobUrl)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process job');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">

      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900">Welcome to JobCopilot</h1>
          <p className="mt-2 text-lg text-gray-600">
            Let's get you started with applying to jobs
          </p>
        </div>

        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {!profileStatus?.hasProfile ? (
          <ResumeUploadCard onUpload={loadProfileStatus} />
        ) : (
          <JobUrlInputCard
            onSubmit={handleJobUrlSubmit}
            initialUrl={searchParams.get('jobUrl') || ''}
            loading={loading}
          />
        )}
      </div>
    </div>
  );
}

function ResumeUploadCard({ onUpload }: { onUpload: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      await apiClient.uploadFile('/v1/profile/resume/upload', file);
      // Redirect to profile review page instead of just reloading status
      router.push('/profile/review');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="text-center mb-8">
        <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Resume</h2>
        <p className="text-gray-600">
          Let's start by uploading your resume. We'll parse it and create your profile.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resume File
          </label>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
            required
          />
          <p className="mt-1 text-sm text-gray-500">
            PDF or DOCX format. We'll extract your experience, education, and skills.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || uploading}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium
            hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
            transition-colors"
        >
          {uploading ? 'Uploading...' : 'Upload Resume'}
        </button>
      </form>
    </div>
  );
}

function JobUrlInputCard({
  onSubmit,
  initialUrl,
  loading
}: {
  onSubmit: (url: string) => void;
  initialUrl: string;
  loading: boolean;
}) {
  const [jobUrl, setJobUrl] = useState(initialUrl);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobUrl.trim()) {
      setError('Please enter a job URL');
      return;
    }
    setError('');
    onSubmit(jobUrl);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="text-center mb-8">
        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m8 0V8a2 2 0 01-2 2H8a2 2 0 01-2-2V6m8 0H8" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Ready to Apply!</h2>
        <p className="text-gray-600">
          Your profile is set up. Paste a job posting URL and we'll tailor your resume.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Posting URL
          </label>
          <input
            type="url"
            value={jobUrl}
            onChange={(e) => setJobUrl(e.target.value)}
            placeholder="https://..."
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
          <p className="mt-1 text-sm text-gray-500">
            Paste the URL of the job posting you want to apply for.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-md font-medium
            hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed
            transition-colors"
        >
          {loading ? 'Processing...' : 'Analyze & Tailor Resume'}
        </button>
      </form>
    </div>
  );
}