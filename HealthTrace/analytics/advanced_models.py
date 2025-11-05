"""
Advanced Analytics Models for HealthTrace 3-Disease Project
Implements the specific models mentioned in Italian specifications:

1. Multiple Linear Regression: Y = β₀ + β₁×PM2.5 + β₂×O₃ + β₃×Rainy_Days + ε
2. GAM/GLM (Generalized Additive/Linear Models)
3. ARIMAX (ARIMA with exogenous variables)
4. DLNM (Distributed Lag Non-Linear Models)
5. Random Forest / XGBoost
6. Spatial Models (Moran's I, Getis-Ord)

Target Diseases: Influenza, Legionellosis, Hepatitis A
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

# Statistical and ML libraries
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb

# Time series analysis
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from statsmodels.regression.linear_model import OLS

# GAM models
from pygam import LinearGAM, s, f

# Spatial analysis
import geopandas as gpd
from libpysal import weights
from esda.moran import Moran, Moran_Local
from esda.getisord import G_Local

# DLNM approximation (simplified implementation)
from scipy.interpolate import interp1d
from scipy.optimize import minimize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelResults:
    """Standard results container for all models"""
    model_type: str
    disease: str
    r_squared: float
    mae: float
    rmse: float
    coefficients: Dict[str, float]
    p_values: Dict[str, float]
    predictions: np.ndarray
    feature_importance: Optional[Dict[str, float]] = None
    spatial_stats: Optional[Dict[str, float]] = None


class MultipleLinearRegressionAdvanced:
    """
    Implementation of the exact model from Italian specifications:
    Y = β₀ + β₁×PM2.5 + β₂×O₃ + β₃×Rainy_Days + ε
    
    Extended with additional environmental factors for the 3 target diseases.
    """
    
    def __init__(self, disease_type: str = "influenza"):
        self.disease_type = disease_type
        self.model = None
        self.feature_names = []
        self.is_fitted = False
        
    def prepare_features(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features based on disease type"""
        
        if self.disease_type == "influenza":
            # Influenza: Focus on air quality and meteorological factors
            features = ['pm25', 'pm10', 'ozone', 'no2', 'temperature_avg', 'humidity', 'rainy_days']
            
        elif self.disease_type == "legionellosis":
            # Legionellosis: Focus on water-related and temperature factors
            features = ['temperature_avg', 'humidity', 'precipitation', 'pm25', 'water_temperature']
            
        elif self.disease_type == "hepatitis_a":
            # Hepatitis A: Focus on precipitation and water quality
            features = ['precipitation', 'rainy_days', 'extreme_precipitation', 'water_ph', 'ecoli_count', 'temperature_avg']
        
        else:
            # Default: All available features
            features = ['pm25', 'ozone', 'rainy_days', 'temperature_avg', 'humidity', 'precipitation']
        
        # Filter available features
        available_features = [f for f in features if f in data.columns]
        
        if not available_features:
            raise ValueError(f"No features available for {self.disease_type}")
        
        X = data[available_features].copy()
        y = data['case_count'] if 'case_count' in data.columns else data['cases']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        self.feature_names = available_features
        return X, y
    
    def fit(self, data: pd.DataFrame) -> ModelResults:
        """Fit the multiple linear regression model"""
        
        X, y = self.prepare_features(data)
        
        # Add constant term for intercept
        X_with_const = sm.add_constant(X)
        
        # Fit OLS model
        self.model = OLS(y, X_with_const).fit()
        self.is_fitted = True
        
        # Calculate predictions
        predictions = self.model.predict(X_with_const)
        
        # Extract results
        coefficients = dict(zip(['intercept'] + self.feature_names, self.model.params))
        p_values = dict(zip(['intercept'] + self.feature_names, self.model.pvalues))
        
        # Calculate metrics
        r_squared = self.model.rsquared
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        logger.info(f"MLR fitted for {self.disease_type}: R² = {r_squared:.3f}")
        
        return ModelResults(
            model_type="Multiple Linear Regression",
            disease=self.disease_type,
            r_squared=r_squared,
            mae=mae,
            rmse=rmse,
            coefficients=coefficients,
            p_values=p_values,
            predictions=predictions
        )
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X = data[self.feature_names].fillna(data[self.feature_names].mean())
        X_with_const = sm.add_constant(X)
        
        return self.model.predict(X_with_const)


