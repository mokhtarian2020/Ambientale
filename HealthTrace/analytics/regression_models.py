"""
Multiple Linear Regression Model for Environmental-Health Correlation Analysis

Implementation of the example from Section 3.1:
Y = β0 + β1*PM2.5 + β2*O3 + β3*Rainy_Days + ε

Where Y is the number of cases of chronic bronchitis.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultipleLinearRegressionAnalysis:
    def __init__(self):
        self.model = LinearRegression()
        self.feature_names = []
        self.target_name = ""
        self.is_fitted = False
        
    def prepare_data(self, 
                    environmental_data: pd.DataFrame, 
                    health_data: pd.DataFrame,
                    disease_name: str = "chronic_bronchitis") -> pd.DataFrame:
        """
        Prepare and merge environmental and health data for analysis
        
        Args:
            environmental_data: DataFrame with environmental measurements
            health_data: DataFrame with disease cases
            disease_name: Name of the disease to analyze
            
        Returns:
            Merged DataFrame ready for analysis
        """
        try:
            # Aggregate environmental data by location and time period
            env_agg = environmental_data.groupby(['istat_code', 'measurement_year', 'measurement_month']).agg({
                'pm25': 'mean',
                'ozone': 'mean', 
                'precipitation': 'sum',
                'temperature_avg': 'mean',
                'humidity': 'mean',
                'no2': 'mean'
            }).reset_index()
            
            # Count rainy days (days with precipitation > 0)
            rainy_days = environmental_data[environmental_data['precipitation'] > 0].groupby(
                ['istat_code', 'measurement_year', 'measurement_month']
            ).size().reset_index(name='rainy_days')
            
            env_agg = env_agg.merge(rainy_days, on=['istat_code', 'measurement_year', 'measurement_month'], how='left')
            env_agg['rainy_days'] = env_agg['rainy_days'].fillna(0)
            
            # Aggregate health data (count cases by location and time)
            health_agg = health_data[health_data['disease_name'] == disease_name].groupby(
                ['istat_code', 'year', 'month']
            ).size().reset_index(name='case_count')
            
            # Merge environmental and health data
            merged_data = env_agg.merge(
                health_agg,
                left_on=['istat_code', 'measurement_year', 'measurement_month'],
                right_on=['istat_code', 'year', 'month'],
                how='inner'
            )
            
            # Remove rows with missing values
            merged_data = merged_data.dropna()
            
            logger.info(f"Prepared {len(merged_data)} records for analysis")
            return merged_data
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            return pd.DataFrame()
    
    def fit_model(self, 
                  data: pd.DataFrame,
                  target_column: str = 'case_count',
                  feature_columns: List[str] = None) -> Dict[str, Any]:
        """
        Fit multiple linear regression model
        
        Args:
            data: Prepared dataset
            target_column: Name of target variable (disease cases)
            feature_columns: List of feature column names
            
        Returns:
            Dictionary with model results
        """
        try:
            if feature_columns is None:
                feature_columns = ['pm25', 'ozone', 'rainy_days', 'temperature_avg', 'humidity', 'no2']
            
            # Prepare features and target
            X = data[feature_columns].copy()
            y = data[target_column].copy()
            
            # Remove rows with missing values
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X = X[mask]
            y = y[mask]
            
            if len(X) == 0:
                raise ValueError("No valid data points after removing missing values")
            
            # Store for later use
            self.feature_names = feature_columns
            self.target_name = target_column
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Fit model
            self.model.fit(X_train, y_train)
            self.is_fitted = True
            
            # Make predictions
            y_pred_train = self.model.predict(X_train)
            y_pred_test = self.model.predict(X_test)
            
            # Calculate metrics
            r2_train = r2_score(y_train, y_pred_train)
            r2_test = r2_score(y_test, y_pred_test)
            rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
            rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
            
            # Calculate statistical significance
            n = len(X_train)
            k = len(feature_columns)
            
            # Calculate p-values for coefficients
            mse = mean_squared_error(y_train, y_pred_train)
            var_residual = mse * (n - k - 1) / n
            
            try:
                # Calculate standard errors (simplified approach)
                X_train_array = X_train.values
                XtX_inv = np.linalg.inv(X_train_array.T @ X_train_array)
                se_coefficients = np.sqrt(var_residual * np.diag(XtX_inv))
                t_stats = self.model.coef_ / se_coefficients
                p_values = [2 * (1 - stats.t.cdf(abs(t_stat), n - k - 1)) for t_stat in t_stats]
            except:
                p_values = [None] * len(feature_columns)
            
            results = {
                'intercept': self.model.intercept_,
                'coefficients': dict(zip(feature_columns, self.model.coef_)),
                'p_values': dict(zip(feature_columns, p_values)),
                'r2_train': r2_train,
                'r2_test': r2_test,
                'rmse_train': rmse_train,
                'rmse_test': rmse_test,
                'n_samples': len(X),
                'feature_names': feature_columns,
                'target_name': target_column
            }
            
            # Generate interpretation
            results['interpretation'] = self._interpret_results(results)
            
            logger.info("Multiple linear regression model fitted successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error fitting model: {e}")
            return {}
    
    def _interpret_results(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable interpretation of results
        """
        interpretation = []
        
        interpretation.append(f"Model Performance:")
        interpretation.append(f"- R² (training): {results['r2_train']:.3f}")
        interpretation.append(f"- R² (test): {results['r2_test']:.3f}")
        interpretation.append(f"- RMSE (training): {results['rmse_train']:.3f}")
        interpretation.append(f"- RMSE (test): {results['rmse_test']:.3f}")
        interpretation.append("")
        
        interpretation.append("Equation:")
        equation = f"{results['target_name']} = {results['intercept']:.2f}"
        for feature, coef in results['coefficients'].items():
            sign = "+" if coef >= 0 else ""
            equation += f" {sign}{coef:.2f}*{feature}"
        interpretation.append(equation)
        interpretation.append("")
        
        interpretation.append("Coefficient Interpretation:")
        for feature, coef in results['coefficients'].items():
            p_val = results['p_values'].get(feature)
            significance = ""
            if p_val is not None:
                if p_val < 0.001:
                    significance = "***"
                elif p_val < 0.01:
                    significance = "**"
                elif p_val < 0.05:
                    significance = "*"
            
            interpretation.append(f"- {feature}: {coef:.3f} {significance}")
            if coef > 0:
                interpretation.append(f"  → Each unit increase in {feature} is associated with {coef:.3f} more cases")
            else:
                interpretation.append(f"  → Each unit increase in {feature} is associated with {abs(coef):.3f} fewer cases")
        
        return "\n".join(interpretation)
    
    def predict(self, environmental_data: Dict[str, float]) -> float:
        """
        Make prediction for new environmental data
        
        Args:
            environmental_data: Dictionary with environmental measurements
            
        Returns:
            Predicted number of cases
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Prepare input data
        X_new = np.array([[environmental_data[feature] for feature in self.feature_names]])
        
        # Make prediction
        prediction = self.model.predict(X_new)[0]
        
        return max(0, prediction)  # Ensure non-negative prediction
    
    def generate_example_analysis(self) -> Dict[str, Any]:
        """
        Generate the example from Section 3.1 of the document
        """
        # Example data matching the document
        example_data = {
            'pm25': [15, 20, 25, 30, 18, 22, 28, 16, 24, 32],
            'ozone': [60, 65, 70, 75, 62, 68, 73, 58, 71, 78],
            'rainy_days': [8, 6, 4, 3, 9, 7, 5, 10, 6, 2],
            'case_count': [65, 75, 85, 95, 70, 80, 90, 60, 85, 105]
        }
        
        df = pd.DataFrame(example_data)
        
        # Fit model
        results = self.fit_model(df, 'case_count', ['pm25', 'ozone', 'rainy_days'])
        
        # Add example prediction from document
        example_prediction = self.predict({
            'pm25': 20,
            'ozone': 65, 
            'rainy_days': 7
        })
        
        results['example_prediction'] = {
            'input': {'pm25': 20, 'ozone': 65, 'rainy_days': 7},
            'predicted_cases': example_prediction
        }
        
        return results


# Example usage
def run_example_analysis():
    """Run the example analysis from the document"""
    analyzer = MultipleLinearRegressionAnalysis()
    results = analyzer.generate_example_analysis()
    
    print("Multiple Linear Regression Analysis Results")
    print("=" * 50)
    print(results['interpretation'])
    print("\nExample Prediction:")
    print(f"Input: {results['example_prediction']['input']}")
    print(f"Predicted cases: {results['example_prediction']['predicted_cases']:.1f}")


if __name__ == "__main__":
    run_example_analysis()
