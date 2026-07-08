import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer, M365CopilotConnector

load_dotenv()

print("\n" + "="*80)
print("MSSV EEG ANALYSIS PIPELINE EXECUTION")
print("="*80)

# Get configuration
dataset_root = os.getenv('DATASET_ROOT')
fs = int(os.getenv('SAMPLING_FREQUENCY', 128))
max_subjects = os.getenv('MAX_SUBJECTS')
enable_copilot = os.getenv('ENABLE_COPILOT', 'False').lower() == 'true'

if max_subjects and max_subjects.lower() != 'none':
    max_subjects = int(max_subjects)
else:
    max_subjects = None

if not dataset_root or not Path(dataset_root).exists():
    print(f"✗ Dataset path not found: {dataset_root}")
    sys.exit(1)

print(f"\nConfiguration:")
print(f"  Dataset Root: {dataset_root}")
print(f"  Sampling Frequency: {fs} Hz")
print(f"  Max Subjects: {max_subjects if max_subjects else 'All'}")
print(f"  Enable Copilot: {enable_copilot}")

# Initialize analyzer
print(f"\n{'='*80}")
print("1. INITIALIZING ANALYZER")
print(f"{'='*80}")

analyzer = MSSVEEGAnalyzer(
    dataset_root=dataset_root,
    fs=fs
)

subjects = analyzer.get_subject_list()
print(f"✓ Found {len(subjects)} subjects in dataset")

# Run analysis
print(f"\n{'='*80}")
print("2. ANALYZING SUBJECTS")
print(f"{'='*80}")

results = analyzer.analyze_all_subjects(max_subjects=max_subjects)
print(f"\n✓ Analysis complete: {len(results)} subjects processed")

# Export results
print(f"\n{'='*80}")
print("3. EXPORTING RESULTS")
print(f"{'='*80}")

# Create results directory
results_dir = Path('results')
results_dir.mkdir(exist_ok=True)

# Export JSON
json_file = results_dir / 'mssv_analysis_results.json'
analyzer.export_to_json(str(json_file))
print(f"✓ JSON export: {json_file}")

# Export CSV
csv_file = results_dir / 'mssv_analysis_results.csv'
df = analyzer.export_to_dataframe()
df.to_csv(csv_file, index=False)
print(f"✓ CSV export: {csv_file}")

# Generate summary
print(f"\n{'='*80}")
print("4. SUMMARY STATISTICS")
print(f"{'='*80}")

summary = analyzer.generate_summary_statistics()
print(json.dumps(summary, indent=2))

# M365 Copilot Integration
if enable_copilot:
    print(f"\n{'='*80}")
    print("5. M365 COPILOT INTEGRATION")
    print(f"{'='*80}")
    
    tenant_id = os.getenv('AZURE_TENANT_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    
    if not all([tenant_id, client_id, client_secret]):
        print("✗ M365 credentials not configured in .env file")
    else:
        print("Initializing M365 Copilot connector...")
        copilot = M365CopilotConnector(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Create grounding data
        print("Creating copilot grounding data...")
        grounding = copilot.create_copilot_grounding(summary)
        
        # Save grounding
        grounding_file = results_dir / 'copilot_grounding.json'
        with open(grounding_file, 'w') as f:
            json.dump(grounding, f, indent=2, default=str)
        print(f"✓ Grounding data saved: {grounding_file}")
        
        # Authenticate and upload
        print("\nAttempting to authenticate with M365...")
        if copilot.authenticate():
            print("✓ Authentication successful")
            print("Uploading grounding data to Copilot...")
            if copilot.upload_to_copilot(grounding):
                print("✓ Successfully uploaded to M365 Copilot")
            else:
                print("✗ Upload failed. See logs for details.")
        else:
            print("✗ Authentication failed. Check credentials in .env file")
else:
    print(f"\n{'='*80}")
    print("5. M365 COPILOT INTEGRATION (SKIPPED)")
    print(f"{'='*80}")
    print("Copilot integration is disabled.")
    print("To enable, set ENABLE_COPILOT=True in .env file")

print(f"\n{'='*80}")
print("ANALYSIS PIPELINE COMPLETE ✓")
print(f"{'='*80}")
print(f"\nResults saved to: {results_dir.absolute()}")