class GAMAnalysis:
    """Generalized Additive Model for non-linear relationships"""
    
    def __init__(self, disease_type: str = "influenza"):
        self.disease_type = disease_type
        self.model = None
        self.feature_names = []
        self.is_fitted = False
    
    def fit(self, data: pd.DataFrame) -> ModelResults:
        """Fit GAM model with smooth terms"""
        
        # Prepare features (reuse MLR logic)
        mlr = MultipleLinearRegressionAdvanced(self.disease_type)
        X, y = mlr.prepare_features(data)
        self.feature_names = mlr.feature_names
        
        # Build GAM with smooth terms for continuous variables
        gam_terms = []
        for i, feature in enumerate(self.feature_names):
            gam_terms.append(s(i))  # Smooth term for each feature
        
        # Fit GAM
        self.model = LinearGAM(*gam_terms)
        self.model.fit(X, y)
        self.is_fitted = True
        
        # Calculate predictions
        predictions = self.model.predict(X)
        
        # Calculate metrics
        r_squared = self.model.statistics_['pseudo_r2']
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        # Feature importance (approximate using coefficients)
        feature_importance = {}
        for i, feature in enumerate(self.feature_names):
            # Use the range of partial dependence as importance measure
            pdep = self.model.partial_dependence(term=i, X=X)
            feature_importance[feature] = np.std(pdep)
        
        logger.info(f"GAM fitted for {self.disease_type}: Pseudo R² = {r_squared:.3f}")
        
        return ModelResults(
            model_type="Generalized Additive Model",
            disease=self.disease_type,
            r_squared=r_squared,
            mae=mae,
            rmse=rmse,
            coefficients={},  # GAM doesn't have simple coefficients
            p_values={},
            predictions=predictions,
            feature_importance=feature_importance
        )


class ARIMAXAnalysis:
    """ARIMAX model for time series forecasting with environmental variables"""
    
    def __init__(self, disease_type: str = "influenza"):
        self.disease_type = disease_type
        self.model = None
        self.fitted_model = None
        self.is_fitted = False
    
    def fit(self, data: pd.DataFrame) -> ModelResults:
        """Fit ARIMAX model"""
        
        # Ensure data is sorted by date
        if 'date' in data.columns:
            data = data.sort_values('date')
        
        # Prepare endogenous variable (cases)
        y = data['case_count'] if 'case_count' in data.columns else data['cases']
        
        # Prepare exogenous variables based on disease type
        if self.disease_type == "influenza":
            exog_cols = ['pm25', 'pm10', 'temperature_avg', 'humidity']
        elif self.disease_type == "legionellosis":
            exog_cols = ['temperature_avg', 'humidity', 'precipitation']
        elif self.disease_type == "hepatitis_a":
            exog_cols = ['precipitation', 'extreme_precipitation', 'water_ph']
        else:
            exog_cols = ['pm25', 'temperature_avg', 'precipitation']
        
        # Filter available exogenous variables
        available_exog = [col for col in exog_cols if col in data.columns]
        
        if available_exog:
            exog = data[available_exog].fillna(method='ffill')
        else:
            exog = None
        
        # Auto-determine ARIMA order
        try:
            auto_model = auto_arima(y, exogenous=exog, seasonal=True, 
                                  stepwise=True, suppress_warnings=True,
                                  max_order=3, max_seasonal_order=1)
            
            order = auto_model.order
            seasonal_order = auto_model.seasonal_order
            
        except:
            # Fallback to simple ARIMA(1,1,1)
            order = (1, 1, 1)
            seasonal_order = (0, 0, 0, 0)
        
        # Fit ARIMA model
        try:
            self.model = ARIMA(y, exog=exog, order=order, 
                             seasonal_order=seasonal_order)
            self.fitted_model = self.model.fit()
            self.is_fitted = True
            
            # Get predictions
            predictions = self.fitted_model.fittedvalues
            
            # Calculate metrics
            r_squared = 1 - (np.sum((y - predictions) ** 2) / np.sum((y - np.mean(y)) ** 2))
            mae = mean_absolute_error(y, predictions)
            rmse = np.sqrt(mean_squared_error(y, predictions))
            
            # Extract coefficients (simplified)
            coefficients = {}
            if hasattr(self.fitted_model, 'params'):
                param_names = self.fitted_model.param_names
                param_values = self.fitted_model.params
                coefficients = dict(zip(param_names, param_values))
            
            logger.info(f"ARIMAX fitted for {self.disease_type}: R² = {r_squared:.3f}")
            
            return ModelResults(
                model_type="ARIMAX",
                disease=self.disease_type,
                r_squared=r_squared,
                mae=mae,
                rmse=rmse,
                coefficients=coefficients,
                p_values={},
                predictions=predictions
            )
            
        except Exception as e:
            logger.error(f"ARIMAX fitting failed: {str(e)}")
            raise


