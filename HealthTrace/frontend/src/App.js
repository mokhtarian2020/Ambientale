import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Components
import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import Dashboard from './components/Dashboard/Dashboard';
import PatientManagement from './components/Patients/PatientManagement';
import DiseaseReporting from './components/Diseases/DiseaseReporting';
import EpidemiologicalInvestigation from './components/Investigations/EpidemiologicalInvestigation';
import EnvironmentalData from './components/Environmental/EnvironmentalData';
import Analytics from './components/Analytics/Analytics';
import GeoVisualization from './components/GeoVisualization/GeoVisualization';

// Context
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Main App component
function AppContent() {
  const { user } = useAuth();
  
  return (
    <Router>
      <Routes>
        <Route path="/login" element={!user ? <Login /> : <Navigate to="/" replace />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          {/* Dashboard Routes */}
          <Route index element={<Dashboard />} />
          
          {/* Patient Management (CU06, CU07, CU08) */}
          <Route path="patients" element={<PatientManagement />} />
          
          {/* Disease Reporting (CU05, CU09) */}
          <Route path="diseases" element={<DiseaseReporting />} />
          
          {/* Epidemiological Investigations (CU10-CU17) */}
          <Route path="investigations" element={<EpidemiologicalInvestigation />} />
          
          {/* Environmental Data */}
          <Route path="environmental" element={<EnvironmentalData />} />
          
          {/* Analytics (Correlation Analysis, ML Models) */}
          <Route path="analytics" element={<Analytics />} />
          
          {/* Geo Visualization (CU19) */}
          <Route path="geo-view" element={<GeoVisualization />} />
        </Route>
        
        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <AppContent />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
