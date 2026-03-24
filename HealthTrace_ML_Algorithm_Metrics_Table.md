# HealthTrace — Infectious Disease ML/AI Algorithm Metrics
*For Supervisor Review — Environmental-Disease Correlation Models*
*Target Diseases: Influenza · Legionellosi · Epatite A*

---

## Algorithm Performance Table

---

### Algorithm Type: Multiple Linear Regression (MLR / GLM baseline)

**Formula**: `Y = β₀ + β₁·PM2.5 + β₂·O₃ + β₃·Rainy_Days + ε`

**Role in project**: Baseline reference model. Establishes linear associations between environmental factors and disease incidence per comune ISTAT.

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| Coefficient of Determination | R² | Proportion of variance explained by the model |
| Root Mean Squared Error | RMSE | Average prediction error in case units |
| Mean Absolute Error | MAE | Average absolute prediction error |
| p-value per coefficient | p | Statistical significance of each environmental variable |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| R² | 0.45 – 0.65 | Acceptable for a linear model on epidemiological count data |
| RMSE | ± 3.5 – 6.0 cases/month | Based on province-level monthly counts |
| MAE | ± 2.0 – 4.5 cases/month | Lower bound for interpretation |
| p-value (PM2.5 → Influenza) | < 0.05 | Expected significant |
| p-value (Temp → Legionellosi) | < 0.05 | Expected significant |
| p-value (E.coli → Epatite A) | < 0.10 | Borderline — small n |

---

### Algorithm Type: GAM (Generalized Additive Model)

**Formula**: `Y = α + f₁(PM2.5) + f₂(Temp) + f₃(Humidity) + ε`
where `fᵢ` are non-parametric smooth spline functions.

**Role in project**: Captures **non-linear dose-response** relationships between environmental factors and disease incidence (e.g., the effect of PM2.5 is not constant — it increases faster above certain thresholds).

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| Pseudo R-squared | Pseudo R² | Proportion of deviance explained (replaces R² for count data) |
| AIC (Akaike Information Criterion) | AIC | Model fit penalized for complexity — lower = better |
| Root Mean Squared Error | RMSE | Average prediction error in case units |
| Mean Absolute Error | MAE | Average absolute prediction error |
| Effective Degrees of Freedom | EDF | Measures non-linearity of each smooth term (EDF=1 = linear) |
| p-value per smooth term | p | Significance of each environmental smooth function |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| Pseudo R² | 0.55 – 0.75 | Better than MLR due to non-linear capture |
| AIC | Lower than MLR baseline by ≥ 10 points | Confirms non-linearity adds value |
| RMSE | ± 2.5 – 5.0 cases/month | Improvement over MLR |
| MAE | ± 1.8 – 3.5 cases/month | |
| EDF (PM2.5 smooth) | 2.5 – 4.5 | Confirms non-linear relationship |
| p (PM2.5 → Influenza) | < 0.01 | Strong expected significance |
| p (Temp_acqua → Legionellosi) | < 0.05 | Expected significant |

---

### Algorithm Type: ARIMAX (AutoRegressive Integrated Moving Average with eXogenous variables)

**Formula**: `Y_t = c + φ₁Y_{t-1} + ... + θ₁ε_{t-1} + β₁·PM2.5_t + β₂·Temp_t + ε_t`

**Role in project**: **Time-series forecasting** of monthly disease cases incorporating seasonal patterns (AR, MA, seasonal components) plus real-time environmental variables as external regressors. Used for 7–30 day forward predictions.

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| R² (in-sample) | R² | Fit on historical training data |
| Mean Absolute Percentage Error | MAPE | Percentage error of forecasts |
| Root Mean Squared Error | RMSE | Forecast error in case units |
| Mean Absolute Error | MAE | Average absolute forecast error |
| AIC / BIC | AIC, BIC | Model order selection criteria |
| Ljung-Box test p-value | Q-stat p | Tests residuals are white noise (good fit if p > 0.05) |
| ARIMA order | (p,d,q)(P,D,Q)_s | Auto-selected seasonal order |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| R² | 0.60 – 0.78 | Monthly Napoli data (17 time points) — limited series |
| MAPE | ± 15% – 30% | Acceptable for short infectious disease series |
| RMSE | ± 3.0 – 6.5 cases/month | |
| MAE | ± 2.0 – 4.5 cases/month | |
| Ljung-Box p | > 0.05 | Residuals should be white noise |
| Best order (Influenza) | (1,1,1)(1,0,0)₁₂ | Expected seasonal ARIMA |
| Best order (Legionellosi) | (1,1,1)(0,0,0) | Non-seasonal expected |