class RandomForestAnalysis:
    """Random Forest for non-linear relationship detection and feature importance"""
    
    def __init__(self, disease_type: str = "influenza", n_estimators: int = 100):
        self.disease_type = disease_type
        self.n_estimators = n_estimators
        self.model = None
        self.feature_names = []
        self.is_fitted = False
    
    def fit(self, data: pd.DataFrame) -> ModelResults:
        """Fit Random Forest model"""
        
        # Prepare features
        mlr = MultipleLinearRegressionAdvanced(self.disease_type)
        X, y = mlr.prepare_features(data)
        self.feature_names = mlr.feature_names
        
        # Fit Random Forest
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            random_state=42,
            max_depth=10,
            min_samples_split=5
        )
        
        self.model.fit(X, y)
        self.is_fitted = True
        
        # Calculate predictions
        predictions = self.model.predict(X)
        
        # Calculate metrics
        r_squared = r2_score(y, predictions)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        # Feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        logger.info(f"Random Forest fitted for {self.disease_type}: R² = {r_squared:.3f}")
        
        return ModelResults(
            model_type="Random Forest",
            disease=self.disease_type,
            r_squared=r_squared,
            mae=mae,
            rmse=rmse,
            coefficients={},
            p_values={},
            predictions=predictions,
            feature_importance=feature_importance
        )


class XGBoostAnalysis:
    """XGBoost for advanced non-linear modeling"""
    
    def __init__(self, disease_type: str = "influenza"):
        self.disease_type = disease_type
        self.model = None
        self.feature_names = []
        self.is_fitted = False
    
    def fit(self, data: pd.DataFrame) -> ModelResults:
        """Fit XGBoost model"""
        
        # Prepare features
        mlr = MultipleLinearRegressionAdvanced(self.disease_type)
        X, y = mlr.prepare_features(data)
        self.feature_names = mlr.feature_names
        
        # Fit XGBoost
        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X, y)
        self.is_fitted = True
        
        # Calculate predictions
        predictions = self.model.predict(X)
        
        # Calculate metrics
        r_squared = r2_score(y, predictions)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        # Feature importance
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        logger.info(f"XGBoost fitted for {self.disease_type}: R² = {r_squared:.3f}")
        
        return ModelResults(
            model_type="XGBoost",
            disease=self.disease_type,
            r_squared=r_squared,
            mae=mae,
            rmse=rmse,
            coefficients={},
            p_values={},
            predictions=predictions,
            feature_importance=feature_importance
        )


class SpatialAnalysis:
    """Spatial autocorrelation analysis using Moran's I and Getis-Ord Gi*"""
    
    def __init__(self, disease_type: str = "influenza"):
        self.disease_type = disease_type
    
    def calculate_morans_i(self, gdf: gpd.GeoDataFrame, variable: str = 'case_rate') -> Dict[str, float]:
        """Calculate Global Moran's I"""
        
        # Create spatial weights
        w = weights.Queen.from_dataframe(gdf)
        w.transform = 'r'  # Row standardization
        
        # Calculate Moran's I
        moran = Moran(gdf[variable], w)
        
        return {
            'morans_i': moran.I,
            'p_value': moran.p_norm,
            'z_score': moran.z_norm,
            'expected_i': moran.EI
        }
    
    def calculate_local_morans_i(self, gdf: gpd.GeoDataFrame, variable: str = 'case_rate') -> gpd.GeoDataFrame:
        """Calculate Local Moran's I (LISA)"""
        
        # Create spatial weights
        w = weights.Queen.from_dataframe(gdf)
        w.transform = 'r'
        
        # Calculate Local Moran's I
        lisa = Moran_Local(gdf[variable], w)
        
        # Add results to GeoDataFrame
        gdf_result = gdf.copy()
        gdf_result['local_morans_i'] = lisa.Is
        gdf_result['p_value'] = lisa.p_sim
        gdf_result['cluster_type'] = lisa.q
        
        return gdf_result
    
    def calculate_getis_ord(self, gdf: gpd.GeoDataFrame, variable: str = 'case_rate') -> gpd.GeoDataFrame:
        """Calculate Getis-Ord Gi* statistic"""
        
        # Create spatial weights (include self)
        w = weights.Queen.from_dataframe(gdf)
        w.transform = 'r'
        
        # Calculate Getis-Ord Gi*
        gi_star = G_Local(gdf[variable], w, star=True)
        
        # Add results to GeoDataFrame
        gdf_result = gdf.copy()
        gdf_result['gi_star'] = gi_star.Zs
        gdf_result['gi_star_p'] = gi_star.p_sim
        
        # Classify hotspots/coldspots
        gdf_result['hotspot_type'] = 'Not Significant'
        gdf_result.loc[(gdf_result['gi_star'] > 1.96) & (gdf_result['gi_star_p'] < 0.05), 'hotspot_type'] = 'Hot Spot'
        gdf_result.loc[(gdf_result['gi_star'] < -1.96) & (gdf_result['gi_star_p'] < 0.05), 'hotspot_type'] = 'Cold Spot'
        
        return gdf_result


