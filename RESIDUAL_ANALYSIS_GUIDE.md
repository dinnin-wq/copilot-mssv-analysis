# Residual Analysis by Sleep State

## Overview

This module implements comprehensive residual analysis with sleep state visualization:

```python
# Your exact visualization:
plt.scatter(log_E, residuals, c=state_labels)
```

Where:
- **X-axis (log_E)**: Log-transformed entropy
- **Y-axis (residuals)**: Model residuals from OLS regression
- **Color (state_labels)**: Sleep state classification

---

## Sleep State Color Mapping

```
🟢 Green       = Deep Sleep (Re_g < 1.0)
🟡 Yellow      = Light Sleep (1.0 < Re_g < 2.0)
🔴 Red         = Wake/REM (Re_g > 2.0)
⚪ Gray        = Undetermined
```

---

## The Visualization

### Main Plot: Residuals vs log(E) by Sleep State

```python
from residual_analysis_by_state import ResidualAnalysisByState

analyzer = ResidualAnalysisByState()

# Fit regression
model, log_E, residuals = analyzer.fit_regression(E_vals, S_vals)

# Classify sleep states
state_labels = analyzer.classify_sleep_state(E_vals, S_vals)

# Plot (your exact request!)
fig = analyzer.plot_residuals_by_state(log_E, residuals, state_labels)
plt.savefig('residuals_by_state.png')
plt.show()
```

**What to look for:**

✅ **Good Model Fit:**
- Residuals scattered randomly around 0
- No patterns or trends
- Equal spread across entropy values
- All states mixed together

⚠️ **Problems:**
- Residuals cluster by sleep state → State affects model
- Systematic pattern → Non-linear relationship
- Increasing/decreasing trend → Heteroscedasticity
- Outliers → Measurement error or artifact

---

## Four Diagnostic Plots

### 1. Residuals vs log(E) by State (YOUR REQUEST)

```python
fig = analyzer.plot_residuals_by_state(log_E, residuals, state_labels)
```

**Output:** `01_residuals_by_state.png`

**Interpretation:**
- Points should be randomly distributed around y=0
- If colors are clustered separately → Sleep state affects residuals
- If wide spread at high entropy → Heteroscedasticity

---

### 2. Residuals vs Fitted Values

```python
fig = analyzer.plot_residuals_by_fitted(fitted_values, residuals, state_labels)
```

**Output:** `02_residuals_vs_fitted.png`

**What it shows:**
- Residual pattern across predicted values
- X-axis: Model predictions (log(Re_g))
- Y-axis: Errors (residuals)
- Colors: Sleep states

**Red flags:**
- Funnel shape → Variance depends on fitted value
- Systematic curve → Non-linear relationship missed

---

### 3. Q-Q Plot by State

```python
fig = analyzer.plot_qq_by_state(residuals, state_labels)
```

**Output:** `03_qq_plot_by_state.png`

**What it shows:**
- Whether residuals are normally distributed
- X-axis: Theoretical normal quantiles
- Y-axis: Sample quantiles
- Colors: Sleep states

**Interpretation:**
- Points on red diagonal → Normal distribution ✓
- Points deviate from diagonal → Non-normal residuals ✗

---

### 4. Residual Distribution by State

```python
fig = analyzer.plot_residuals_distribution_by_state(residuals, state_labels)
```

**Output:** `04_residuals_distribution.png`

**What it shows:**
- Histogram of residuals
- Separate color for each sleep state
- Overlaid distributions

**Good model:**
- Bell curve centered at 0
- States overlap (no bias by state)
- Symmetric distribution

---

## Statistics by Sleep State

```python
analyzer.print_residual_statistics_by_state(residuals, state_labels)
```

**Output:**
```
================================================================================
RESIDUAL STATISTICS BY SLEEP STATE
================================================================================

Deep Sleep:
  n                = 28
  Mean             = 0.012345
  Std Dev          = 0.087654
  Min              = -0.234567
  Max              = 0.156789
  Median           = 0.001234
  Q25-Q75          = [-0.045678, 0.067890]

Light Sleep:
  n                = 35
  Mean             = -0.001234
  Std Dev          = 0.098765
  Min              = -0.345678
  Max              = 0.234567
  Median           = -0.012345
  Q25-Q75          = [-0.056789, 0.078901]

Wake/REM:
  n                = 29
  Mean             = -0.023456
  Std Dev          = 0.112345
  Min              = -0.456789
  Max              = 0.345678
  Median           = -0.034567
  Q25-Q75          = [-0.067890, 0.089012]
================================================================================
```

