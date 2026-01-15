import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../utils/api';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

const AdminDashboard: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    adminUsers: 0,
    editorUsers: 0,
    reviewerUsers: 0,
    viewerUsers: 0,
    activeUsers: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch current user to verify admin access
      const user = await api.get('/api/auth/me');
      setCurrentUser(user);

      // Fetch all users
      const usersData = await api.get('/api/auth/users?limit=1000');
      setUsers(usersData);

      // Calculate stats
      const stats = {
        totalUsers: usersData.length,
        adminUsers: usersData.filter((u: User) => u.role === 'admin').length,
        editorUsers: usersData.filter((u: User) => u.role === 'editor').length,
        reviewerUsers: usersData.filter((u: User) => u.role === 'reviewer').length,
        viewerUsers: usersData.filter((u: User) => u.role === 'viewer').length,
        activeUsers: usersData.filter((u: User) => u.is_active).length,
      };
      setStats(stats);
    } catch (error: any) {
      console.error('Error fetching admin data:', error);
      if (error.message.includes('permissions')) {
        alert('You do not have admin permissions');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-gray-300">Loading admin dashboard...</div>
      </div>
    );
  }

  if (!currentUser || currentUser.role !== 'admin') {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-red-900 border border-red-700 text-red-100 px-6 py-4 rounded-lg">
          <h2 className="text-xl font-bold mb-2">Access Denied</h2>
          <p>You do not have permission to access the admin dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Admin Dashboard</h1>
        <p className="text-gray-400">Manage users and system settings</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm font-medium mb-2">Total Users</div>
          <div className="text-3xl font-bold text-white">{stats.totalUsers}</div>
          <div className="text-green-400 text-sm mt-2">{stats.activeUsers} active</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm font-medium mb-2">Admins</div>
          <div className="text-3xl font-bold text-primary-400">{stats.adminUsers}</div>
          <div className="text-gray-500 text-sm mt-2">Full access</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm font-medium mb-2">Editors</div>
          <div className="text-3xl font-bold text-blue-400">{stats.editorUsers}</div>
          <div className="text-gray-500 text-sm mt-2">Can create/edit</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm font-medium mb-2">Reviewers</div>
          <div className="text-3xl font-bold text-yellow-400">{stats.reviewerUsers}</div>
          <div className="text-gray-500 text-sm mt-2">Can review queue</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-gray-400 text-sm font-medium mb-2">Viewers</div>
          <div className="text-3xl font-bold text-gray-400">{stats.viewerUsers}</div>
          <div className="text-gray-500 text-sm mt-2">Read-only access</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            to="/admin/users"
            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-md transition-colors font-medium text-center"
          >
            Manage Users
          </Link>
          <button
            onClick={fetchData}
            className="bg-gray-700 hover:bg-gray-600 text-white px-6 py-3 rounded-md transition-colors font-medium"
          >
            Refresh Data
          </button>
        </div>
      </div>

      {/* Recent Users */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mt-8">
        <h2 className="text-xl font-bold text-white mb-4">Recent Users</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-300 font-medium">Username</th>
                <th className="text-left py-3 px-4 text-gray-300 font-medium">Email</th>
                <th className="text-left py-3 px-4 text-gray-300 font-medium">Role</th>
                <th className="text-left py-3 px-4 text-gray-300 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {users.slice(0, 5).map((user) => (
                <tr key={user.id} className="border-b border-gray-700 hover:bg-gray-750">
                  <td className="py-3 px-4 text-white">{user.username}</td>
                  <td className="py-3 px-4 text-gray-300">{user.email}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      user.role === 'admin' ? 'bg-primary-900 text-primary-200' :
                      user.role === 'editor' ? 'bg-blue-900 text-blue-200' :
                      user.role === 'reviewer' ? 'bg-yellow-900 text-yellow-200' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {user.role.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      user.is_active ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'
                    }`}>
                      {user.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 text-center">
          <Link
            to="/admin/users"
            className="text-primary-400 hover:text-primary-300 font-medium"
          >
            View All Users →
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