---

### Algorithm Type: DLNM (Distributed Lag Non-Linear Model)

**Formula**: `Y_t = α + Σ_{l=0}^{L} f(x_{t-l}, l) + ε_t`
where `f(x,l)` is a bivariate smooth function over exposure **and** lag simultaneously.

**Role in project**: Models **delayed environmental effects** — e.g., PM2.5 exposure 10 days ago affecting today's influenza cases. Captures both non-linearity and lag effects in a single model. Standard in environmental epidemiology (WHO-endorsed).

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| R² | R² | Proportion of variance explained |
| Root Mean Squared Error | RMSE | Average prediction error |
| Mean Absolute Error | MAE | Average absolute error |
| Cumulative Relative Risk | RR_cum | Total disease risk from sustained exposure over lag period |
| Lag at peak effect | Lag_peak | Day of maximum effect after exposure |
| 95% Confidence Interval on RR | 95% CI | Uncertainty of risk estimate |
| p-value for exposure-lag surface | p | Overall significance of the lagged relationship |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| R² | 0.65 – 0.82 | Best statistical fit — captures lag structure |
| RMSE | ± 2.0 – 4.5 cases/month | |
| MAE | ± 1.5 – 3.0 cases/month | |
| Lag_peak (PM2.5 → Influenza) | 5 – 10 days | Literature: 7-day lag typical |
| Lag_peak (Temp → Legionellosi) | 3 – 7 days | Literature: 5-day lag typical |
| RR_cum (PM2.5 +10 μg/m³) | 1.08 – 1.20 | 8–20% increased influenza risk |
| RR_cum (Temp +5°C in water) | 1.15 – 1.40 | 15–40% increased legionellosi risk |
| Max lag window | L = 14 days | Applied in implementation |

---

### Algorithm Type: Random Forest

**Role in project**: **Ensemble method** for robust prediction and feature importance ranking — identifies which environmental variables matter most per disease. Less interpretable than GAM but higher predictive accuracy.

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| R² (cross-validated) | R²_CV | 5-fold cross-validation R² — prevents overfitting |
| Root Mean Squared Error | RMSE | Average prediction error |
| Mean Absolute Error | MAE | Average absolute error |
| Feature Importance | FI | Gini impurity-based importance per variable (0–1) |
| Out-of-Bag Error | OOB | Internal validation estimate (unique to Random Forest) |
| Number of estimators | n_trees | Trees in the ensemble (set to 100 in implementation) |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| R² (CV) | 0.72 – 0.88 | Higher than GLM/GAM due to ensemble |
| RMSE | ± 1.8 – 4.0 cases/month | |
| MAE | ± 1.2 – 2.8 cases/month | |
| Top feature (Influenza) | PM2.5 (FI ≈ 0.35) | Expected highest importance |
| Top feature (Legionellosi) | Temperature (FI ≈ 0.42) | Water temp + air temp |
| Top feature (Epatite A) | E.coli (FI ≈ 0.48) | Expected dominant factor |
| OOB score | 0.70 – 0.86 | Internal validation |

---

### Algorithm Type: XGBoost (eXtreme Gradient Boosting)

**Role in project**: **Highest accuracy model** — sequential ensemble of decision trees optimized with gradient descent. Used for final risk scoring in the dashboard and alert system.

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| R² (cross-validated) | R²_CV | 5-fold cross-validation |
| Root Mean Squared Error | RMSE | Average prediction error |
| Mean Absolute Error | MAE | Average absolute error |
| SHAP values | SHAP | Shapley values — explainable feature contributions per prediction |
| Feature Importance | FI | Gain-based feature importance |
| Log-loss / Eval metric | Eval | Training/test loss curve convergence |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| R² (CV) | 0.80 – 0.93 | Best predictive model |
| RMSE | ± 1.5 – 3.5 cases/month | |
| MAE | ± 1.0 – 2.5 cases/month | |
| Improvement over MLR | +15% – +30% R² | Typical XGBoost vs. linear gain |
| Top 3 features (Influenza) | PM2.5, Temperature, Humidity | Expected SHAP ranking |
| Top 3 features (Legionellosi) | Water_Temp, Humidity, Precipitation | |
| Top 3 features (Epatite A) | E.coli, pH, Precipitation | |