**Interpretation:**
- **Mean near 0** → Unbiased estimates
- **Similar Std Dev** → Homogeneous variance
- **Symmetric range** → No skewness
- **Similar across states** → State-independent residuals

---

## Complete Workflow

```python
from residual_analysis_by_state import ResidualAnalysisByState
import numpy as np

# Load your MSSV data
E_vals = np.array([...])  # Entropy per channel
S_vals = np.array([...])  # Connectivity per channel

# Initialize analyzer
analyzer = ResidualAnalysisByState()

# Step 1: Fit regression model
model, log_E, residuals = analyzer.fit_regression(E_vals, S_vals)
print(model.summary())

# Step 2: Classify sleep states
state_labels = analyzer.classify_sleep_state(E_vals, S_vals)
print(f"Deep Sleep: {sum(s == 'Deep Sleep' for s in state_labels)}")
print(f"Light Sleep: {sum(s == 'Light Sleep' for s in state_labels)}")
print(f"Wake/REM: {sum(s == 'Wake/REM' for s in state_labels)}")

# Step 3: Create visualizations
fig1 = analyzer.plot_residuals_by_state(log_E, residuals, state_labels)
fig1.savefig('residuals_by_state.png')

fig2 = analyzer.plot_residuals_by_fitted(model.fittedvalues, residuals, state_labels)
fig2.savefig('residuals_vs_fitted.png')

fig3 = analyzer.plot_qq_by_state(residuals, state_labels)
fig3.savefig('qq_plot.png')

fig4 = analyzer.plot_residuals_distribution_by_state(residuals, state_labels)
fig4.savefig('residuals_distribution.png')

# Step 4: Print statistics
analyzer.print_residual_statistics_by_state(residuals, state_labels)
```

---

## Expected Output Files

When running `python residual_analysis_by_state.py`:

```
01_residuals_by_state.png           ← Your scatter plot!
02_residuals_vs_fitted.png          ← Model diagnostics
03_qq_plot_by_state.png             ← Normality check
04_residuals_distribution.png       ← State comparison
```

---

## Model Diagnostics Checklist

✅ **For a good model:**

- [ ] R² > 0.90 (from OLS summary)
- [ ] β₁ (log E) ≈ 2.0 ± 0.1
- [ ] β₂ (log S) ≈ -1.0 ± 0.1
- [ ] p-values < 0.001 (highly significant)
- [ ] Residuals centered at 0
- [ ] Residuals randomly distributed
- [ ] Q-Q plot points on diagonal
- [ ] No clustering by sleep state
- [ ] Similar variance across entropy values
- [ ] No systematic patterns

---

## Interpretation by Sleep State

### If residuals differ by state:

**Deep Sleep residuals large?**
→ Formula works better for wake/light sleep

**Wake/REM residuals large?**
→ Formula works better for deep sleep

**All states have large residuals?**
→ Overall model needs improvement

### Possible causes:

1. **Sleep state affects actual Re_g differently than formula predicts**
   - Solution: Fit separate models per state

2. **Measurement noise varies by state**
   - Solution: State-weighted regression

3. **Other factors present in sleep states**
   - Solution: Include additional predictors

---

## Integration with MSSV Pipeline

```python
from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer
from residual_analysis_by_state import ResidualAnalysisByState

# Analyze MSSV dataset
mssv = MSSVEEGAnalyzer(dataset_root='/path/to/ds006366')
results = mssv.analyze_all_subjects(max_subjects=92)

# Extract metrics
E_all = []
S_all = []
for result in results:
    E_all.extend(result.entropy_per_channel)
    S_all.extend(result.connectivity_per_channel)

E_all = np.array(E_all)
S_all = np.array(S_all)

# Run residual analysis
analyzer = ResidualAnalysisByState()
model, log_E, residuals = analyzer.fit_regression(E_all, S_all)
state_labels = analyzer.classify_sleep_state(E_all, S_all)

# Visualize
fig = analyzer.plot_residuals_by_state(log_E, residuals, state_labels)
fig.savefig('results/residuals_analysis_all_subjects.png')
```

---

## References

- Residual diagnostics: https://en.wikipedia.org/wiki/Regression_residual
- Q-Q plots: https://en.wikipedia.org/wiki/Q%E2%80%93Q_plot
- Heteroscedasticity: https://en.wikipedia.org/wiki/Heteroscedasticity
- Model assumptions: https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html

---

**Ready to analyze your MSSV residuals!** ✅
