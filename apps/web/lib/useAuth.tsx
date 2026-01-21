'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authClient, User } from './auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, displayName: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    // Check if user is already authenticated on mount
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      if (authClient.isAuthenticated()) {
        const userData = await authClient.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      // Token is invalid, clear it
      authClient.clearToken();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await authClient.login({ email, password });
      authClient.setToken(response.access_token);
      const userData = await authClient.getCurrentUser();
      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, username: string, displayName: string, password: string) => {
    try {
      await authClient.register({ email, username, display_name: displayName, password });
      // After registration, automatically log in
      await login(email, password);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authClient.clearToken();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}