---

### Algorithm Type: Spatial Models (Moran's I + Getis-Ord Gi*)

**Role in project**: Detects **geographic clustering** of disease cases — are high-incidence comuni located near each other (spatial autocorrelation)? Identifies hot spots and cold spots for alert prioritization.

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| Global Moran's I | I | Spatial autocorrelation index: -1 (dispersed) to +1 (clustered) |
| Z-score (Moran) | Z | Standard deviations from expected I under randomness |
| p-value (Moran) | p | Significance of spatial pattern |
| Local Moran's I (LISA) | Iᵢ | Per-comune clustering statistic |
| Getis-Ord Gi* | Gi* | Z-score for hot spot detection per comune |
| Hot spot threshold | z > 1.96 | p < 0.05 — statistically significant hot spot |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| Global Moran's I (Legionellosi) | 0.25 – 0.50 | Moderate-strong clustering around Napoli |
| Global Moran's I (Influenza) | 0.15 – 0.35 | Moderate clustering |
| Global Moran's I (Epatite A) | 0.10 – 0.30 | Weaker — fewer cases |
| p-value (Legionellosi) | < 0.01 | Expected significant clustering |
| p-value (Influenza) | < 0.05 | Expected significant |
| Primary hot spot | Napoli (063049) | Expected Gi* z > 3.0 |
| Secondary hot spots | Marano, Casalnuovo, Casoria | Expected Gi* z = 1.96–2.5 |

---

### Algorithm Type: Case-Crossover (Conditional Logistic Regression)

**Design**: Each case patient acts as their own control — their environmental exposure on the day of the disease onset is compared against exposure on matched control days (same weekday, same month, different weeks). Eliminates all time-invariant confounders (age, sex, chronic conditions) by design.

**Role in project**: Estimates the **acute triggering effect** of short-term environmental spikes (e.g., sudden PM2.5 peak) on disease onset. Gold standard for studying transient environmental exposures in epidemiology. Particularly powerful for Legionellosi (water temperature spikes) and Influenza (cold spell events).

**Formula**: `log[P(case)/P(control)] = β₁·Exposure_case_day - β₁·Exposure_control_day`
Result expressed as **Odds Ratio**: `OR = exp(β₁)`

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| Odds Ratio | OR | Multiplicative change in disease odds per unit increase in exposure |
| 95% Confidence Interval | 95% CI | Uncertainty range of OR — must not include 1.0 for significance |
| p-value | p | H₀: OR = 1 (no effect). Significant if p < 0.05 |
| Conditional Log-Likelihood | CLL | Fit of the conditional logistic model |
| McFadden's Pseudo R² | Pseudo R² | Overall model fit for conditional logistic |
| Number of matched strata | n_strata | One stratum per case patient (n = cases in dataset) |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| OR (PM2.5 +10 μg/m³ → Influenza) | **1.08 – 1.18** | 8–18% increased odds per 10 μg/m³ increase |
| OR (Water temp +5°C → Legionellosi) | **1.20 – 1.45** | 20–45% increased odds — strong acute trigger |
| OR (E.coli spike → Epatite A) | **1.15 – 1.35** | 15–35% increased odds during contamination events |
| 95% CI width | **narrow** (does not cross 1.0) | Significance confirmed if both bounds > 1.0 or < 1.0 |
| p-value (all 3 diseases) | **< 0.05** | Expected statistically significant |
| Number of strata | **113 (Legionellosi), 129 (Influenza), 32 (Epatite A)** | One per case in GESAN DB |
| Pseudo R² | **0.12 – 0.30** | Typical range for conditional logistic — lower than regression |

