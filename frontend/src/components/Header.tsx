import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getCurrentUser } from '../utils/api';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
}

const Header = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    // Check if user has a token in localStorage
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);

    // Fetch current user info if authenticated
    if (token) {
      fetchCurrentUser();
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
    }
  };

  const handleLogout = () => {
    // Remove tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
    setCurrentUser(null);
    navigate('/login');
  };

  return (
    <header className="bg-primary-700 text-white shadow-lg">
      <nav className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold">GADB</div>
            <div className="hidden md:block text-sm text-primary-100">
              Government Accountability Database
            </div>
          </Link>

          <div className="flex items-center space-x-6">
            <Link
              to="/incidents"
              className="hover:text-primary-100 transition-colors font-medium"
            >
              Incidents
            </Link>
            <Link
              to="/analytics"
              className="hover:text-primary-100 transition-colors font-medium"
            >
              Analytics
            </Link>
            {isAuthenticated && currentUser && ['reviewer', 'editor', 'admin'].includes(currentUser.role) && (
              <Link
                to="/ingestion"
                className="hover:text-primary-100 transition-colors font-medium"
              >
                Ingestion Queue
              </Link>
            )}
            {isAuthenticated && currentUser?.role === 'admin' && (
              <Link
                to="/admin"
                className="hover:text-primary-100 transition-colors font-medium"
              >
                Admin
              </Link>
            )}
            <Link
              to="/about"
              className="hover:text-primary-100 transition-colors font-medium"
            >
              About
            </Link>

            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <span className="text-sm text-primary-200">
                  {currentUser?.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-primary-800 hover:bg-primary-900 px-4 py-2 rounded-md transition-colors font-medium"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="bg-primary-800 hover:bg-primary-900 px-4 py-2 rounded-md transition-colors font-medium"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
