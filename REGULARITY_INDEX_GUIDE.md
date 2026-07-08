# Regularity Index (Re_g) Analysis Examples

This module provides comprehensive tools for analyzing the regularity index (Re_g) metric across EEG data.

## Formula

```
Re_g = E² / (S + ε)

Where:
  E   = Shannon entropy (signal complexity)
  S   = Mean coherence (signal synchronization)
  ε   = Small epsilon (1e-8) to avoid division by zero
```

## Key Concepts

### Entropy (E)
- **Measures**: Signal complexity/randomness
- **Range**: 0-5 (typically 1-4 for EEG)
- **High E**: Complex, chaotic signal (Wake/REM)
- **Low E**: Regular, predictable signal (Deep Sleep)

### Connectivity (S)
- **Measures**: Channel synchronization (mean coherence)
- **Range**: 0-1
- **High S**: Channels firing in sync
- **Low S**: Independent channel activity

### Regularity Index (Re_g)
- **Formula**: E² / (S + ε)
- **High Re_g (>2.0)**: Complex + low sync → Wake/REM
- **Medium Re_g (1.0-2.0)**: Moderate complexity → Light Sleep
- **Low Re_g (<1.0)**: Simple + high sync → Deep Sleep

## Usage

### 1. Basic Usage

```python
from regularity_index_analysis import RegularityIndexAnalyzer
import numpy as np

# Create analyzer
analyzer = RegularityIndexAnalyzer(fs=128)

# Your EEG data (n_channels x n_samples)
data = np.random.randn(4, 3840)  # 4 channels, 30 seconds at 128 Hz

# Compute regularity index
E_vals = analyzer.compute_entropy_values(data)
S_vals = analyzer.compute_connectivity_values(data)
Re_g_vals = analyzer.compute_regularity_index(E_vals, S_vals)

print(f"Entropy per channel: {E_vals}")
print(f"Connectivity per channel: {S_vals}")
print(f"Regularity Index per channel: {Re_g_vals}")
```

### 2. Global Metrics

```python
# Compute all metrics at once
metrics = analyzer.compute_all_metrics(data)

print(f"Global Entropy: {metrics['entropy_global']:.4f}")
print(f"Global Connectivity: {metrics['connectivity_global']:.4f}")
print(f"Global Re_g: {metrics['regularity_index_global']:.4f}")
print(f"Mean Re_g per channel: {metrics['mean_regularity_index']:.4f}")
print(f"Std Re_g per channel: {metrics['std_regularity_index']:.4f}")
```

### 3. Sleep State Classification

```python
# Per-channel classification
sleep_states = analyzer.classify_sleep_state_per_channel(Re_g_vals, E_vals)
for ch, (state, confidence) in enumerate(sleep_states):
    print(f"Channel {ch}: {state} ({confidence:.2%})")

# Global classification
state, conf = analyzer.classify_sleep_state_global(
    metrics['regularity_index_global'],
    metrics['entropy_global'],
    metrics['connectivity_global']
)
print(f"Sleep State: {state} ({conf:.2%})")
```

### 4. Time-Windowed Analysis

```python
# Analyze regularity index over time
windowed_df = analyzer.compute_time_windowed_reg(
    data,
    window_sec=4.0,    # 4-second windows
    overlap=0.5        # 50% overlap
)

print(windowed_df.head())
# Shows: time_sec, entropy_global, connectivity_global, regularity_index_global
```

### 5. Visualization

```python
import matplotlib.pyplot as plt

# Create visualizations
fig = analyzer.visualize_regularity_index(
    Re_g_vals,
    E_vals,
    S_vals,
    channel_names=['EEG1', 'EEG2', 'EEG3', 'EEG4']
)

plt.savefig('regularity_analysis.png')
plt.show()
```

### 6. Statistical Summary

```python
# Get statistical summary
stats = analyzer.compute_statistics(Re_g_vals)

print(f"Mean: {stats['mean']:.4f}")
print(f"Std: {stats['std']:.4f}")
print(f"Min: {stats['min']:.4f}")
print(f"Max: {stats['max']:.4f}")
print(f"Skewness: {stats['skewness']:.4f}")
print(f"Kurtosis: {stats['kurtosis']:.4f}")
```

## Output Interpretation

### Regularity Index Classification

```
Re_g > 2.0 AND E > 2.5
  ├─ Interpretation: High complexity, low synchronization
  ├─ Sleep State: Wake/REM (Confidence: 70%)
  └─ Characteristics: Active, desynchronized brain

1.0 < Re_g ≤ 2.0 AND 2.0 < E ≤ 2.5
  ├─ Interpretation: Moderate complexity, partial sync
  ├─ Sleep State: Light Sleep (N1/N2) (Confidence: 75%)
  └─ Characteristics: Transitional state

Re_g ≤ 1.0 AND E ≤ 2.0
  ├─ Interpretation: Low complexity, high synchronization
  ├─ Sleep State: Deep Sleep (N3) (Confidence: 80%)
  └─ Characteristics: Synchronized, organized activity

Otherwise:
  ├─ Interpretation: Ambiguous combination
  ├─ Sleep State: Undetermined (Confidence: 50%)
  └─ Note: May require additional context
```

## Integration with MSSV Pipeline

This module integrates with `mssv_eeg_analysis_pipeline.py`:

```python
from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer
from regularity_index_analysis import RegularityIndexAnalyzer

# Load and analyze MSSV data
mssv_analyzer = MSSVEEGAnalyzer(dataset_root='/path/to/ds006366')
results = mssv_analyzer.analyze_all_subjects(max_subjects=5)

# Deep-dive into regularity index
reg_analyzer = RegularityIndexAnalyzer(fs=128)

for result in results:
    # Extract metrics
    E = result.entropy
    S = result.connectivity
    Re_g = result.regularity_index
    
    # Get detailed analysis
    print(f"Subject: {result.subject_id}")
    print(f"  Re_g = {E:.4f}² / {S:.4f} = {Re_g:.4f}")
    print(f"  Sleep State: {result.predicted_sleep_state}")
```

## References

- Shannon Entropy: https://en.wikipedia.org/wiki/Entropy_(information_theory)
- Coherence: https://en.wikipedia.org/wiki/Coherence_(signal_processing)
- MSSV Dataset: https://doi.org/10.1093/sleepadvances/zpaf025
- EEG Analysis: https://mne.tools/
