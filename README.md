# MSSV EEG Analysis Pipeline with M365 Copilot Integration

A comprehensive Python pipeline for analyzing the Mouse Sleep Staging Validation (MSSV) dataset and integrating results with Microsoft 365 Copilot.

## Dataset

**Mouse Sleep Staging Validation (MSSV)** - OpenNeuro ds006366
- **Subjects**: 92 healthy mice
- **Labs**: 5 international research centers
- **Recording Type**: EEG + EMG
- **Sampling Rate**: 128 Hz
- **Format**: BIDS-compliant EDF files
- **DOI**: https://doi.org/10.18112/openneuro.ds006366

## Features

### EEG Analysis
- ✅ **Shannon Entropy (E)** - Signal complexity measure
- ✅ **Mean Coherence (S)** - Inter-channel synchronization
- ✅ **Regularity Index (Re_g)** - Formula: `Re_g = E² / (S + ε)`
- ✅ **Approximate Entropy** - Temporal pattern complexity
- ✅ **Sample Entropy** - Model-free complexity measure
- ✅ **Spectral Analysis** - Delta, Theta, Alpha, Beta, Gamma bands
- ✅ **Sleep State Classification** - Wake/REM, Light Sleep, Deep Sleep
- ✅ **Channel-wise Metrics** - Per-electrode analysis

### Output Formats
- **JSON** - Complete detailed results with metadata
- **CSV** - Summary statistics for spreadsheet analysis
- **Copilot Grounding** - Formatted for M365 integration

### M365 Copilot Integration
- Azure AD authentication
- Grounding data generation
- Knowledge base upload capability
- Microsoft Graph API integration

## Installation

### Requirements
- Python 3.8+
- pip or conda

### Setup

```bash
# Clone repository
git clone https://github.com/dinnin-wq/copilot-mssv-analysis.git
cd copilot-mssv-analysis

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Analysis

```python
from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer

# Initialize analyzer
analyzer = MSSVEEGAnalyzer(
    dataset_root="/path/to/ds006366",
    fs=128
)

# Analyze all subjects
results = analyzer.analyze_all_subjects()

# Export results
analyzer.export_to_json('mssv_results.json')
df = analyzer.export_to_dataframe()
df.to_csv('mssv_results.csv', index=False)
```

### M365 Copilot Integration

```python
from mssv_eeg_analysis_pipeline import M365CopilotConnector

# Initialize connector
copilot = M365CopilotConnector(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

# Get summary statistics
summary = analyzer.generate_summary_statistics()

# Create grounding data
grounding = copilot.create_copilot_grounding(summary)

# Authenticate and upload
if copilot.authenticate():
    copilot.upload_to_copilot(grounding)
```

## Metrics Explained

### Shannon Entropy (E)
- Measures the randomness/complexity of the EEG signal
- Higher values indicate more chaotic, less regular signals
- Associated with wake/REM states

### Mean Coherence (S)
- Measures synchronization between EEG channels
- Higher values indicate channels firing in sync
- Associated with coordinated brain activity

### Regularity Index (Re_g)
- **Formula**: `Re_g = E² / (S + 10⁻⁸)`
- Differentiates sleep states by combining entropy and connectivity
- **High Re_g** (>2.0): Wake/REM state
- **Medium Re_g** (1.0-2.0): Light sleep (N1/N2)
- **Low Re_g** (<1.0): Deep sleep (N3)

### Approximate Entropy (ApEn)
- Quantifies the regularity of patterns in time series
- Lower values indicate more regular/predictable signals
- Useful for detecting sleep depth

### Sample Entropy (SampEn)
- Similar to ApEn but model-free
- More sensitive to time series length
- Better for comparative analysis

## Output Examples

### Summary Statistics
```json
{
  "total_subjects": 92,
  "entropy": {
    "mean": 2.342,
    "std": 0.456,
    "min": 1.234,
    "max": 3.567
  },
  "connectivity": {
    "mean": 0.456,
    "std": 0.123,
    "min": 0.234,
    "max": 0.789
  },
  "regularity_index": {
    "mean": 1.234,
    "std": 0.567,
    "min": 0.234,
    "max": 4.567
  },
  "sleep_state_distribution": {
    "Wake/REM": 28,
    "Light Sleep": 34,
    "Deep Sleep": 30
  }
}
```

### Per-Subject Results
```json
{
  "subject_id": "sub-001",
  "entropy": 2.456,
  "connectivity": 0.512,
  "regularity_index": 1.245,
  "approx_entropy": 0.834,
  "sample_entropy": 0.923,
  "predicted_sleep_state": "Light Sleep (N1/N2)",
  "confidence": 0.75,
  "spectral_metrics": {
    "delta": {"entropy": 1.234, "regularity_index": 0.456},
    "theta": {"entropy": 1.456, "regularity_index": 0.567},
    "alpha": {"entropy": 1.567, "regularity_index": 0.678},
    "beta": {"entropy": 1.789, "regularity_index": 0.789},
    "gamma": {"entropy": 2.012, "regularity_index": 0.901}
  }
}
```

## M365 Copilot Setup

See `copilot_integration_guide.md` for detailed instructions on:
1. Creating Azure AD application
2. Configuring API permissions
3. Setting up authentication
4. Uploading grounding data
5. Creating Copilot prompts

## Dataset Access

The MSSV dataset is publicly available on OpenNeuro:
- **URL**: https://openneuro.org/datasets/ds006366
- **Download**: Use `datalad get` or direct download
- **Citation**: See dataset page for citation details

## References

- MSSV Paper: https://doi.org/10.1093/sleepadvances/zpaf025
- BIDS Standard: https://bids-standard.github.io/
- MNE-Python: https://mne.tools/
- Microsoft Graph API: https://docs.microsoft.com/en-us/graph/

## License

This project is licensed under the CC0 license (same as the dataset).

## Authors

- EEG Analysis System
- Based on MSSV dataset by Rose et al., 2024

## Support

For issues or questions:
1. Check the dataset documentation: https://openneuro.org/datasets/ds006366
2. Review the M365 Copilot guide: `copilot_integration_guide.md`
3. See code examples in test files

## Citation

If you use this pipeline in research, please cite:

```bibtex
@software{mssv_copilot_2025,
  title={MSSV EEG Analysis Pipeline with M365 Copilot Integration},
  author={EEG Analysis System},
  year={2025},
  url={https://github.com/dinnin-wq/copilot-mssv-analysis}
}

@dataset{rose2024mssv,
  title={Mouse Sleep Staging Validation dataset (MSSV)},
  author={Rose, Laura and others},
  journal={Sleep Advances},
  year={2024},
  doi={10.1093/sleepadvances/zpaf025}
}
```