class DLNMApproximation:
    """
    Simplified implementation of Distributed Lag Non-Linear Models
    For complex environmental exposure-health relationships
    """
    
    def __init__(self, disease_type: str = "influenza", max_lag: int = 14):
        self.disease_type = disease_type
        self.max_lag = max_lag
        self.model = None
        self.is_fitted = False
    
    def create_lag_matrix(self, data: pd.DataFrame, variable: str) -> pd.DataFrame:
        """Create lagged variables matrix"""
        
        lag_df = pd.DataFrame()
        
        for lag in range(self.max_lag + 1):
            lag_col = f"{variable}_lag_{lag}"
            lag_df[lag_col] = data[variable].shift(lag)
        
        return lag_df.fillna(0)
    
    def fit(self, data: pd.DataFrame) -> ModelResults:
        """Fit DLNM approximation using polynomial distributed lags"""
        
        # Prepare main exposure variable based on disease
        if self.disease_type == "influenza":
            exposure_var = 'pm25'
        elif self.disease_type == "legionellosis":
            exposure_var = 'temperature_avg'
        elif self.disease_type == "hepatitis_a":
            exposure_var = 'precipitation'
        else:
            exposure_var = 'pm25'
        
        if exposure_var not in data.columns:
            raise ValueError(f"Exposure variable {exposure_var} not found in data")
        
        # Create lag matrix
        lag_matrix = self.create_lag_matrix(data, exposure_var)
        
        # Combine with outcome
        y = data['case_count'] if 'case_count' in data.columns else data['cases']
        
        # Fit polynomial distributed lag model (simplified)
        X = lag_matrix.iloc[self.max_lag:]  # Remove initial NaN rows
        y = y.iloc[self.max_lag:]
        
        # Use weighted regression (weights decrease with lag)
        lag_weights = np.exp(-np.arange(self.max_lag + 1) * 0.1)
        
        # Apply weights to lag columns
        for i, col in enumerate(X.columns):
            X[col] = X[col] * lag_weights[i]
        
        # Fit linear model
        X_const = sm.add_constant(X)
        model = OLS(y, X_const).fit()
        
        self.model = model
        self.is_fitted = True
        
        # Calculate cumulative effect
        cumulative_effect = np.sum(model.params[1:] * lag_weights)  # Exclude intercept
        
        predictions = model.predict(X_const)
        
        # Calculate metrics
        r_squared = model.rsquared
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        coefficients = {'cumulative_effect': cumulative_effect}
        coefficients.update(dict(zip(X.columns, model.params[1:])))
        
        logger.info(f"DLNM fitted for {self.disease_type}: R² = {r_squared:.3f}")
        
        return ModelResults(
            model_type="DLNM Approximation",
            disease=self.disease_type,
            r_squared=r_squared,
            mae=mae,
            rmse=rmse,
            coefficients=coefficients,
            p_values=dict(zip(X.columns, model.pvalues[1:])),
            predictions=predictions
        )


