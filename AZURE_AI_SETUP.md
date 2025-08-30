# Azure AI Setup Guide for PDF Parsing

## Overview
This guide will help you set up Azure AI to parse PDF documents and extract financial transactions automatically.

## Prerequisites

### 1. Azure Subscription
- Active Azure subscription
- Access to create Azure OpenAI resources

### 2. Azure OpenAI Resource
You need an Azure OpenAI resource with a GPT model deployed.

## Step-by-Step Setup

### Step 1: Create Azure OpenAI Resource

1. **Go to Azure Portal**: https://portal.azure.com
2. **Create Resource**:
   - Search for "Azure OpenAI"
   - Click "Create"
   - Fill in the details:
     - **Subscription**: Your Azure subscription
     - **Resource Group**: Create new or select existing
     - **Region**: Choose a region with Azure OpenAI availability (e.g., East US, West Europe)
     - **Name**: Choose a unique name (e.g., `yourname-finance-ai`)
     - **Pricing Tier**: Standard S0

3. **Wait for Deployment**: This may take a few minutes.

### Step 2: Deploy GPT Model

1. **Navigate to Your Resource**:
   - Go to your newly created Azure OpenAI resource
   - Click on "Go to Azure OpenAI Studio" or find the "Azure OpenAI" section

2. **Create Model Deployment**:
   - Go to "Deployments" in the left sidebar
   - Click "Create new deployment"
   - Choose a model:
     - **Model**: `gpt-4` (recommended) or `gpt-3.5-turbo`
     - **Deployment Name**: `gpt-4-finance` (or your preferred name)
     - **Deployment Type**: Standard
   - Click "Create"

3. **Wait for Deployment**: This may take 10-15 minutes.

### Step 3: Get API Credentials

1. **Get API Key**:
   - In your Azure OpenAI resource
   - Go to "Keys and Endpoint" in the left sidebar
   - Copy **Key 1** (keep this secret!)

2. **Get Endpoint URL**:
   - Copy the **Endpoint** URL
   - Format: `https://your-resource-name.openai.azure.com/`

3. **Get API Version**:
   - Use: `2024-02-15-preview` (latest stable)

4. **Get Deployment Name**:
   - This is the name you chose in Step 2 (e.g., `gpt-4-finance`)

### Step 4: Configure Environment Variables

Create or update your `.env` file with the Azure AI credentials:

```bash
# Azure AI Configuration
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-finance
```

### Step 5: Test the Integration

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Test Azure AI Connection**:
```bash
python test_azure_ai.py
```

3. **Expected Output**:
```
🔧 Testing Azure AI Integration...
========================================
✅ Successfully extracted 5 transactions
   1. 2025-01-15 - GROCERY STORE - $-45.67
   2. 2025-01-16 - GAS STATION - $-32.45
   3. 2025-01-17 - RESTAURANT - $-28.90
   4. 2025-01-18 - ONLINE SHOPPING - $-156.78
   5. 2025-01-20 - SALARY DEPOSIT - $2500.00

🎉 Azure AI integration is working!
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
❌ Azure AI test failed: AuthenticationError
```
**Solution**:
- Verify your API key is correct
- Check that your Azure OpenAI resource is active
- Ensure the API key has not expired

#### 2. Model Not Found
```
❌ Azure AI test failed: The model 'gpt-4' does not exist
```
**Solution**:
- Verify the deployment name in your `.env` file
- Check that the model deployment is complete in Azure Portal
- Wait a few more minutes if deployment is still in progress

#### 3. Region/Endpoint Issues
```
❌ Azure AI test failed: ConnectionError
```
**Solution**:
- Verify the endpoint URL is correct
- Check that your region supports Azure OpenAI
- Ensure your network allows connections to Azure

#### 4. Quota Exceeded
```
❌ Azure AI test failed: QuotaExceededError
```
**Solution**:
- Check your Azure OpenAI usage quota
- Upgrade your pricing tier if needed
- Wait for quota reset or contact Azure support

### Debug Commands

```bash
# Check environment variables
echo $AZURE_OPENAI_API_KEY
echo $AZURE_OPENAI_ENDPOINT

# Test basic connectivity
curl -H "api-key: $AZURE_OPENAI_API_KEY" \
     "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2024-02-15-preview"

# View detailed logs
python -c "
import os
from openai import AzureOpenAI
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version='2024-02-15-preview',
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)
print('Client initialized successfully')
"
```

## Cost Estimation

### Azure OpenAI Pricing (as of 2025)
- **GPT-4**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- **GPT-3.5-turbo**: ~$0.002 per 1K input tokens, ~$0.002 per 1K output tokens

### Estimated Usage for PDF Parsing
- **Average PDF**: ~2,000 tokens input, ~500 tokens output
- **Cost per PDF**: ~$0.06 - $0.09 (GPT-4)
- **Monthly Estimate**: 100 PDFs = $6-9/month

## Security Best Practices

1. **API Key Security**:
   - Never commit API keys to version control
   - Use environment variables or Azure Key Vault
   - Rotate keys regularly

2. **Data Privacy**:
   - Review what data is sent to Azure AI
   - Ensure compliance with data protection regulations
   - Consider data residency requirements

3. **Access Control**:
   - Use Azure RBAC for resource access
   - Limit API key permissions
   - Monitor usage and costs

## Next Steps

After successful setup:

1. **Test with Real PDFs**: Upload actual financial statements
2. **Monitor Performance**: Track parsing accuracy and costs
3. **Optimize Prompts**: Fine-tune the AI prompts for better accuracy
4. **Add Error Handling**: Implement retry logic and fallbacks
5. **Scale Up**: Consider batch processing for multiple PDFs

## Support

- **Azure OpenAI Documentation**: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **Azure Portal**: https://portal.azure.com
- **Azure OpenAI Studio**: Access via your resource

---

**Setup Complete**: ✅ Azure AI is now configured for PDF transaction extraction!
