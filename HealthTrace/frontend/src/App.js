import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import './index.css';

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

// Create theme — HealthTrace design system (D.4 §1.1)
const theme = createTheme({
  palette: {
    primary: {
      main: '#0F3157',       // Blu Notte — Brand / Navbar
      dark: '#0a2240',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#123B67',       // Voce sottomenu / accento
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#28A745',       // Inserimento, conferma, creazione
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FFC107',       // Modifica, revoca, attenzione
      contrastText: '#212121',
    },
    error: {
      main: '#DC3545',       // Eliminazione, pericolo
      contrastText: '#FFFFFF',
    },
    info: {
      main: '#16A3B7',       // Ricerca, avvio processi, sola lettura
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#212121',
      secondary: '#616161',  // --v-text-form
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      "'Segoe UI'",
      'Roboto',
      "'Helvetica Neue'",
      'Arial',
      "'Noto Sans'",
      'sans-serif',
    ].join(','),
    body1: { lineHeight: 1.4 },
    body2: { lineHeight: 1.4 },
  },
  shape: {
    borderRadius: 4,         // border-radius uniforme bottoni
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#0F3157',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          color: '#0E3964',  // --v-text-table
          lineHeight: 1.4,
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#616161',  // --v-text-form
        },
      },
    },
    MuiFormHelperText: {
      styleOverrides: {
        root: {
          color: '#616161',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            backgroundColor: '#EDEDED',
            color: '#123B67',
            '&:hover': {
              backgroundColor: '#E0E0E0',
            },
          },
        },
      },
    },
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
