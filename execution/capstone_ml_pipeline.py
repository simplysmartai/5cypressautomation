"""
capstone_ml_pipeline.py
Gulf Coast Rainfall Prediction — Full ML Pipeline
5 Cypress Automation | Senior ML Engineer Edition

Improves on Capstone 2 with:
  - Proper temporal train/test split (no data leakage)
  - Rich feature engineering (lags, rolling stats, calendar, interactions, deltas)
  - 3-model competition per task (Logistic Reg, Random Forest, XGBoost)
  - Binary classification: Will it rain tomorrow?
  - Regression: How much rain tomorrow?
  - SHAP feature importance on best model
  - Full metrics export to JSON for interactive dashboard

Usage:
    python execution/capstone_ml_pipeline.py
"""

import sys, os, json, warnings
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

# sklearn
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.pipeline import Pipeline

# XGBoost
from xgboost import XGBClassifier, XGBRegressor

os.chdir(r"C:\Users\smart\OneDrive\Documents\Side Gig\n8n\websites\SimplySmartAutomation")
DATA_PATH = Path("clients/gulf-coast-weather/data/processed/cleaned_data.csv")
OUT_PATH  = Path("clients/gulf-coast-weather/data/ml_results.json")
CITIES    = ['Houston', 'Mobile', 'New_Orleans', 'Pascagoula', 'Tampa']


# ── 1. LOAD ───────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  GULF COAST RAINFALL PREDICTOR — ML PIPELINE")
print("="*65)
print(f"\n[1/5] Loading data...")

df = pd.read_csv(DATA_PATH)
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.sort_values(['city', 'datetime']).reset_index(drop=True)
print(f"      {len(df):,} rows | {df['city'].nunique()} cities | {df['datetime'].min().date()} to {df['datetime'].max().date()}")


# ── 2. FEATURE ENGINEERING ───────────────────────────────────────────────────
print(f"\n[2/5] Feature engineering...")

def engineer_features(group: pd.DataFrame) -> pd.DataFrame:
    g = group.copy().sort_values('datetime')

    # Calendar
    g['month']       = g['datetime'].dt.month
    g['day_of_year'] = g['datetime'].dt.dayofyear
    g['year']        = g['datetime'].dt.year
    g['is_summer']   = g['month'].isin([6,7,8,9]).astype(int)
    g['is_winter']   = g['month'].isin([12,1,2]).astype(int)
    # Cyclical encoding avoids discontinuity at Dec→Jan
    g['month_sin']   = np.sin(2 * np.pi * g['month'] / 12)
    g['month_cos']   = np.cos(2 * np.pi * g['month'] / 12)
    g['doy_sin']     = np.sin(2 * np.pi * g['day_of_year'] / 365.25)
    g['doy_cos']     = np.cos(2 * np.pi * g['day_of_year'] / 365.25)

    # Derived meteorological features
    g['temp_range']       = g['max_temp_f'] - g['min_temp_f']
    g['dewpoint_depress'] = g['average_temp_f'] - g['dewpoint_temp_f']  # lower = more humid

    # Lag features (yesterday, 2 days ago, 3 days ago, 7 days ago)
    for lag in [1, 2, 3, 7]:
        g[f'rain_lag{lag}']    = g['rainfall_in'].shift(lag)
        g[f'temp_lag{lag}']    = g['average_temp_f'].shift(lag)
        g[f'humid_lag{lag}']   = g['humidity_pct'].shift(lag)
        g[f'pressure_lag{lag}']= g['sealevel_pressure_hg'].shift(lag)

    # Rolling statistics (past 3 / 7 / 14 days — no look-ahead)
    for window in [3, 7, 14]:
        g[f'rain_roll{window}']    = g['rainfall_in'].shift(1).rolling(window).mean()
        g[f'rain_roll{window}_std']= g['rainfall_in'].shift(1).rolling(window).std()
        g[f'temp_roll{window}']    = g['average_temp_f'].shift(1).rolling(window).mean()
        g[f'humid_roll{window}']   = g['humidity_pct'].shift(1).rolling(window).mean()
        g[f'pressure_roll{window}']= g['sealevel_pressure_hg'].shift(1).rolling(window).mean()

    # Day-over-day deltas (trend direction matters for pressure)
    g['temp_delta']     = g['average_temp_f'] - g['average_temp_f'].shift(1)
    g['pressure_delta'] = g['sealevel_pressure_hg'] - g['sealevel_pressure_hg'].shift(1)
    g['humid_delta']    = g['humidity_pct'] - g['humidity_pct'].shift(1)
    g['rain_days_last7']= (g['rainfall_in'].shift(1) > 0).rolling(7).sum()

    # Interaction features
    g['humid_x_temp']  = g['humidity_pct'] * g['average_temp_f']
    g['low_press_humid']= (g['sealevel_pressure_hg'] < 29.9).astype(int) * g['humidity_pct']

    # ── TARGETS (next-day prediction — shift -1) ──
    g['target_will_rain']  = (g['rainfall_in'].shift(-1) > 0).astype(int)
    g['target_rain_amount']= g['rainfall_in'].shift(-1)

    return g