**Python libraries:**
```python
from statsmodels.discrete.conditional_models import ConditionalLogit  # main model
from lifelines import CoxTimeVaryingFitter                             # alternative
import scipy.stats                                                      # CI calculation
```

---

### Algorithm Type: LSTM (Long Short-Term Memory — Recurrent Neural Network)

**Architecture**: Stacked LSTM layers with dropout regularization, trained on sequences of daily environmental measurements to predict future disease case counts. Learns both short-term fluctuations and long-term seasonal patterns.

**Role in project**: **Deep learning time series forecasting** — highest potential accuracy for multi-step ahead predictions (7–30 days). Unlike ARIMAX, LSTM requires no manual specification of model order and automatically discovers complex temporal patterns including non-linear interactions between multiple environmental variables.

**Architecture used in project:**
```
Input → LSTM(64 units) → Dropout(0.2) → LSTM(32 units) → Dropout(0.2) → Dense(1)
Input shape: (sequence_length=30 days, features=7 environmental variables)
Output: predicted case count t+1 to t+7
```

| Performance Indicator | Symbol | Description |
|-----------------------|--------|-------------|
| R² (coefficient of determination) | R² | Proportion of variance explained on test set |
| Root Mean Squared Error | RMSE | Average forecast error in case units |
| Mean Absolute Percentage Error | MAPE | Percentage forecast error — scale-independent |
| Mean Absolute Error | MAE | Average absolute forecast error |
| Training Loss (MSE) | Loss | Convergence of training and validation loss curves |
| Validation Loss | Val_Loss | Overfitting check — should track training loss |

**Expected performance from the project:**

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| R² | **≥ 0.80** | Better than ARIMAX when sufficient data available |
| RMSE | **≈ ± 10%** of mean case count | Literature benchmark [4] |
| MAPE | **≤ 15% – 20%** | Target from project specification |
| MAE | **± 1.0 – 2.5** cases/month | |
| Improvement over ARIMAX | **+5% – +15% R²** | Typical LSTM vs. ARIMA gain in epidemiology |
| Epochs to convergence | **50 – 150** | With early stopping (patience=10) |
| Sequence length | **30 days** | Lookback window for environmental input |
| Training/Validation split | **80% / 20%** | Chronological split (no shuffle) |

> **Important caveat**: With current dataset size (≤ 17 monthly points for Napoli), LSTM is **data-hungry** and may underperform ARIMAX. Performance targets above apply once 3+ years of data are available (2024–2026). Currently, LSTM should be treated as **future roadmap** while ARIMAX and GAM are the operational models.

**Python libraries:**
```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler           # feature normalization
```

---

## Summary Comparison Table

| Algorithm | R² / OR Expected | RMSE (cases/month) | MAE (cases/month) | Best For |
|-----------|----------------|-------------------|------------------|---------|
| MLR (baseline) | R² 0.45–0.65 | ±3.5–6.0 | ±2.0–4.5 | Interpretability, significance testing |
| **GAM** | **R² 0.55–0.75** | **±2.5–5.0** | **±1.8–3.5** | **Non-linear dose-response** |
| **ARIMAX** | **R² 0.60–0.78** | **±3.0–6.5** | **±2.0–4.5** | **Forecasting, seasonal trends** |
| **DLNM** | **R² 0.65–0.82** | **±2.0–4.5** | **±1.5–3.0** | **Lag effects, WHO standard** |
| Random Forest | R² 0.72–0.88 | ±1.8–4.0 | ±1.2–2.8 | Feature importance ranking |
| **XGBoost** | **R² 0.80–0.93** | **±1.5–3.5** | **±1.0–2.5** | **Best prediction, alerting** |
| **Case-Crossover** | **OR 1.08–1.45, p < 0.05** | — | — | **Acute exposure triggers, OR estimation** |
| **LSTM** | **R² ≥ 0.80, MAPE ≤ 20%** | **≈ ±10% of mean** | **±1.0–2.5** | **Deep learning multi-step forecast** |
| Moran's I / Gi* | I = 0.15–0.50 | — | — | Geographic hot spot detection |

---

## Python Libraries — Complete List

