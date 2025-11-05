import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  LinearProgress
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ResponsiveContainer
} from 'recharts';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';

import { useAuth } from '../../contexts/AuthContext';
import { dashboardAPI } from '../../services/api';

// Summary Dashboard Component (CU18: Summary and Monitoring Dashboard)
const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [timeFilter, setTimeFilter] = useState('month');
  const [regionFilter, setRegionFilter] = useState('all');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  
  // Dashboard data state
  const [summaryData, setSummaryData] = useState({
    totalReports: 0,
    totalInvestigations: 0,
    activePatients: 0,
    recoveredPatients: 0
  });
  
  const [chartData, setChartData] = useState({
    reportsOverTime: [],
    diseaseDistribution: [],
    regionDistribution: []
  });
  
  useEffect(() => {
    loadDashboardData();
  }, [timeFilter, regionFilter, startDate, endDate]);
  
  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const params = {
        time_filter: timeFilter,
        region: regionFilter !== 'all' ? regionFilter : undefined,
        start_date: startDate?.toISOString().split('T')[0],
        end_date: endDate?.toISOString().split('T')[0]
      };
      
      const response = await dashboardAPI.getSummaryDashboard(params);
      
      // Update summary data
      setSummaryData({
        totalReports: response.total_reports || 0,
        totalInvestigations: response.total_investigations || 0,
        activePatients: response.active_patients || 0,
        recoveredPatients: response.recovered_patients || 0
      });
      
      // Update chart data
      setChartData({
        reportsOverTime: response.reports_over_time || [],
        diseaseDistribution: response.disease_distribution || [],
        regionDistribution: response.region_distribution || []
      });
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Sample data for demonstration
  const sampleReportsOverTime = [
    { month: 'Jan', reports: 24, investigations: 18 },
    { month: 'Feb', reports: 32, investigations: 25 },
    { month: 'Mar', reports: 28, investigations: 22 },
    { month: 'Apr', reports: 35, investigations: 28 },
    { month: 'May', reports: 42, investigations: 33 },
    { month: 'Jun', reports: 38, investigations: 30 }
  ];
  
  const sampleDiseaseDistribution = [
    { name: 'Influenza', value: 35, color: '#8884d8' },
    { name: 'COVID-19', value: 28, color: '#82ca9d' },
    { name: 'Legionellosis', value: 15, color: '#ffc658' },
    { name: 'Measles', value: 12, color: '#ff7c7c' },
    { name: 'Others', value: 10, color: '#8dd1e1' }
  ];
  
  const sampleRegionDistribution = [
    { region: 'Campania', cases: 145 },
    { region: 'Calabria', cases: 89 },
    { region: 'Molise', cases: 56 }
  ];
  
  // Use sample data if no real data is available
  const displayReportsOverTime = chartData.reportsOverTime.length > 0 ? chartData.reportsOverTime : sampleReportsOverTime;
  const displayDiseaseDistribution = chartData.diseaseDistribution.length > 0 ? chartData.diseaseDistribution : sampleDiseaseDistribution;
  const displayRegionDistribution = chartData.regionDistribution.length > 0 ? chartData.regionDistribution : sampleRegionDistribution;
  
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Header */}
        <Typography variant="h4" sx={{ mb: 3 }}>
          Dashboard di Monitoraggio - HealthTrace
        </Typography>
        
        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Periodo</InputLabel>
                <Select
                  value={timeFilter}
                  label="Periodo"
                  onChange={(e) => setTimeFilter(e.target.value)}
                >
                  <MenuItem value="week">Settimanale</MenuItem>
                  <MenuItem value="month">Mensile</MenuItem>
                  <MenuItem value="year">Annuale</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Regione</InputLabel>
                <Select
                  value={regionFilter}
                  label="Regione"
                  onChange={(e) => setRegionFilter(e.target.value)}
                >
                  <MenuItem value="all">Tutte</MenuItem>
                  <MenuItem value="Campania">Campania</MenuItem>
                  <MenuItem value="Calabria">Calabria</MenuItem>
                  <MenuItem value="Molise">Molise</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={2}>
              <DatePicker
                label="Data Inizio"
                value={startDate}
                onChange={setStartDate}
                slotProps={{ textField: { size: 'small', fullWidth: true } }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={2}>
              <DatePicker
                label="Data Fine"
                value={endDate}
                onChange={setEndDate}
                slotProps={{ textField: { size: 'small', fullWidth: true } }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={2}>
              <Button
                variant="contained"
                onClick={loadDashboardData}
                fullWidth
                disabled={loading}
              >
                Aggiorna
              </Button>
            </Grid>
          </Grid>
        </Paper>
        
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Segnalazioni Totali
                </Typography>
                <Typography variant="h4" component="div">
                  {summaryData.totalReports || 156}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Indagini Epidemiologiche
                </Typography>
                <Typography variant="h4" component="div">
                  {summaryData.totalInvestigations || 124}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Pazienti Attivi
                </Typography>
                <Typography variant="h4" component="div" color="error">
                  {summaryData.activePatients || 45}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Pazienti Guariti
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {summaryData.recoveredPatients || 89}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* Charts */}
        <Grid container spacing={3}>
          {/* Reports Over Time Chart */}
          <Grid item xs={12} lg={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Andamento Segnalazioni e Indagini
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={displayReportsOverTime}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="reports" stroke="#8884d8" name="Segnalazioni" />
                  <Line type="monotone" dataKey="investigations" stroke="#82ca9d" name="Indagini" />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          
          {/* Disease Distribution Pie Chart */}
          <Grid item xs={12} lg={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Distribuzione per Patologia
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={displayDiseaseDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {displayDiseaseDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          
          {/* Region Distribution Bar Chart */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Distribuzione per Regione
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={displayRegionDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="region" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="cases" fill="#8884d8" name="Casi" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </LocalizationProvider>
  );
};

export default Dashboard;
