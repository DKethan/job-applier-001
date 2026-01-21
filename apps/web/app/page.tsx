'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../lib/useAuth';
import { apiClient } from '../lib/api';
import Landing from './components/Landing';

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
}

export default function Home() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [profileStatus, setProfileStatus] = useState<ProfileStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkUserStatus = async () => {
      if (authLoading) return;

      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        const status = await apiClient.get('/v1/profile/me');
        setProfileStatus(status);
      } catch (error) {
        console.error('Failed to check profile status:', error);
      } finally {
        setLoading(false);
      }
    };

    checkUserStatus();
  }, [isAuthenticated, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  // Anonymous users: show marketing landing page without job URL input
  if (!isAuthenticated) {
    return <MarketingLanding />;
  }

  // Authenticated users without complete profile: redirect to dashboard
  if (!profileStatus?.hasProfile) {
    router.push('/dashboard');
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  // Authenticated users with complete profile: show full landing page with job URL input
  return <Landing />;
}

function MarketingLanding() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="relative z-10 flex items-center justify-center min-h-screen px-4">
        <div className="max-w-4xl w-full text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            Applying is easier
          </h1>
          <p className="text-xl md:text-2xl text-white/90 mb-12">
            Paste a job link, we'll extract the JD, tailor your resume, and autofill forms.
          </p>

          <div className="space-y-8">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-8">
              <h2 className="text-2xl font-semibold text-white mb-4">How It Works</h2>
              <div className="grid md:grid-cols-3 gap-6 text-left">
                <div className="text-center">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">1️⃣</span>
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Upload Resume</h3>
                  <p className="text-white/80">Parse and analyze your resume with AI</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">2️⃣</span>
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Paste Job URL</h3>
                  <p className="text-white/80">Extract job details automatically</p>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">3️⃣</span>
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Get Tailored Resume</h3>
                  <p className="text-white/80">Download customized applications</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <a
                href="/login"
                className="inline-block bg-white text-purple-900 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white/90 transition-colors"
              >
                Get Started - Sign In
              </a>
              <p className="text-white/60 text-sm">
                Already have an account? <a href="/login" className="underline">Sign in here</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
