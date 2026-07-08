# Regularity Index Visualization Guide

Comprehensive visualization tools for Re_g analysis with focus on sleep state classification.

## Core Visualizations

### 1. Re_g with Threshold Lines

```python
viz = RegularityIndexVisualizer()
fig = viz.plot_re_g_with_threshold(Re_g_vals, channel_names)
plt.savefig('re_g_thresholds.png')
```

**Features:**
- Line plot of Re_g values per channel
- Horizontal threshold lines:
  - Re_g = 1.0 (Deep Sleep boundary)
  - Re_g = 2.0 (Light Sleep boundary)
- Background regions colored by sleep state
- Value labels on each point

**Output:**
```
Chan 0: Re_g=9.8  ─ Wake/REM
Chan 1: Re_g=8.2  ─ Wake/REM
Chan 2: Re_g=1.5  ─ Light Sleep
Chan 3: Re_g=0.8  ─ Deep Sleep
```

---

### 2. Re_g Distribution

```python
fig = viz.plot_re_g_distribution(Re_g_vals)
plt.savefig('re_g_distribution.png')
```

**Features:**
- Histogram with kernel density estimation
- Mean and median lines
- Sleep state threshold lines
- Statistical summary

---

### 3. E, S, Re_g Comparison

```python
fig = viz.plot_re_g_vs_entropy_connectivity(
    Re_g_vals, E_vals, S_vals, channel_names
)
plt.savefig('e_s_reg_comparison.png')
```

**3-panel visualization:**
- Left: Entropy (E) per channel
- Middle: Connectivity (S) per channel
- Right: Regularity Index (Re_g) with formula overlay

---

### 4. Time Series

```python
fig = viz.plot_re_g_time_series(time_sec, Re_g_time)
plt.savefig('re_g_timeseries.png')
```

**Features:**
- Re_g values over time
- Colored regions for sleep states
- Tracks transitions between states

**Example:**
```
Time 0-10s:   Re_g ≈ 2.5  ─ Wake/REM
Time 10-30s:  Re_g ≈ 1.5  ─ Light Sleep → Deep Sleep
Time 30-60s:  Re_g ≈ 0.9  ─ Deep Sleep
```

---

### 5. Sleep State Regions

```python
fig = viz.plot_re_g_sleep_state_regions(Re_g_vals, E_vals, channel_names)
plt.savefig('sleep_state_regions.png')
```

**Features:**
- Bars colored by predicted sleep state
- Sleep state label in each bar
- Re_g value displayed
- Threshold lines

**Color Coding:**
- 🟢 Green: Deep Sleep (Re_g < 1.0)
- 🟡 Yellow: Light Sleep (1.0 < Re_g < 2.0)
- 🔴 Red: Wake/REM (Re_g > 2.0)
- ⚪ Gray: Undetermined

---

### 6. Subject Comparison

```python
fig = viz.plot_re_g_comparison(
    subjects=['sub-001', 'sub-002', 'sub-003'],
    re_g_means=[1.2, 1.8, 2.3],
    re_g_stds=[0.3, 0.4, 0.35]
)
plt.savefig('subject_comparison.png')
```

**Features:**
- Mean Re_g per subject
- Error bars (±1 std)
- Sleep state thresholds

---

## Usage Examples

### Complete Workflow

```python
from regularity_index_visualization import RegularityIndexVisualizer
from regularity_index_analysis import RegularityIndexAnalyzer
import numpy as np

# Load/simulate EEG data
data = np.random.randn(4, 3840)  # 4 channels, 30 seconds

# Compute metrics
analyzer = RegularityIndexAnalyzer(fs=128)
E_vals = analyzer.compute_entropy_values(data)
S_vals = analyzer.compute_connectivity_values(data)
Re_g_vals = analyzer.compute_regularity_index(E_vals, S_vals)

# Visualize
viz = RegularityIndexVisualizer()

# Create multiple plots
figs = [
    viz.plot_re_g_with_threshold(Re_g_vals),
    viz.plot_re_g_distribution(Re_g_vals),
    viz.plot_re_g_vs_entropy_connectivity(Re_g_vals, E_vals, S_vals),
    viz.plot_re_g_sleep_state_regions(Re_g_vals, E_vals)
]

# Save all
for i, fig in enumerate(figs):
    fig.savefig(f'plot_{i+1}.png', dpi=150)
```

### Custom Styling

```python
import matplotlib.pyplot as plt

viz = RegularityIndexVisualizer()

# Customize colors
viz.colors['wake_rem'] = '#FF0000'     # Custom red
viz.colors['light_sleep'] = '#FFFF00'  # Custom yellow
viz.colors['deep_sleep'] = '#00FF00'   # Custom green

fig = viz.plot_re_g_with_threshold(Re_g_vals)
plt.show()
```

---

## Sleep State Classification Guide

### Threshold-based Classification

```
Re_g > 2.0 AND E > 2.5
  ↓
  Wake/REM
  Characteristics:
  • High entropy (signal complexity)
  • Low connectivity (desynchronized)
  • High irregularity

1.0 < Re_g ≤ 2.0 AND 2.0 < E ≤ 2.5
  ↓
  Light Sleep (N1/N2)
  Characteristics:
  • Moderate entropy
  • Moderate connectivity
  • Transitional state

Re_g ≤ 1.0 AND E ≤ 2.0
  ↓
  Deep Sleep (N3)
  Characteristics:
  • Low entropy (regular patterns)
  • High connectivity (synchronized)
  • Low irregularity
```

---

## Integration with MSSV Pipeline

```python
from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer
from regularity_index_visualization import RegularityIndexVisualizer

# Analyze MSSV subjects
mssv = MSSVEEGAnalyzer(dataset_root='/path/to/ds006366')
results = mssv.analyze_all_subjects(max_subjects=5)

# Visualize results
viz = RegularityIndexVisualizer()

for result in results:
    fig = viz.plot_re_g_sleep_state_regions(
        result.channel_metrics,
        result.entropy,
        channel_names=[f'Ch {i}' for i in range(len(result.channel_metrics))]
    )
    fig.savefig(f'subject_{result.subject_id}_analysis.png')
```

---

## Output File Examples

When running `python regularity_index_visualization.py`, generates:

```
01_re_g_with_thresholds.png       ← Main plot with threshold lines
02_re_g_distribution.png           ← Histogram + KDE
03_e_s_reg_comparison.png          ← 3-panel comparison
04_re_g_timeseries.png             ← Time-windowed analysis
05_sleep_state_regions.png         ← Color-coded sleep states
06_subject_comparison.png          ← Cross-subject analysis
```

---

## Advanced Features

### Custom Thresholds

```python
# Modify sleep state boundaries
viz.threshold_deep_sleep = 0.8      # Re_g < 0.8
viz.threshold_light_sleep = 1.8     # 0.8 < Re_g < 1.8
viz.threshold_wake_rem = 2.5        # Re_g > 2.5
```

### Batch Processing

```python
import os
from pathlib import Path

# Process all subjects
results_dir = Path('results')
results_dir.mkdir(exist_ok=True)

for subject_id in range(1, 93):  # All 92 MSSV subjects
    # Load and analyze
    data = load_subject_data(subject_id)
    metrics = compute_metrics(data)
    
    # Visualize
    fig = viz.plot_re_g_with_threshold(metrics['Re_g_vals'])
    fig.savefig(results_dir / f'sub-{subject_id:03d}_analysis.png')
    plt.close(fig)
```

---

## References

- Matplotlib documentation: https://matplotlib.org/
- Sleep stage classification: https://doi.org/10.1093/sleepadvances/zpaf025
- Regularity metrics: https://mne.tools/
