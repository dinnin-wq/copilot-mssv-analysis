# M365 Copilot Integration Guide

Step-by-step guide to integrate MSSV EEG analysis with Microsoft 365 Copilot.

## Prerequisites

- Microsoft 365 Business subscription
- Azure AD tenant access
- Application registration permissions
- Python 3.8+ with required packages

## Step 1: Create Azure AD Application

### 1.1 Register Application in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory → App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: `MSSV EEG Analysis`
   - **Supported account types**: Single tenant
   - **Redirect URI**: Web → `http://localhost:8000/callback`
5. Click **Register**

### 1.2 Save Application Credentials

Note the following values (you'll need them later):
- **Application (client) ID**
- **Directory (tenant) ID**

### 1.3 Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Set expiration (recommended: 24 months)
4. Copy the **Value** (only shown once!)
5. Store securely (use `.env` file)

## Step 2: Configure API Permissions

### 2.1 Add Permissions

1. In app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions**
5. Add the following permissions:
   - `Directory.Read.All` - Read directory data
   - `User.Read.All` - Read user profiles
   - `Sites.ReadWrite.All` - Read/write SharePoint sites

### 2.2 Grant Admin Consent

1. Click **Grant admin consent for [Organization]**
2. Confirm the consent

## Step 3: Configure Environment Variables

### 3.1 Create `.env` File

```bash
# .env file
AZURE_TENANT_ID=your_tenant_id_here
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
DATASET_ROOT=/path/to/ds006366
```

### 3.2 Load Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

tenant_id = os.getenv('AZURE_TENANT_ID')
client_id = os.getenv('AZURE_CLIENT_ID')
client_secret = os.getenv('AZURE_CLIENT_SECRET')
```

## Step 4: Set Up Copilot Grounding Data

### 4.1 Generate Grounding Data

```python
from mssv_eeg_analysis_pipeline import MSSVEEGAnalyzer, M365CopilotConnector
import os
import json

# Initialize analyzer
analyzer = MSSVEEGAnalyzer(
    dataset_root=os.getenv('DATASET_ROOT'),
    fs=128
)

# Analyze all subjects
results = analyzer.analyze_all_subjects()

# Get summary statistics
summary = analyzer.generate_summary_statistics()

# Initialize Copilot connector
copilot = M365CopilotConnector(
    tenant_id=os.getenv('AZURE_TENANT_ID'),
    client_id=os.getenv('AZURE_CLIENT_ID'),
    client_secret=os.getenv('AZURE_CLIENT_SECRET')
)

# Create grounding data
grounding = copilot.create_copilot_grounding(summary)

# Save grounding data
with open('copilot_grounding.json', 'w') as f:
    json.dump(grounding, f, indent=2, default=str)

print("✓ Grounding data saved to copilot_grounding.json")
```

### 4.2 Upload Grounding Data

```python
# Authenticate with Azure AD
if copilot.authenticate():
    print("✓ Authenticated with M365")
    
    # Upload to Copilot
    if copilot.upload_to_copilot(grounding):
        print("✓ Successfully uploaded grounding data")
    else:
        print("✗ Upload failed")
else:
    print("✗ Authentication failed")
```

## Step 5: Create Copilot Prompts

### 5.1 Example Prompts

Once grounding data is uploaded, you can query Copilot with prompts like:

**Prompt 1: Dataset Overview**
```
What is the Mouse Sleep Staging Validation (MSSV) dataset and what does it contain?
```

**Prompt 2: Metric Interpretation**
```
Explain the regularity index (Re_g) metric and how it's used to classify sleep states.
```

**Prompt 3: Analysis Summary**
```
Summarize the key findings from the MSSV EEG analysis across all 92 subjects.
```

**Prompt 4: Statistical Overview**
```
What are the mean and standard deviation values for entropy, connectivity, and regularity index
across all subjects in the MSSV dataset?
```

**Prompt 5: Sleep State Distribution**
```
How many mice in the MSSV dataset were classified as Wake/REM, Light Sleep, and Deep Sleep?
```

### 5.2 Advanced Prompts

**Prompt 6: Comparative Analysis**
```
Compare the spectral characteristics (delta, theta, alpha, beta, gamma bands) across different
sleep states in the MSSV analysis.
```

**Prompt 7: Research Context**
```
What is the significance of the MSSV dataset in sleep neuroscience research?
```

## Step 6: Monitor and Troubleshooting

### 6.1 Check Grounding Data Upload

```python
import requests

headers = {
    'Authorization': f'Bearer {copilot.access_token}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://graph.microsoft.com/v1.0/me/copilot/groundingData',
    headers=headers
)

if response.status_code == 200:
    print("✓ Grounding data is accessible")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"✗ Error: {response.status_code}")
```

### 6.2 Common Issues

**Issue: Authentication Failed**
- Verify credentials in `.env` file
- Check that app registration has necessary permissions
- Ensure client secret hasn't expired

**Issue: Upload Failed**
- Confirm grounding data is valid JSON
- Check API permissions are granted
- Verify endpoint URL is correct

**Issue: Copilot Not Using Grounding Data**
- Verify upload was successful
- Check data format matches Copilot requirements
- Ensure data is accessible by your user account

## Step 7: Maintenance

### 7.1 Refresh Grounding Data

Run the analysis pipeline periodically to update grounding data:

```bash
# Run daily/weekly analysis
python mssv_eeg_analysis_pipeline.py --mode generate_grounding
```

### 7.2 Monitor Usage

Track Copilot queries and interactions:

```python
# Add logging to track Copilot usage
import logging

logger = logging.getLogger('copilot_usage')
logger.info(f"User: {user_id}, Query: {query}, Timestamp: {timestamp}")
```

### 7.3 Update API Permissions

Review and update API permissions annually:
- Check for deprecated permissions
- Add new permissions as needed
- Remove unused permissions

## Resources

- [Azure AD Documentation](https://docs.microsoft.com/en-us/azure/active-directory/)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/)
- [Copilot in M365](https://www.microsoft.com/en-us/microsoft-365/copilot)
- [MSSV Dataset](https://openneuro.org/datasets/ds006366)

## Support

For issues with:
- **Azure AD**: See Azure AD documentation
- **M365 Copilot**: Contact Microsoft Support
- **MSSV Analysis**: Check dataset documentation
- **Integration**: Review this guide and code examples
