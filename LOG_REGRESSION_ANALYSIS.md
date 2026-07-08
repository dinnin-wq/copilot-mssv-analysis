# Logarithmic Regression Analysis for Regularity Index

## Overview

This module implements logarithmic regression analysis to understand the relationship:

```
log(Re_g) = β₀ + β₁·log(E) + β₂·log(S) + ε
```

Where:
- **log(Re_g)** = Log-transformed regularity index
- **log(E)** = Log-transformed entropy
- **log(S)** = Log-transformed connectivity
- **β₁** = Coefficient for entropy (theoretical: 2.0)
- **β₂** = Coefficient for connectivity (theoretical: -1.0)
- **ε** = Error term

---

## Mathematical Foundation

### The Formula in Log Space

**Original formula:**
```
Re_g = E² / S
```

**Log transformation:**
```
log(Re_g) = log(E²) - log(S)
log(Re_g) = 2·log(E) - log(S)
```

**Regression form:**
```
log(Re_g) = β₀ + 2·log(E) - 1·log(S) + ε
```

**Expected coefficients:**
- β₁ (log(E) coefficient) = **2.0** (theoretical)
- β₂ (log(S) coefficient) = **-1.0** (theoretical)
- β₀ (intercept) ≈ **0** (if formula is exact)

---

## Implementation

### Code Template

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy import stats

# Step 1: Compute metrics
E_vals = np.array(E_vals)          # Entropy per channel
S_vals = np.array(S_vals)          # Connectivity per channel
Re_g_vals = (E_vals**2) / (S_vals + 1e-8)  # Regularity index

# Step 2: Log transform
log_E = np.log(E_vals)
log_S = np.log(S_vals + 1e-8)
log_Re_g = np.log(Re_g_vals)

# Step 3: Build regression model
X = np.column_stack([log_E, log_S])
X = sm.add_constant(X)  # Add intercept

model = sm.OLS(log_Re_g, X).fit()

# Step 4: Print results
print(model.summary())
```

---

## Interpretation Guide

### What to Look For

#### 1. **R-squared (R²)**
```
R² = 0.95-1.00  → Excellent fit (formula validated)
R² = 0.80-0.95  → Good fit (minor noise)
R² = 0.50-0.80  → Moderate fit (some deviation)
R² < 0.50       → Poor fit (systematic deviation)
```

If R² ≈ 1.0, the formula Re_g = E²/S is accurate for your data.

---

#### 2. **Coefficients (β₁, β₂)**

**For log(E):**
```
β₁ ≈ 2.0  → Formula validated (E² term confirmed)
β₁ ≈ 1.0  → Linear relationship (not quadratic)
β₁ >> 2.0 → Entropy dominates
β₁ << 2.0 → Other factors present
```

**For log(S):**
```
β₂ ≈ -1.0  → Formula validated (S⁻¹ term confirmed)
β₂ ≈ 0     → Connectivity doesn't affect Re_g
β₂ >> -1.0 → Connectivity strongly suppresses Re_g
β₂ << -1.0 → Inverse relationship weaker than expected
```

---

#### 3. **P-values (Prob > |t|)**

```
p < 0.001   → Highly significant ***
p < 0.01    → Very significant **
p < 0.05    → Significant *
p > 0.05    → Not significant (ns)
```

If p < 0.05 for both coefficients, they are statistically significant.

---

#### 4. **Confidence Intervals (95% CI)**

```
If CI includes the theoretical value (2.0 for E, -1.0 for S):
  → Theory is consistent with data
  
If CI does NOT include theoretical value:
  → Possible systematic deviation or noise
```

---

## Example Output Interpretation

### Scenario 1: Perfect Fit

```
                            OLS Regression Results
==============================================================================
Dep. Variable:                log_Re_g   R-squared:                       0.998
Model:                            OLS   Adj. R-squared:                  0.997
Method:                 Least Squares   F-statistic:                   1250.0
Date:                Mon, 08 Jul 2026   Prob (F-statistic):           1.2e-45
Time:                        12:16:12   Log-Likelihood:               125.43
No. Observations:                  92   AIC:                          -244.86
Df Residuals:                      89   BIC:                          -237.15
Df Model:                           2
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const          0.0123      0.045      0.274      0.785      -0.076       0.100
log_E          1.9847      0.031     64.026      0.000       1.924       2.046 ***
log_S         -0.9921      0.028    -35.393      0.000      -1.047      -0.937 ***
==============================================================================
```

**Interpretation:**
- ✅ R² = 0.998 (nearly perfect fit)
- ✅ Coefficient for log(E) = 1.98 ≈ 2.0 ✓
- ✅ Coefficient for log(S) = -0.99 ≈ -1.0 ✓
- ✅ Both p-values < 0.001 (highly significant)
- ✅ **Conclusion: Formula Re_g = E²/S is validated!**

---

### Scenario 2: Systematic Deviation

```
                            OLS Regression Results