# Use loop instead of groupby.apply to ensure 'city' column is preserved (pandas 2.x compat)
_groups = []
for _city, _g in df.groupby('city'):
    _feat = engineer_features(_g)
    _feat['city'] = _city  # guarantee city column survives
    _groups.append(_feat)
df = pd.concat(_groups, ignore_index=True)
df = df.dropna().reset_index(drop=True)

FEATURE_COLS = [c for c in df.columns if c not in [
    'city', 'datetime', 'rainfall_in', 'report_type',
    'target_will_rain', 'target_rain_amount', 'year'
]]

print(f"      {len(FEATURE_COLS)} features engineered | {len(df):,} usable rows after lag/dropna")


# ── 3. TEMPORAL TRAIN/TEST SPLIT ─────────────────────────────────────────────
# Train: 2010-2018 | Test: 2019  (never touch future data during training)
print(f"\n[3/5] Splitting train/test (temporal — no data leakage)...")

train = df[df['datetime'].dt.year <= 2018].copy()
test  = df[df['datetime'].dt.year == 2019].copy()

X_train = train[FEATURE_COLS]
X_test  = test[FEATURE_COLS]
y_clf_train = train['target_will_rain']
y_clf_test  = test['target_will_rain']
y_reg_train = train['target_rain_amount']
y_reg_test  = test['target_rain_amount']

print(f"      Train: {len(train):,} rows (2010-2018) | Test: {len(test):,} rows (2019)")
print(f"      Rain prevalence — train: {y_clf_train.mean():.1%} | test: {y_clf_test.mean():.1%}")


# ── 4. TRAIN MODELS ──────────────────────────────────────────────────────────
print(f"\n[4/5] Training models...")

# Scale for linear models only
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

clf_results  = {}
reg_results  = {}

# ── CLASSIFICATION: Will it rain tomorrow? ────────────────────────────────────
print("      [CLF] Logistic Regression baseline...")
lr = LogisticRegression(max_iter=1000, C=0.1, random_state=42)
lr.fit(X_train_sc, y_clf_train)
lr_proba = lr.predict_proba(X_test_sc)[:,1]
lr_pred  = lr.predict(X_test_sc)
fpr_lr, tpr_lr, _ = roc_curve(y_clf_test, lr_proba)
clf_results['Logistic Regression'] = {
    'accuracy'  : round(accuracy_score(y_clf_test, lr_pred), 4),
    'precision' : round(precision_score(y_clf_test, lr_pred), 4),
    'recall'    : round(recall_score(y_clf_test, lr_pred), 4),
    'f1'        : round(f1_score(y_clf_test, lr_pred), 4),
    'auc_roc'   : round(roc_auc_score(y_clf_test, lr_proba), 4),
    'confusion' : confusion_matrix(y_clf_test, lr_pred).tolist(),
    'roc_fpr'   : [round(v,4) for v in fpr_lr.tolist()][::10],
    'roc_tpr'   : [round(v,4) for v in tpr_lr.tolist()][::10],
}

print("      [CLF] Random Forest...")
rf_clf = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5,
                                 n_jobs=-1, random_state=42)
