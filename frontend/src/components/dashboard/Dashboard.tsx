import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface DashboardStats {
  totalNiches: number;
  activeNiches: number;
  highPotentialNiches: number;
  averageScore: number;
  recentDiscoveries: number;
}

interface HighPotentialNiche {
  id: number;
  name: string;
  overall_score: number;
  category: string;
  discovered_at: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalNiches: 0,
    activeNiches: 0,
    highPotentialNiches: 0,
    averageScore: 0,
    recentDiscoveries: 0
  });
  
  const [highPotentialNiches, setHighPotentialNiches] = useState<HighPotentialNiche[]>([]);
  const [loading, setLoading] = useState(true);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch high-potential niches
      const highPotentialResponse = await axios.get(`${API_BASE}/niches/high-potential/`);
      setHighPotentialNiches(highPotentialResponse.data.niches || []);

      // Fetch all niches for stats calculation
      const nichesResponse = await axios.get(`${API_BASE}/niches/?limit=1000`);
      const niches = nichesResponse.data.niches || [];
      
      // Calculate stats
      const totalNiches = niches.length;
      const activeNiches = niches.filter((n: any) => n.is_active).length;
      const highPotential = niches.filter((n: any) => n.overall_score >= 90).length;
      const averageScore = niches.reduce((sum: number, n: any) => sum + n.overall_score, 0) / totalNiches || 0;
      
      // Recent discoveries (last 24 hours)
      const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
      const recentDiscoveries = niches.filter((n: any) => 
        new Date(n.discovered_at) > oneDayAgo
      ).length;

      setStats({
        totalNiches,
        activeNiches,
        highPotentialNiches: highPotential,
        averageScore: Math.round(averageScore * 100) / 100,
        recentDiscoveries
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600">Overview of your niche discovery engine</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Total Niches</h3>
          <p className="text-3xl font-bold text-gray-900">{stats.totalNiches}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Active Niches</h3>
          <p className="text-3xl font-bold text-green-600">{stats.activeNiches}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">High Potential</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.highPotentialNiches}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Average Score</h3>
          <p className="text-3xl font-bold text-purple-600">{stats.averageScore}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Recent Discoveries</h3>
          <p className="text-3xl font-bold text-orange-600">{stats.recentDiscoveries}</p>
        </div>
      </div>

      {/* High Potential Niches */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">High Potential Niches</h3>
        {highPotentialNiches.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Discovered
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {highPotentialNiches.slice(0, 10).map((niche) => (
                  <tr key={niche.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{niche.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        niche.overall_score >= 95 
                          ? 'bg-green-100 text-green-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {niche.overall_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-500">{niche.category || 'Uncategorized'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(niche.discovered_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No high potential niches found yet.</p>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
            Start Discovery
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors">
            Analyze Niche
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition-colors">
            Export Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;