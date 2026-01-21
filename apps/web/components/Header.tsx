'use client';

import { useAuth } from '../lib/useAuth';
import { usePathname } from 'next/navigation';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Header() {
  const { user, isAuthenticated } = useAuth();
  const appName = process.env.NEXT_PUBLIC_APP_NAME || 'JobCopilot';
  const pathname = usePathname();
  const router = useRouter();

  const handleLogoClick = () => {
    if (isAuthenticated) {
      // If authenticated, go to dashboard (will show appropriate content based on profile status)
      router.push('/dashboard');
    } else {
      // If not authenticated, go to home/landing page
      router.push('/');
    }
  };

  // Don't show header on login page
  if (pathname === '/login') {
    return null;
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand */}
          <div className="flex items-center">
            <h1
              className="text-xl font-bold text-gray-900 cursor-pointer hover:text-blue-600 transition-colors"
              onClick={handleLogoClick}
            >
              {appName}
            </h1>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link
              href="/profile"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
            >
              Account Settings
            </Link>
            <Link
              href="/upload"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
            >
              Upload New Resume
            </Link>
            <Link
              href="/profile/review"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium"
            >
              Edit Existing Resume
            </Link>
          </nav>

          {/* Auth Section */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <span className="text-sm text-gray-700">
                Welcome, {user?.display_name || user?.username || 'User'}
              </span>
            ) : (
              <a
                href="/login"
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Login
              </a>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}