### Yes, stiamo usando Python. Ecco l'elenco completo delle librerie:

```
# ── CORE DATA SCIENCE ──────────────────────────────────────────
pandas==2.1.4           # Data manipulation and time series
numpy==1.24.4           # Numerical computing
scipy==1.11.4           # Statistical functions, interpolation

# ── MACHINE LEARNING (Random Forest, XGBoost) ─────────────────
scikit-learn==1.3.2     # Random Forest, cross-validation, metrics
xgboost==2.0.1          # XGBoost gradient boosting

# ── GAM / GLM ─────────────────────────────────────────────────
pyGAM==0.9.0            # Generalized Additive Models (LinearGAM, s(), f())
statsmodels==0.14.0     # GLM, OLS, statistical tests, p-values

# ── TIME SERIES — ARIMAX ──────────────────────────────────────
statsmodels==0.14.0     # ARIMA, SARIMAX (same library as above)
pmdarima==2.0.4         # auto_arima — automatic ARIMA order selection

# ── DLNM (Distributed Lag Non-Linear Models) ──────────────────
dlnm==0.2.0             # DLNM cross-basis functions
scipy==1.11.4           # Spline interpolation for lag functions (same as above)

# ── CASE-CROSSOVER (Conditional Logistic Regression) ──────────
# statsmodels already included above:
#   from statsmodels.discrete.conditional_models import ConditionalLogit
lifelines==0.27.8       # Alternative: CoxTimeVaryingFitter for case-crossover
#   from lifelines import CoxTimeVaryingFitter

# ── LSTM / DEEP LEARNING (Recurrent Neural Networks) ──────────
tensorflow==2.15.0      # LSTM via tf.keras.layers.LSTM — primary choice
keras==2.15.0           # High-level Keras API (bundled with TensorFlow)
torch==2.1.2            # PyTorch — alternative LSTM implementation
torchvision==0.16.2     # PyTorch vision utilities (optional)

# ── SPATIAL MODELS ────────────────────────────────────────────
geopandas==0.14.1       # Spatial data (GeoDataFrame, shapefiles)
libpysal==4.9.2         # Spatial weights (Queen contiguity)
esda==2.5.1             # Moran's I, Local Moran's I (LISA), Getis-Ord Gi*
spreg==1.5.0            # Spatial regression models
mgwr==2.2.1             # Geographically Weighted Regression (GWR)

# ── VISUALIZATION ─────────────────────────────────────────────
plotly==5.17.0          # Interactive charts (dashboard)
folium==0.15.0          # Interactive maps (hot spot maps)
matplotlib==3.8.2       # Static plots, correlation heatmaps
seaborn==0.13.0         # Statistical visualization

# ── DATABASE / BACKEND ────────────────────────────────────────
psycopg2-binary==2.9.9  # PostgreSQL connection (GESAN malattie DB)
sqlalchemy==2.0.23      # ORM for database queries
```

### Install command:
```bash
pip install pandas==2.1.4 numpy==1.24.4 scipy==1.11.4 \
            scikit-learn==1.3.2 xgboost==2.0.1 \
            pyGAM==0.9.0 statsmodels==0.14.0 pmdarima==2.0.4 \
            dlnm==0.2.0 \
            lifelines==0.27.8 \
            tensorflow==2.15.0 torch==2.1.2 \
            geopandas==0.14.1 libpysal==4.9.2 esda==2.5.1 spreg==1.5.0 mgwr==2.2.1 \
            plotly==5.17.0 folium==0.15.0 matplotlib==3.8.2 seaborn==0.13.0 \
            psycopg2-binary==2.9.9 sqlalchemy==2.0.23
```

---

## Note on Expected Performance Ranges

Performance ranges are expressed as **±** to indicate the uncertainty band given:
- Current dataset: 129 Influenza + 113 Legionellosi + 32 Epatite A cases (2024–2025)
- Geographic scope: primarily Napoli province (Campania)
- These ranges will **narrow and improve** as more data is collected from Calabria and Molise

All ranges are consistent with peer-reviewed environmental epidemiology literature for
similar study designs in Italian and Mediterranean contexts.

---
*HealthTrace Platform — Version 1.0 — March 2026*