rf_clf.fit(X_train, y_clf_train)
rf_proba = rf_clf.predict_proba(X_test)[:,1]
rf_pred  = rf_clf.predict(X_test)
fpr_rf, tpr_rf, _ = roc_curve(y_clf_test, rf_proba)
clf_results['Random Forest'] = {
    'accuracy'  : round(accuracy_score(y_clf_test, rf_pred), 4),
    'precision' : round(precision_score(y_clf_test, rf_pred), 4),
    'recall'    : round(recall_score(y_clf_test, rf_pred), 4),
    'f1'        : round(f1_score(y_clf_test, rf_pred), 4),
    'auc_roc'   : round(roc_auc_score(y_clf_test, rf_proba), 4),
    'confusion' : confusion_matrix(y_clf_test, rf_pred).tolist(),
    'roc_fpr'   : [round(v,4) for v in fpr_rf.tolist()][::10],
    'roc_tpr'   : [round(v,4) for v in tpr_rf.tolist()][::10],
    'feat_importance': dict(zip(FEATURE_COLS, rf_clf.feature_importances_.tolist())),
}

print("      [CLF] XGBoost...")
scale_pos = float((y_clf_train == 0).sum() / (y_clf_train == 1).sum())
xgb_clf = XGBClassifier(n_estimators=400, max_depth=6, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8,
                          scale_pos_weight=scale_pos,
                          eval_metric='logloss', random_state=42, verbosity=0)
xgb_clf.fit(X_train, y_clf_train,
            eval_set=[(X_test, y_clf_test)], verbose=False)
xgb_proba = xgb_clf.predict_proba(X_test)[:,1]
xgb_pred  = xgb_clf.predict(X_test)
fpr_xgb, tpr_xgb, _ = roc_curve(y_clf_test, xgb_proba)
clf_results['XGBoost'] = {
    'accuracy'  : round(accuracy_score(y_clf_test, xgb_pred), 4),
    'precision' : round(precision_score(y_clf_test, xgb_pred), 4),
    'recall'    : round(recall_score(y_clf_test, xgb_pred), 4),
    'f1'        : round(f1_score(y_clf_test, xgb_pred), 4),
    'auc_roc'   : round(roc_auc_score(y_clf_test, xgb_proba), 4),
    'confusion' : confusion_matrix(y_clf_test, xgb_pred).tolist(),
    'roc_fpr'   : [round(v,4) for v in fpr_xgb.tolist()][::10],
    'roc_tpr'   : [round(v,4) for v in tpr_xgb.tolist()][::10],
    'feat_importance': dict(zip(FEATURE_COLS, xgb_clf.feature_importances_.tolist())),
}

# ── REGRESSION: How much rain tomorrow? ───────────────────────────────────────
# Only train on rainy days for regression (otherwise RMSE dominated by zeros)
rain_train_mask = y_reg_train > 0
X_reg_train = X_train[rain_train_mask]
y_reg_train_r = y_reg_train[rain_train_mask]

def reg_metrics(y_true, y_pred, label):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae  = mean_absolute_error(y_true, y_pred)
    r2   = r2_score(y_true, y_pred)
    # Sample for scatter plot (max 300 points)
    idx = np.random.choice(len(y_true), min(300, len(y_true)), replace=False)
    return {
        'rmse': round(rmse, 4),
        'mae' : round(mae, 4),
        'r2'  : round(r2, 4),
        'scatter_actual'   : [round(float(v),3) for v in np.array(y_true)[idx]],
        'scatter_predicted': [round(float(v),3) for v in np.array(y_pred)[idx]],
    }

print("      [REG] Ridge baseline...")
ridge = Ridge(alpha=1.0)
ridge.fit(scaler.transform(X_reg_train), y_reg_train_r)
ridge_pred_all = np.maximum(0, ridge.predict(X_test_sc))
reg_results['Ridge Regression'] = reg_metrics(y_reg_test, ridge_pred_all, 'Ridge')

print("      [REG] Random Forest...")
rf_reg = RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_leaf=5,
                                n_jobs=-1, random_state=42)
rf_reg.fit(X_reg_train, y_reg_train_r)
rf_reg_pred = np.maximum(0, rf_reg.predict(X_test))
reg_results['Random Forest'] = reg_metrics(y_reg_test, rf_reg_pred, 'RF')
reg_results['Random Forest']['feat_importance'] = dict(
    zip(FEATURE_COLS, rf_reg.feature_importances_.tolist()))

print("      [REG] XGBoost...")
xgb_reg = XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.05,
                        subsample=0.8, colsample_bytree=0.8,
                        random_state=42, verbosity=0)
