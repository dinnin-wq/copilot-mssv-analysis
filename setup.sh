#!/bin/bash
# Setup and execution script for MSSV EEG Analysis Pipeline

set -e

echo "====================================================================="
echo "MSSV EEG ANALYSIS PIPELINE - AUTOMATED SETUP"
echo "====================================================================="

# Step 1: Clone Repository
echo ""
echo "[STEP 1/5] CLONING REPOSITORY..."
echo "---------------------------------------------------------------------"

if [ -d "copilot-mssv-analysis" ]; then
    echo "✓ Repository already exists. Updating..."
    cd copilot-mssv-analysis
    git pull origin main
    cd ..
else
    echo "Cloning from GitHub..."
    git clone https://github.com/dinnin-wq/copilot-mssv-analysis.git
fi

cd copilot-mssv-analysis
echo "✓ Repository ready at: $(pwd)"

# Step 2: Install Dependencies
echo ""
echo "[STEP 2/5] INSTALLING DEPENDENCIES..."
echo "---------------------------------------------------------------------"

if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "✗ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

echo "Installing pip packages..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

echo "✓ Dependencies installed successfully"

# Step 3: Download MSSV Dataset
echo ""
echo "[STEP 3/5] DOWNLOADING MSSV DATASET..."
echo "---------------------------------------------------------------------"
echo "The MSSV dataset is ~100GB. You have 2 options:"
echo ""
echo "Option A: Use datalad (recommended)"
echo "  1. Install datalad: pip install datalad"
echo "  2. Run: datalad clone https://github.com/OpenNeuroDatasets/ds006366.git"
echo ""
echo "Option B: Download from OpenNeuro directly"
echo "  Visit: https://openneuro.org/datasets/ds006366"
echo "  Click 'Download' and follow instructions"
echo ""

read -p "Have you downloaded the dataset? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter the path to your MSSV dataset: " DATASET_PATH
    
    if [ -d "$DATASET_PATH" ]; then
        echo "✓ Dataset found at: $DATASET_PATH"
        DATASET_PATH=$(cd "$DATASET_PATH" && pwd)
    else
        echo "✗ Dataset path not found. Exiting."
        exit 1
    fi
else
    echo "Please download the dataset and run this script again."
    exit 1
fi

# Step 4: Configure Environment
echo ""
echo "[STEP 4/5] CONFIGURING ENVIRONMENT..."
echo "---------------------------------------------------------------------"

cat > .env << EOF
# MSSV Dataset Configuration
DATASET_ROOT=$DATASET_PATH
SAMPLING_FREQUENCY=128

# M365 Copilot Configuration (optional)
# Get these from Azure AD app registration
AZURE_TENANT_ID=your_tenant_id_here
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here

# Analysis Configuration
MAX_SUBJECTS=None  # Set to number to limit (e.g., 5 for testing)
ENABLE_COPILOT=False  # Set to True after configuring Azure credentials
EOF

echo "✓ Environment file created: .env"
echo ""
echo "IMPORTANT: Edit .env file to add your Azure credentials for M365 Copilot integration"

# Step 5: Run Analysis
echo ""
echo "[STEP 5/5] RUNNING ANALYSIS..."
echo "---------------------------------------------------------------------"

echo "Running analysis..."
$PYTHON_CMD run_analysis.py

echo ""
echo "====================================================================="
echo "✓ SETUP AND ANALYSIS COMPLETE"
echo "====================================================================="
echo ""
echo "Next steps:"
echo "  1. Review results in ./results/ directory"
echo "  2. For M365 Copilot integration:"
echo "     - Edit .env with your Azure AD credentials"
echo "     - Set ENABLE_COPILOT=True"
echo "     - Run: python run_analysis.py"
echo "  3. See README.md for detailed documentation"
echo ""
