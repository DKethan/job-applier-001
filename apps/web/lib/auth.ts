interface User {
  id: string;
  email: string;
  username: string;
  display_name: string;
  created_at: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface RegisterData {
  email: string;
  username: string;
  display_name: string;
  password: string;
}

interface LoginData {
  email: string;
  password: string;
}

class AuthClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  async register(data: RegisterData): Promise<User> {
    const response = await fetch(`${this.baseUrl}/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      let message = 'Registration failed';
      try {
        const error = await response.json();
        if (typeof error?.detail === 'string') {
          message = error.detail;
        } else if (Array.isArray(error?.detail) && error.detail.length > 0) {
          // FastAPI / Pydantic validation errors
          message = error.detail.map((e: any) => e.msg || e.detail || '').join(', ');
        }
      } catch {
        // ignore JSON parse errors
      }
      throw new Error(message);
    }

    return response.json();
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: data.email,
        password: data.password,
      }),
    });

    if (!response.ok) {
      let message = 'Login failed';
      try {
        const error = await response.json();
        // Prefer simple messages
        if (typeof error?.detail === 'string') {
          message = error.detail;
        } else if (Array.isArray(error?.detail) && error.detail.length > 0) {
          message = error.detail[0].msg || 'Invalid input';
        }
      } catch {
        // ignore JSON parse errors
      }
      if (response.status === 400 || response.status === 401) {
        message = 'Invalid email or password';
      }
      throw new Error(message);
    }

    return response.json();
  }

  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('No auth token');
    }

    const response = await fetch(`${this.baseUrl}/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('auth_token');
        throw new Error('Session expired');
      }
      throw new Error('Failed to get user info');
    }

    return response.json();
  }

  setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  getToken(): string | null {
    if (typeof window === 'undefined') {
      return null; // Server-side
    }
    return localStorage.getItem('auth_token');
  }

  clearToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authClient = new AuthClient();
export type { User, RegisterData, LoginData, AuthResponse };