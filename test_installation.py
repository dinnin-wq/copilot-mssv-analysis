# Quick test to verify installation and setup
import sys
import os
from pathlib import Path

print("\n" + "="*80)
print("MSSV EEG ANALYSIS PIPELINE - INSTALLATION TEST")
print("="*80)

# Test 1: Check Python version
print("\n[TEST 1] Python Version")
print("-" * 80)
python_version = sys.version_info
if python_version.major >= 3 and python_version.minor >= 8:
    print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
else:
    print(f"✗ Python {python_version.major}.{python_version.minor} - FAILED (requires 3.8+)")
    sys.exit(1)

# Test 2: Check required packages
print("\n[TEST 2] Required Packages")
print("-" * 80)

required_packages = [
    ('numpy', 'NumPy'),
    ('pandas', 'Pandas'),
    ('scipy', 'SciPy'),
    ('sklearn', 'Scikit-learn'),
    ('mne', 'MNE-Python'),
    ('matplotlib', 'Matplotlib'),
    ('requests', 'Requests'),
    ('dotenv', 'python-dotenv'),
]

for package, name in required_packages:
    try:
        __import__(package)
        print(f"✓ {name} - OK")
    except ImportError:
        print(f"✗ {name} - MISSING")
        sys.exit(1)

# Test 3: Check repository structure
print("\n[TEST 3] Repository Structure")
print("-" * 80)

required_files = [
    'mssv_eeg_analysis_pipeline.py',
    'requirements.txt',
    'README.md',
    'copilot_integration_guide.md',
    'run_analysis.py',
]

for file in required_files:
    if Path(file).exists():
        print(f"✓ {file} - OK")
    else:
        print(f"✗ {file} - MISSING")
        sys.exit(1)

# Test 4: Check .env file
print("\n[TEST 4] Configuration")
print("-" * 80)

if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()
    dataset_root = os.getenv('DATASET_ROOT')
    if dataset_root:
        if Path(dataset_root).exists():
            print(f"✓ Dataset found: {dataset_root}")
        else:
            print(f"✗ Dataset not found: {dataset_root}")
            print("   Please ensure DATASET_ROOT in .env points to valid ds006366 directory")
    else:
        print("✗ DATASET_ROOT not configured in .env")
else:
    print("✗ .env file not found")
    print("   Please run setup.sh (Linux/Mac) or setup.bat (Windows)")

# Test 5: Verify core classes
print("\n[TEST 5] Core Classes")
print("-" * 80)

try:
    from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer, M365CopilotConnector
    print("✓ MSSVEEGAnalyzer - OK")
    print("✓ M365CopilotConnector - OK")
except ImportError as e:
    print(f"✗ Failed to import classes: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✓ ALL TESTS PASSED - Installation is complete!")
print("="*80)

print("\nNext steps:")
print("  1. Ensure DATASET_ROOT in .env points to your ds006366 directory")
print("  2. Run: python run_analysis.py")
print("  3. For M365 integration, configure Azure credentials in .env")
print()
