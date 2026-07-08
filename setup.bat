@echo off
REM Setup and execution script for MSSV EEG Analysis Pipeline (Windows)

echo.
echo =====================================================================
echo MSSV EEG ANALYSIS PIPELINE - AUTOMATED SETUP
echo =====================================================================

REM Step 1: Clone Repository
echo.
echo [STEP 1/5] CLONING REPOSITORY...
echo ---------------------------------------------------------------------

if exist copilot-mssv-analysis (
    echo Repository already exists. Updating...
    cd copilot-mssv-analysis
    git pull origin main
    cd ..
) else (
    echo Cloning from GitHub...
    git clone https://github.com/dinnin-wq/copilot-mssv-analysis.git
)

cd copilot-mssv-analysis
echo Repository ready at: %cd%

REM Step 2: Install Dependencies
echo.
echo [STEP 2/5] INSTALLING DEPENDENCIES...
echo ---------------------------------------------------------------------

echo Installing pip packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Dependencies installed successfully

REM Step 3: Download MSSV Dataset
echo.
echo [STEP 3/5] DOWNLOADING MSSV DATASET...
echo ---------------------------------------------------------------------
echo The MSSV dataset is ~100GB. You have 2 options:
echo.
echo Option A: Use datalad (recommended)
echo   1. Install datalad: pip install datalad
echo   2. Run: datalad clone https://github.com/OpenNeuroDatasets/ds006366.git
echo.
echo Option B: Download from OpenNeuro directly
echo   Visit: https://openneuro.org/datasets/ds006366
echo   Click 'Download' and follow instructions
echo.

set /p DATASET_PATH="Enter the path to your MSSV dataset: "

if not exist "%DATASET_PATH%" (
    echo Dataset path not found. Exiting.
    exit /b 1
)

echo Dataset found at: %DATASET_PATH%

REM Step 4: Configure Environment
echo.
echo [STEP 4/5] CONFIGURING ENVIRONMENT...
echo ---------------------------------------------------------------------

REM Create .env file
(
    echo # MSSV Dataset Configuration
    echo DATASET_ROOT=%DATASET_PATH%
    echo SAMPLING_FREQUENCY=128
    echo.
    echo # M365 Copilot Configuration ^(optional^)
    echo # Get these from Azure AD app registration
    echo AZURE_TENANT_ID=your_tenant_id_here
    echo AZURE_CLIENT_ID=your_client_id_here
    echo AZURE_CLIENT_SECRET=your_client_secret_here
    echo.
    echo # Analysis Configuration
    echo MAX_SUBJECTS=None
    echo ENABLE_COPILOT=False
) > .env

echo Environment file created: .env
echo.
echo IMPORTANT: Edit .env file to add your Azure credentials for M365 Copilot integration

REM Step 5: Run Analysis
echo.
echo [STEP 5/5] RUNNING ANALYSIS...
echo ---------------------------------------------------------------------

python run_analysis.py

echo.
echo =====================================================================
echo SETUP AND ANALYSIS COMPLETE ✓
echo =====================================================================
echo.
echo Next steps:
echo   1. Review results in .\results\ directory
echo   2. For M365 Copilot integration:
echo      - Edit .env with your Azure AD credentials
echo      - Set ENABLE_COPILOT=True
echo      - Run: python run_analysis.py
echo   3. See README.md for detailed documentation
echo.
pause