class ComprehensiveAnalyzer:
    """
    Comprehensive analyzer that runs all models for a given disease
    """
    
    def __init__(self, disease_type: str = "influenza"):
        self.disease_type = disease_type
        self.results = {}
    
    def run_all_analyses(self, data: pd.DataFrame) -> Dict[str, ModelResults]:
        """Run all analytical models"""
        
        logger.info(f"Running comprehensive analysis for {self.disease_type}")
        
        try:
            # 1. Multiple Linear Regression
            mlr = MultipleLinearRegressionAdvanced(self.disease_type)
            self.results['MLR'] = mlr.fit(data)
        except Exception as e:
            logger.error(f"MLR failed: {str(e)}")
        
        try:
            # 2. GAM
            gam = GAMAnalysis(self.disease_type)
            self.results['GAM'] = gam.fit(data)
        except Exception as e:
            logger.error(f"GAM failed: {str(e)}")
        
        try:
            # 3. ARIMAX (only if temporal data available)
            if 'date' in data.columns and len(data) > 20:
                arimax = ARIMAXAnalysis(self.disease_type)
                self.results['ARIMAX'] = arimax.fit(data)
        except Exception as e:
            logger.error(f"ARIMAX failed: {str(e)}")
        
        try:
            # 4. Random Forest
            rf = RandomForestAnalysis(self.disease_type)
            self.results['RandomForest'] = rf.fit(data)
        except Exception as e:
            logger.error(f"Random Forest failed: {str(e)}")
        
        try:
            # 5. XGBoost
            xgb_analyzer = XGBoostAnalysis(self.disease_type)
            self.results['XGBoost'] = xgb_analyzer.fit(data)
        except Exception as e:
            logger.error(f"XGBoost failed: {str(e)}")
        
        try:
            # 6. DLNM (if sufficient temporal data)
            if len(data) > 30:
                dlnm = DLNMApproximation(self.disease_type)
                self.results['DLNM'] = dlnm.fit(data)
        except Exception as e:
            logger.error(f"DLNM failed: {str(e)}")
        
        return self.results
    
    def get_best_model(self) -> Tuple[str, ModelResults]:
        """Return the best performing model based on R-squared"""
        
        if not self.results:
            raise ValueError("No models have been fitted")
        
        best_model_name = max(self.results.keys(), key=lambda k: self.results[k].r_squared)
        return best_model_name, self.results[best_model_name]
    
    def compare_models(self) -> pd.DataFrame:
        """Create comparison table of all models"""
        
        comparison_data = []
        
        for model_name, result in self.results.items():
            comparison_data.append({
                'Model': model_name,
                'R²': result.r_squared,
                'MAE': result.mae,
                'RMSE': result.rmse,
                'Disease': result.disease
            })
        
        return pd.DataFrame(comparison_data).sort_values('R²', ascending=False)


# Example usage function
def run_example_analysis():
    """
    Example analysis using synthetic data
    Demonstrates the exact multiple linear regression from specifications
    """
    
    # Create synthetic data matching Italian specifications
    np.random.seed(42)
    n_samples = 365  # One year of daily data
    
    # Environmental variables
    pm25 = np.random.normal(15, 5, n_samples)  # μg/m³
    ozone = np.random.normal(80, 20, n_samples)  # μg/m³
    rainy_days = np.random.poisson(0.3, n_samples)  # Binary daily indicator
    
    # Generate synthetic disease cases using the exact formula
    # Y = β₀ + β₁×PM2.5 + β₂×O₃ + β₃×Rainy_Days + ε
    beta_0 = 50
    beta_1 = 2.5
    beta_2 = 1.8
    beta_3 = -0.5
    
    epsilon = np.random.normal(0, 10, n_samples)
    
    case_count = beta_0 + beta_1 * pm25 + beta_2 * ozone + beta_3 * rainy_days + epsilon
    case_count = np.maximum(0, case_count)  # Ensure non-negative
    
    # Create DataFrame
    dates = pd.date_range('2023-01-01', periods=n_samples, freq='D')
    
    data = pd.DataFrame({
        'date': dates,
        'pm25': pm25,
        'ozone': ozone,
        'rainy_days': rainy_days,
        'case_count': case_count,
        'temperature_avg': np.random.normal(15, 8, n_samples),
        'humidity': np.random.normal(70, 15, n_samples),
        'precipitation': np.random.exponential(2, n_samples)
    })
    
    print("Running example analysis with synthetic data...")
    print(f"True coefficients: β₀={beta_0}, β₁={beta_1}, β₂={beta_2}, β₃={beta_3}")
    
    # Run comprehensive analysis
    analyzer = ComprehensiveAnalyzer("influenza")
    results = analyzer.run_all_analyses(data)
    
    # Print results
    print("\n=== Model Comparison ===")
    comparison = analyzer.compare_models()
    print(comparison.to_string(index=False))
    
    # Show best model
    best_name, best_result = analyzer.get_best_model()
    print(f"\nBest Model: {best_name}")
    print(f"Coefficients: {best_result.coefficients}")
    
    return analyzer


if __name__ == "__main__":
    run_example_analysis()
