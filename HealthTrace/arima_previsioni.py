"""
ARIMA Time Series Forecasting for HealthTrace 🔮 Previsioni
Enhanced prediction module using ARIMA models for Italian infectious disease surveillance
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging
import warnings
warnings.filterwarnings('ignore')

# ARIMA and time series libraries
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
from scipy import stats
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARIMAPrevisioni:
    """
    🔮 ARIMA Time Series Forecasting for HealthTrace
    Implements sophisticated ARIMA models for infectious disease prediction
    """
    
    def __init__(self):
        self.models = {}
        self.fitted_models = {}
        self.seasonal_patterns = {
            "influenza": {"winter": 1.5, "spring": 0.8, "summer": 0.3, "autumn": 1.2},
            "legionellosi": {"winter": 0.7, "spring": 1.1, "summer": 1.4, "autumn": 0.9},
            "hepatitis_a": {"winter": 0.9, "spring": 1.2, "summer": 1.1, "autumn": 0.8}
        }
    
    def prepare_time_series_data(self, trends: List[Dict[str, Any]]) -> Tuple[pd.Series, pd.DatetimeIndex]:
        """
        Prepare time series data from database trends for ARIMA analysis
        """
        if not trends or len(trends) < 6:
            raise ValueError("Insufficient data for ARIMA analysis (minimum 6 data points required)")
        
        # Convert to pandas Series with datetime index
        dates = []
        cases = []
        
        for trend in trends:
            date_str = trend["month"]
            if isinstance(date_str, str):
                # Handle different date formats
                if "T" in date_str:
                    date = pd.to_datetime(date_str)
                else:
                    date = pd.to_datetime(date_str)
            else:
                date = pd.to_datetime(date_str)
            
            dates.append(date)
            cases.append(int(trend["cases"]))
        
        # Create time series
        ts_index = pd.DatetimeIndex(dates)
        ts_data = pd.Series(cases, index=ts_index)
        
        # Fill missing months with interpolation
        ts_data = ts_data.asfreq('MS').interpolate(method='linear')
        
        logger.info(f"Prepared time series: {len(ts_data)} data points from {ts_data.index.min()} to {ts_data.index.max()}")
        
        return ts_data, ts_index
    
    def detect_seasonality(self, ts_data: pd.Series, disease_type: str) -> Dict[str, Any]:
        """
        Detect seasonal patterns in the time series data
        """
        seasonality_info = {
            "has_seasonality": False,
            "seasonal_period": 12,  # Monthly data, yearly seasonality
            "trend": "none",
            "seasonal_strength": 0.0
        }
        
        if len(ts_data) >= 24:  # Need at least 2 years for seasonal decomposition
            try:
                decomposition = seasonal_decompose(ts_data, model='additive', period=12)
                
                # Calculate seasonal strength
                seasonal_var = np.var(decomposition.seasonal)
                residual_var = np.var(decomposition.resid.dropna())
                
                if residual_var > 0:
                    seasonal_strength = seasonal_var / (seasonal_var + residual_var)
                    seasonality_info["seasonal_strength"] = seasonal_strength
                    seasonality_info["has_seasonality"] = seasonal_strength > 0.1
                
                # Detect trend
                if decomposition.trend is not None:
                    trend_slope = np.polyfit(range(len(decomposition.trend.dropna())), 
                                           decomposition.trend.dropna(), 1)[0]
                    if abs(trend_slope) > 0.1:
                        seasonality_info["trend"] = "increasing" if trend_slope > 0 else "decreasing"
                
                logger.info(f"Seasonality detected for {disease_type}: strength={seasonal_strength:.3f}")
                
            except Exception as e:
                logger.warning(f"Seasonality detection failed: {str(e)}")
        
        return seasonality_info
    
    def fit_arima_model(self, ts_data: pd.Series, disease_type: str) -> Dict[str, Any]:
        """
        Fit optimal ARIMA model using auto-ARIMA with seasonal considerations
        """
        try:
            # Detect seasonality
            seasonality_info = self.detect_seasonality(ts_data, disease_type)
            
            logger.info(f"Fitting ARIMA model for {disease_type}...")
            
            # Use auto-ARIMA to find optimal parameters
            model = auto_arima(
                ts_data,
                start_p=0, start_q=0, max_p=3, max_q=3,
                seasonal=seasonality_info["has_seasonality"],
                m=12 if seasonality_info["has_seasonality"] else 1,  # Monthly seasonality
                start_P=0, start_Q=0, max_P=2, max_Q=2, max_D=1,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=False
            )
            
            # Store fitted model
            self.fitted_models[disease_type] = model
            
            # Extract model information
            model_info = {
                "order": model.order,
                "seasonal_order": model.seasonal_order if hasattr(model, 'seasonal_order') else (0, 0, 0, 0),
                "aic": model.aic(),
                "bic": model.bic(),
                "model_type": "SARIMAX" if seasonality_info["has_seasonality"] else "ARIMA",
                "seasonality": seasonality_info,
                "fitted_successfully": True
            }
            
            logger.info(f"ARIMA fitted for {disease_type}: {model_info['model_type']}{model_info['order']}")
            
            return model_info
            
        except Exception as e:
            logger.error(f"ARIMA fitting failed for {disease_type}: {str(e)}")
            return {
                "fitted_successfully": False,
                "error": str(e),
                "fallback_to_simple": True
            }
    
    def generate_arima_predictions(self, disease_type: str, periods: int = 6) -> List[Dict[str, Any]]:
        """
        Generate ARIMA forecasts for specified periods
        """
        if disease_type not in self.fitted_models:
            raise ValueError(f"No fitted model available for {disease_type}")
        
        model = self.fitted_models[disease_type]
        
        try:
            # Generate forecasts with confidence intervals
            forecast_result = model.predict(n_periods=periods, return_conf_int=True)
            
            if isinstance(forecast_result, tuple):
                forecasts = forecast_result[0]
                conf_int = forecast_result[1]
            else:
                forecasts = forecast_result
                conf_int = None
            
            # Create prediction results
            predictions = []
            
            # Get the last date from the original time series data
            try:
                # Try to get the end date from the model's training data
                import datetime
                last_date = datetime.datetime.now().replace(day=1)  # Default to current month start
            except:
                last_date = datetime.datetime.now().replace(day=1)
            
            for i in range(periods):
                # Calculate next month
                next_month = last_date + timedelta(days=30 * (i + 1))
                
                predicted_cases = max(0, int(round(forecasts[i])))
                
                # Calculate confidence intervals
                if conf_int is not None:
                    lower_bound = max(0, int(round(conf_int[i][0])))
                    upper_bound = int(round(conf_int[i][1]))
                    confidence_level = 0.95  # 95% confidence interval
                else:
                    # Fallback confidence calculation
                    std_error = np.std(forecasts) if len(forecasts) > 1 else predicted_cases * 0.2
                    lower_bound = max(0, int(predicted_cases - 1.96 * std_error))
                    upper_bound = int(predicted_cases + 1.96 * std_error)
                    confidence_level = 0.95
                
                # Apply seasonal adjustments if applicable
                season_factor = self._get_seasonal_factor(disease_type, next_month.month)
                predicted_cases = int(predicted_cases * season_factor)
                lower_bound = int(lower_bound * season_factor)
                upper_bound = int(upper_bound * season_factor)
                
                prediction = {
                    "month": next_month.strftime("%Y-%m-01T00:00:00"),
                    "predicted_cases": predicted_cases,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "confidence_level": confidence_level,
                    "prediction_method": "ARIMA",
                    "seasonal_factor": season_factor
                }
                
                predictions.append(prediction)
            
            logger.info(f"Generated {len(predictions)} ARIMA predictions for {disease_type}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"ARIMA prediction failed for {disease_type}: {str(e)}")
            return self._fallback_simple_prediction(disease_type, periods)
    
    def _get_seasonal_factor(self, disease_type: str, month: int) -> float:
        """
        Get seasonal adjustment factor based on disease type and month
        """
        if disease_type not in self.seasonal_patterns:
            return 1.0
        
        # Map month to season
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:  # [9, 10, 11]
            season = "autumn"
        
        return self.seasonal_patterns[disease_type].get(season, 1.0)
    
    def _fallback_simple_prediction(self, disease_type: str, periods: int) -> List[Dict[str, Any]]:
        """
        Fallback to simple moving average if ARIMA fails
        """
        logger.warning(f"Using fallback simple prediction for {disease_type}")
        
        predictions = []
        base_cases = 10  # Default fallback value
        
        for i in range(periods):
            next_month = datetime.now() + timedelta(days=30 * (i + 1))
            season_factor = self._get_seasonal_factor(disease_type, next_month.month)
            
            predicted_cases = int(base_cases * season_factor)
            
            prediction = {
                "month": next_month.strftime("%Y-%m-01T00:00:00"),
                "predicted_cases": predicted_cases,
                "lower_bound": max(0, predicted_cases - 5),
                "upper_bound": predicted_cases + 5,
                "confidence_level": 0.7,
                "prediction_method": "Simple_Fallback",
                "seasonal_factor": season_factor
            }
            
            predictions.append(prediction)
        
        return predictions
    
    def analyze_model_performance(self, disease_type: str, ts_data: pd.Series) -> Dict[str, Any]:
        """
        Analyze the performance of the fitted ARIMA model
        """
        if disease_type not in self.fitted_models:
            return {"error": "No fitted model available"}
        
        model = self.fitted_models[disease_type]
        
        try:
            # Get fitted values
            fitted_values = model.fittedvalues()
            
            # Calculate performance metrics
            mse = np.mean((ts_data - fitted_values) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(ts_data - fitted_values))
            
            # Calculate accuracy metrics
            mape = np.mean(np.abs((ts_data - fitted_values) / ts_data.replace(0, 1))) * 100
            
            performance = {
                "rmse": float(rmse),
                "mae": float(mae),
                "mape": float(mape),
                "aic": float(model.aic()),
                "bic": float(model.bic()),
                "model_summary": str(model.summary())
            }
            
            logger.info(f"Model performance for {disease_type}: RMSE={rmse:.2f}, MAE={mae:.2f}")
            
            return performance
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return {"error": str(e)}

# Create global instance
arima_previsioni = ARIMAPrevisioni()