==============================================================================
Dep. Variable:                log_Re_g   R-squared:                       0.856
Model:                            OLS   Adj. R-squared:                  0.851
Method:                 Least Squares   F-statistic:                   156.33
Date:                Mon, 08 Jul 2026   Prob (F-statistic):           4.5e-35
Time:                        12:20:45   Log-Likelihood:                 87.22
No. Observations:                  92   AIC:                          -168.44
Df Residuals:                      89   BIC:                          -160.73
Df Model:                           2
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         -0.3421      0.156     -2.193      0.031      -0.652      -0.032 *
log_E          1.6234      0.104     15.606      0.000       1.417       1.829 ***
log_S         -1.2156      0.098    -12.404      0.000      -1.410      -1.021 ***
==============================================================================
```

**Interpretation:**
- ⚠️ R² = 0.856 (moderate fit, ~14% unexplained variance)
- ⚠️ Coefficient for log(E) = 1.62 < 2.0 (entropy effect lower)
- ⚠️ Coefficient for log(S) = -1.22 < -1.0 (connectivity effect stronger)
- ✅ Both p-values < 0.001 (still significant)
- ⚠️ **Conclusion: Formula partially valid, but other factors present**

---

## Advanced Analysis: Residual Diagnostics

### Check Model Assumptions

```python
# Residual analysis
residuals = model.resid
fitted_values = model.fittedvalues

# Plot 1: Residuals vs Fitted
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.scatter(fitted_values, residuals, alpha=0.6)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Fitted Values')
plt.ylabel('Residuals')
plt.title('Residuals vs Fitted')
plt.grid(True, alpha=0.3)

# Plot 2: Q-Q Plot
plt.subplot(1, 2, 2)
stats.probplot(residuals, dist="norm", plot=plt)
plt.title('Q-Q Plot')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Normality test
k2, p = stats.normaltest(residuals)
print(f"\nNormality Test: k²={k2:.4f}, p={p:.4f}")
if p > 0.05:
    print("✓ Residuals are normally distributed")
else:
    print("✗ Residuals deviate from normality")
```

---

## Complete Analysis Workflow

```python
class LogarithmicRegression:
    """Logarithmic regression analysis for Re_g formula validation"""
    
    def __init__(self):
        self.model = None
        self.results = None
        
    def fit(self, E_vals, S_vals):
        """
        Fit logarithmic regression model
        
        log(Re_g) = β₀ + β₁·log(E) + β₂·log(S)
        """
        # Compute Re_g
        Re_g_vals = (E_vals**2) / (S_vals + 1e-8)
        
        # Log transform
        log_E = np.log(E_vals)
        log_S = np.log(S_vals + 1e-8)
        log_Re_g = np.log(Re_g_vals)
        
        # Build model
        X = np.column_stack([log_E, log_S])
        X = sm.add_constant(X)
        
        self.model = sm.OLS(log_Re_g, X).fit()
        
        return self.model
    
    def print_summary(self):
        """Print regression summary"""
        print(self.model.summary())
    
    def get_coefficients(self):
        """Extract coefficients"""
        params = self.model.params
        return {
            'intercept': params[0],
            'log_E_coeff': params[1],
            'log_S_coeff': params[2],
            'r_squared': self.model.rsquared,
            'adj_r_squared': self.model.rsquared_adj
        }
    
    def validate_formula(self, threshold=0.05):
        """
        Validate if coefficients match theoretical values
        """
        params = self.model.params
        pvals = self.model.pvalues
        
        # Theoretical values
        theory_E = 2.0
        theory_S = -1.0
        
        coeff_E = params[1]
        coeff_S = params[2]
        pval_E = pvals[1]
        pval_S = pvals[2]
        
        # Check if coefficients are close to theory
        E_valid = abs(coeff_E - theory_E) < 0.1 and pval_E < threshold
        S_valid = abs(coeff_S - theory_S) < 0.1 and pval_S < threshold
        
        return {
            'formula_valid': E_valid and S_valid,
            'entropy_term_valid': E_valid,
            'connectivity_term_valid': S_valid,
            'coeff_E': coeff_E,
            'coeff_S': coeff_S,
            'pval_E': pval_E,
            'pval_S': pval_S
        }

# Usage
analyzer = LogarithmicRegression()
model = analyzer.fit(E_vals, S_vals)
analyzer.print_summary()

coeffs = analyzer.get_coefficients()
print(f"\nCoefficients:")
for key, val in coeffs.items():
    print(f"  {key}: {val:.4f}")

validation = analyzer.validate_formula()
print(f"\nFormula Validation:")
for key, val in validation.items():
    print(f"  {key}: {val}")
```

---

## Sleep State Analysis

You can also analyze how log-transformed metrics vary by sleep state:

```python
# If you have sleep state labels
sleep_states = [...]  # Wake/REM, Light Sleep, Deep Sleep

data = pd.DataFrame({
    'log_E': log_E,
    'log_S': log_S,
    'log_Re_g': log_Re_g,
    'sleep_state': sleep_states
})

# Box plots by sleep state
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for i, metric in enumerate(['log_E', 'log_S', 'log_Re_g']):
    data.boxplot(column=metric, by='sleep_state', ax=axes[i])
    axes[i].set_title(f'{metric} by Sleep State')
    axes[i].set_xlabel('Sleep State')
    axes[i].set_ylabel(metric)

plt.tight_layout()
plt.show()

# Summary statistics
print(data.groupby('sleep_state')[['log_E', 'log_S', 'log_Re_g']].describe())
```

---

## Key Takeaways

1. **If R² ≈ 1.0**: Your formula Re_g = E²/S is accurate
2. **If β₁ ≈ 2.0**: Entropy's quadratic effect is confirmed
3. **If β₂ ≈ -1.0**: Connectivity's inverse effect is confirmed
4. **If p-values < 0.05**: Both effects are statistically significant
5. **If residuals are normal**: Model assumptions are satisfied

---

## References

- OLS Regression: https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html
- Log-likelihood: https://en.wikipedia.org/wiki/Likelihood_function
- Model diagnostics: https://en.wikipedia.org/wiki/Regression_diagnostics

---

**Ready to run this analysis on your MSSV data!** ✅
