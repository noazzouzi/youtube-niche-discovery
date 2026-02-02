import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Button,
  Tooltip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MonetizationOnIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

interface DashboardStats {
  summary: {
    total_niches: number;
    high_potential: number;
    medium_potential: number;
    recent_discoveries_24h: number;
    average_score: number;
  };
  performance_metrics: {
    high_potential_rate: number;
    discovery_target_progress: string;
    algorithm_effectiveness: number;
  };
  category_distribution: Array<{
    category: string;
    count: number;
  }>;
  generated_at: string;
}

interface HighPotentialNiche {
  id: number;
  name: string;
  score: number;
  category: string;
  discovered_at: string;
  last_updated: string;
  score_breakdown: {
    overall: number;
    trend: number;
    competition: number;
    monetization: number;
    audience: number;
    content_opportunity: number;
  };
}

interface DiscoveryStatus {
  today_stats: {
    total_discovered: number;
    high_potential: number;
    target_progress: string;
  };
  latest_discoveries: Array<{
    name: string;
    score: number;
    category: string;
    discovered_at: string;
  }>;
}

const NicheDiscoveryDashboard: React.FC = () => {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [highPotentialNiches, setHighPotentialNiches] = useState<HighPotentialNiche[]>([]);
  const [discoveryStatus, setDiscoveryStatus] = useState<DiscoveryStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [discoveryRunning, setDiscoveryRunning] = useState(false);

  // Fetch dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      const [statsResponse, nichesResponse, statusResponse] = await Promise.all([
        fetch('/api/v1/niches/dashboard/stats'),
        fetch('/api/v1/niches/high-potential/?limit=20'),
        fetch('/api/v1/niches/discover/status')
      ]);

      if (statsResponse.ok) {
        const stats = await statsResponse.json();
        setDashboardStats(stats);
      }

      if (nichesResponse.ok) {
        const niches = await nichesResponse.json();
        setHighPotentialNiches(niches);
      }

      if (statusResponse.ok) {
        const status = await statusResponse.json();
        setDiscoveryStatus(status);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Auto-refresh data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const startDailyDiscovery = async () => {
    setDiscoveryRunning(true);
    try {
      const response = await fetch('/api/v1/niches/discover/daily', {
        method: 'POST'
      });
      if (response.ok) {
        // Refresh data after starting discovery
        setTimeout(fetchDashboardData, 2000);
      }
    } catch (error) {
      console.error('Error starting discovery:', error);
    } finally {
      setDiscoveryRunning(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    if (score >= 50) return 'info';
    return 'error';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 90) return 'HIGH POTENTIAL';
    if (score >= 70) return 'GOOD';
    if (score >= 50) return 'MODERATE';
    return 'LOW';
  };

  // Chart data for score distribution
  const chartData = {
    labels: ['Search Volume', 'Competition', 'Monetization', 'Content', 'Trends'],
    datasets: highPotentialNiches.slice(0, 3).map((niche, index) => ({
      label: niche.name,
      data: [
        (niche.score_breakdown.trend / 15) * 100, // Normalize to percentage
        (niche.score_breakdown.competition / 25) * 100,
        (niche.score_breakdown.monetization / 20) * 100,
        (niche.score_breakdown.content_opportunity / 15) * 100,
        (niche.score_breakdown.trend / 15) * 100,
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 205, 86, 1)'
      ][index],
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(255, 205, 86, 0.2)'
      ][index],
      fill: true,
    }))
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          🚀 YouTube Niche Discovery Engine
        </Typography>
        <Box>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              {refreshing ? <CircularProgress size={24} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            color="primary"
            onClick={startDailyDiscovery}
            disabled={discoveryRunning}
            startIcon={discoveryRunning ? <CircularProgress size={20} /> : <TrendingUpIcon />}
            sx={{ ml: 1 }}
          >
            {discoveryRunning ? 'Discovering...' : 'Start Discovery'}
          </Button>
        </Box>
      </Box>

      {/* Real-time Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)' }}>
            <CardContent>
              <Typography color="white" gutterBottom>
                Total Niches Discovered
              </Typography>
              <Typography variant="h4" component="div" color="white">
                {dashboardStats?.summary.total_niches || 0}
              </Typography>
              <Typography variant="body2" color="white" opacity={0.8}>
                Active and validated niches
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)' }}>
            <CardContent>
              <Typography color="white" gutterBottom>
                High Potential (90+)
              </Typography>
              <Typography variant="h4" component="div" color="white">
                {dashboardStats?.summary.high_potential || 0}
              </Typography>
              <Typography variant="body2" color="white" opacity={0.8}>
                Immediate action recommended
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(45deg, #FF9800 30%, #FFD54F 90%)' }}>
            <CardContent>
              <Typography color="white" gutterBottom>
                Today's Progress
              </Typography>
              <Typography variant="h4" component="div" color="white">
                {discoveryStatus?.today_stats.target_progress || '0/100'}
              </Typography>
              <Typography variant="body2" color="white" opacity={0.8}>
                Daily discovery target
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(45deg, #4CAF50 30%, #8BC34A 90%)' }}>
            <CardContent>
              <Typography color="white" gutterBottom>
                Avg. Algorithm Score
              </Typography>
              <Typography variant="h4" component="div" color="white">
                {dashboardStats?.summary.average_score?.toFixed(1) || '0.0'}
              </Typography>
              <Typography variant="body2" color="white" opacity={0.8}>
                PM Agent 100-point algorithm
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alert for high-potential discoveries */}
      {(dashboardStats?.summary.high_potential || 0) > 0 && (
        <Alert severity="success" sx={{ mb: 3 }}>
          🎯 <strong>{dashboardStats?.summary.high_potential} high-potential niches</strong> discovered! 
          These are scoring 90+ points and ready for immediate content creation.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* High-Potential Niches Table */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🏆 High-Potential Niches (90+ Score)
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Niche Name</TableCell>
                      <TableCell align="center">PM Score</TableCell>
                      <TableCell align="center">Category</TableCell>
                      <TableCell align="center">Trend</TableCell>
                      <TableCell align="center">Competition</TableCell>
                      <TableCell align="center">Monetization</TableCell>
                      <TableCell align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {highPotentialNiches.map((niche) => (
                      <TableRow key={niche.id} hover>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {niche.name}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              Discovered: {new Date(niche.discovered_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={`${niche.score.toFixed(1)}`}
                            color={getScoreColor(niche.score)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Chip label={niche.category} variant="outlined" size="small" />
                        </TableCell>
                        <TableCell align="center">
                          <LinearProgress
                            variant="determinate"
                            value={(niche.score_breakdown.trend / 15) * 100}
                            sx={{ width: 60 }}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <LinearProgress
                            variant="determinate"
                            value={(niche.score_breakdown.competition / 25) * 100}
                            sx={{ width: 60 }}
                            color="secondary"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <LinearProgress
                            variant="determinate"
                            value={(niche.score_breakdown.monetization / 20) * 100}
                            sx={{ width: 60 }}
                            color="warning"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => window.open(`/niches/${niche.id}`, '_blank')}
                          >
                            Analyze
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              {highPotentialNiches.length === 0 && (
                <Box textAlign="center" py={4}>
                  <Typography color="textSecondary">
                    No high-potential niches discovered yet. Start the daily discovery to find opportunities!
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics & Latest Discoveries */}
        <Grid item xs={12} lg={4}>
          {/* PM Algorithm Performance */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 PM Algorithm Performance
              </Typography>
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  High-Potential Rate
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={dashboardStats?.performance_metrics.high_potential_rate || 0}
                  sx={{ mt: 1, mb: 1 }}
                />
                <Typography variant="caption">
                  {dashboardStats?.performance_metrics.high_potential_rate?.toFixed(1) || 0}%
                </Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Algorithm Effectiveness
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={dashboardStats?.performance_metrics.algorithm_effectiveness || 0}
                  color="secondary"
                  sx={{ mt: 1, mb: 1 }}
                />
                <Typography variant="caption">
                  {dashboardStats?.performance_metrics.algorithm_effectiveness?.toFixed(1) || 0}/100
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="textSecondary">
                  Daily Discovery Progress
                </Typography>
                <Typography variant="h6" color="primary">
                  {dashboardStats?.performance_metrics.discovery_target_progress || '0/100'}
                </Typography>
                <Typography variant="caption">
                  Target: 100+ niches daily
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Latest Discoveries */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🕐 Latest Discoveries
              </Typography>
              {discoveryStatus?.latest_discoveries.slice(0, 5).map((discovery, index) => (
                <Box key={index} mb={1.5}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" fontWeight="bold">
                      {discovery.name}
                    </Typography>
                    <Chip
                      label={discovery.score.toFixed(1)}
                      size="small"
                      color={getScoreColor(discovery.score)}
                    />
                  </Box>
                  <Typography variant="caption" color="textSecondary">
                    {discovery.category} • {new Date(discovery.discovered_at).toLocaleTimeString()}
                  </Typography>
                </Box>
              )) || (
                <Typography color="textSecondary" variant="body2">
                  No recent discoveries yet.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Score Distribution Chart */}
        {highPotentialNiches.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📈 Top 3 Niches - PM Score Breakdown
                </Typography>
                <Box height={300}>
                  <Line
                    data={chartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top' as const,
                        },
                        title: {
                          display: true,
                          text: 'PM Agent 100-Point Scoring Algorithm Breakdown',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100,
                          title: {
                            display: true,
                            text: 'Score Percentage'
                          }
                        },
                      },
                    }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Category Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📂 Category Distribution
              </Typography>
              {dashboardStats?.category_distribution.slice(0, 8).map((cat, index) => (
                <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                    {cat.category}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LinearProgress
                      variant="determinate"
                      value={(cat.count / (dashboardStats?.summary.total_niches || 1)) * 100}
                      sx={{ width: 100 }}
                    />
                    <Typography variant="caption">
                      {cat.count}
                    </Typography>
                  </Box>
                </Box>
              )) || (
                <Typography color="textSecondary">
                  No categories available yet.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ⚙️ System Status
              </Typography>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">PM Algorithm</Typography>
                  <Chip label="ACTIVE" color="success" size="small" />
                </Box>
              </Box>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">YouTube Data API</Typography>
                  <Chip label="CONNECTED" color="success" size="small" />
                </Box>
              </Box>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Discovery Engine</Typography>
                  <Chip
                    label={discoveryRunning ? "RUNNING" : "READY"}
                    color={discoveryRunning ? "warning" : "success"}
                    size="small"
                  />
                </Box>
              </Box>
              <Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Last Update</Typography>
                  <Typography variant="caption">
                    {dashboardStats?.generated_at
                      ? new Date(dashboardStats.generated_at).toLocaleTimeString()
                      : 'N/A'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NicheDiscoveryDashboard;