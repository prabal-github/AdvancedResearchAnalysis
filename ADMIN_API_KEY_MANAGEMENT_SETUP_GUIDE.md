# Admin API Key Management Setup Guide

## Overview
The admin interface now includes comprehensive API key management for AI services, allowing you to configure Anthropic Claude API keys directly through the web interface.

## How to Access

1. **Login as Admin**: Navigate to the admin login page
2. **Admin Dashboard**: Go to `/admin` 
3. **API Keys Management**: Click the "API Keys" button or navigate to `/admin/api_keys`

## Setting Up Anthropic Claude API Key

### Step 1: Get Your API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or login
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (starts with `sk-ant-api...`)

### Step 2: Configure in Admin Panel
1. Go to `/admin/api_keys`
2. Click "Add API Key" button
3. Fill in the form:
   - **Service Name**: Select "Anthropic Claude"
   - **API Key**: Paste your API key
   - **Description**: "Production Claude API for report analysis"
   - **Active**: Keep checked
4. Click "Save API Key"

### Step 3: Test the API Key
1. After saving, you'll see the key in the table
2. Click the test button (check circle icon) 
3. Wait for the test result
4. Should show "✅ API key test successful!"

## Features Available

### 🤖 AI-Powered Report Generation
Once the Anthropic API key is configured, the following features become available:

1. **Enhanced Analysis**: Improved AI analysis using Claude instead of fallback templates
2. **Compliant Report Generation**: Generate SEBI-compliant versions of analyst reports
3. **Professional Insights**: Advanced AI-powered research analysis

### 📊 Admin Dashboard Integration
- **Real-time Status**: See which API keys are configured and active
- **Test Results**: Monitor API key health and connectivity
- **Service Cards**: Quick overview of configured vs. missing services

### 🔧 Management Options
- **Add/Edit/Delete**: Full CRUD operations for API keys
- **Activate/Deactivate**: Enable or disable keys without deletion
- **Test Connectivity**: Verify API keys work before use
- **Usage Tracking**: See when keys were last tested

## API Key Security

### 🔒 Storage
- API keys are stored securely in the database
- Only previews are shown in the admin interface (first 8 and last 4 characters)
- Full keys are only used for API calls, never displayed

### 🛡️ Access Control
- Only admin users can access API key management
- All operations require admin authentication
- Changes are logged for audit purposes

## Automatic Integration

### 🔄 Real-time Updates
When you save an Anthropic API key:
1. The system automatically refreshes the Claude client
2. New API key is immediately available for use
3. No restart required

### 📈 Fallback Handling
- If API key is not configured: System uses template-based responses
- If API key fails: Automatic fallback to templates with error logging
- If database is unavailable: Falls back to environment variables

## Environment Variables (Alternative)

You can still use environment variables as a fallback:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-api-your-key-here"

# Windows Command Prompt  
set ANTHROPIC_API_KEY=sk-ant-api-your-key-here

# Linux/Mac
export ANTHROPIC_API_KEY="sk-ant-api-your-key-here"
```

## Troubleshooting

### Common Issues

1. **"No API key found" message**
   - Check if API key is added in admin panel
   - Verify the key is marked as "Active"
   - Test the API key connectivity

2. **API test fails**
   - Verify the API key is correct and not expired
   - Check internet connectivity
   - Ensure sufficient credits in Anthropic account

3. **Reports still show template responses**
   - Click "Test API Key" button to verify connectivity
   - Check the Enhanced Analysis page for real-time AI responses
   - Try generating a new compliant report

### Admin Support

If you need help:
1. Check the application logs for detailed error messages
2. Use the "Test API Key" feature to diagnose issues
3. Verify your Anthropic account has available credits
4. Contact technical support with specific error messages

## Benefits

### ✅ For Administrators
- Easy web-based configuration
- No need to manage environment variables
- Real-time testing and validation
- Centralized API key management

### ✅ For Analysts
- Better AI-powered report analysis
- Professional compliant report generation
- Improved Enhanced Analysis insights
- Higher quality research output

### ✅ For the System
- Automatic failover to templates if API unavailable
- Real-time configuration updates
- Secure key storage and management
- Audit trail for API key changes

---

**Note**: The Anthropic Claude API is a paid service. Ensure your account has sufficient credits for API usage. The system will automatically fall back to template responses if the API is unavailable or credits are exhausted.