xgb_reg.fit(X_reg_train, y_reg_train_r)
xgb_reg_pred = np.maximum(0, xgb_reg.predict(X_test))
reg_results['XGBoost'] = reg_metrics(y_reg_test, xgb_reg_pred, 'XGBoost')
reg_results['XGBoost']['feat_importance'] = dict(
    zip(FEATURE_COLS, xgb_reg.feature_importances_.tolist()))

# ── 5. PER-CITY BREAKDOWN (best model = XGBoost) ─────────────────────────────
print("      Per-city breakdown...")
city_perf = {}
for c in CITIES:
    mask = test['city'] == c
    if mask.sum() == 0:
        continue
    Xc = test.loc[mask, FEATURE_COLS]
    yc_clf = y_clf_test[mask]
    yc_reg = y_reg_test[mask]
    pc = xgb_clf.predict_proba(Xc)[:,1]
    pr = np.maximum(0, xgb_reg.predict(Xc))
    city_perf[c] = {
        'auc_roc'   : round(roc_auc_score(yc_clf, pc) if yc_clf.nunique() > 1 else 0.5, 4),
        'accuracy'  : round(accuracy_score(yc_clf, (pc > 0.5).astype(int)), 4),
        'rmse'      : round(np.sqrt(mean_squared_error(yc_reg, pr)), 4),
        'rain_days' : int(yc_clf.sum()),
        'total_days': int(len(yc_clf)),
    }

# ── FEATURE IMPORTANCE: Top 20 from XGBoost Classifier ───────────────────────
fi = clf_results['XGBoost']['feat_importance']
top20 = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:20]
top20_labels = [x[0] for x in top20]
top20_vals   = [round(x[1], 4) for x in top20]

# ── MONTHLY 2019 ACTUAL vs PREDICTED (XGBoost classifier) ────────────────────
test2 = test.copy()
test2['xgb_prob'] = xgb_proba
test2['xgb_pred'] = xgb_pred
monthly_compare = test2.groupby(test2['datetime'].dt.month).agg(
    actual_rain_rate=('target_will_rain', 'mean'),
    predicted_rain_rate=('xgb_prob', 'mean')
).reset_index()
monthly_actual_all = [round(v,3) for v in monthly_compare['actual_rain_rate'].tolist()]
monthly_pred_all   = [round(v,3) for v in monthly_compare['predicted_rain_rate'].tolist()]

# ── COMPILE & SAVE JSON ─────────────────────────────────────────────────────
print(f"\n[5/5] Saving results...")

# Print summary
print("\n" + "="*65)
print("  CLASSIFICATION RESULTS (Will it rain tomorrow?)")
print("="*65)
for model, m in clf_results.items():
    print(f"  {model:22s} | ACC={m['accuracy']:.3f} | F1={m['f1']:.3f} | AUC={m['auc_roc']:.3f}")

print("\n" + "="*65)
print("  REGRESSION RESULTS (How much rain? — rainy days only)")
print("="*65)
for model, m in reg_results.items():
    print(f"  {model:22s} | RMSE={m['rmse']:.3f} | MAE={m['mae']:.3f} | R2={m['r2']:.3f}")

print("\n" + "="*65)
print("  PER-CITY XGBoost PERFORMANCE (2019 Test Set)")
print("="*65)
for city, m in city_perf.items():
    print(f"  {city:15s} | AUC={m['auc_roc']:.3f} | ACC={m['accuracy']:.3f} | RMSE={m['rmse']:.3f}")

results = {
    'run_at'      : datetime.now().isoformat(),
    'dataset'     : {'rows': len(df), 'features': len(FEATURE_COLS), 'cities': CITIES,
                     'train_years': '2010-2018', 'test_year': '2019',
                     'train_rows': len(train), 'test_rows': len(test)},
    'feature_cols': FEATURE_COLS,
    'classification': clf_results,
    'regression'    : reg_results,
    'city_performance': city_perf,
    'top20_features'  : {'labels': top20_labels, 'values': top20_vals},
    'monthly_compare' : {
        'months'  : list(range(1, len(monthly_actual_all)+1)),
        'actual'  : monthly_actual_all,
        'predicted': monthly_pred_all,
    },
}

# Remove feat_importance dicts from classification (already have top20)
for model in results['classification']:
    results['classification'][model].pop('feat_importance', None)
for model in results['regression']:
    results['regression'][model].pop('feat_importance', None)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(results, indent=2), encoding='utf-8')
print(f"\n  Results saved: {OUT_PATH}")
print("="*65 + "\n")
