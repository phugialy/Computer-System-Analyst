# Google OAuth Setup Guide

## Overview

This application now uses **real Google OAuth integration** for secure email sending. This means:

- ✅ **Secure**: No passwords stored in the application
- ✅ **Modern**: Uses Google's official OAuth 2.0 flow
- ✅ **User-friendly**: Simple "Sign in with Google" button
- ✅ **Professional**: Uses Gmail API for sending emails

## Setup Requirements

### 1. Google Cloud Project Setup

To use this feature, you need to set up a Google Cloud project:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials JSON file

### 2. Configure the Application

1. **Update the OAuth Configuration**
   - Open `google_oauth_real.py`
   - Replace the placeholder credentials:

```python
class GoogleOAuthConfig:
    CLIENT_ID = "your-actual-client-id.apps.googleusercontent.com"
    CLIENT_SECRET = "your-actual-client-secret"
```

2. **Install Required Dependencies**
   ```bash
   pip install requests PyQt6
   ```

## How It Works

### 1. User Authentication
- User clicks "Sign in with Google"
- Browser opens with Google's OAuth page
- User signs in and grants permissions
- Application receives access token

### 2. Email Sending
- Application uses access token to call Gmail API
- Emails are sent directly through Google's servers
- No passwords or credentials stored locally

## Security Benefits

- **No Password Storage**: Credentials never stored in the app
- **Token-based**: Uses temporary access tokens
- **Google-managed**: Google handles all security
- **Revocable**: Users can revoke access anytime

## User Experience

### For End Users:
1. Click "Sign in with Google"
2. Complete authentication in browser
3. Return to application
4. Send emails normally

### For Developers:
1. Set up Google Cloud project
2. Configure OAuth credentials
3. Update application configuration
4. Deploy to users

## Troubleshooting

### "Authentication Failed"
- Check Google Cloud project setup
- Verify OAuth credentials are correct
- Ensure Gmail API is enabled

### "Email Sending Failed"
- Check internet connection
- Verify user granted email permissions
- Check Gmail API quotas

### "Client ID Not Found"
- Update `google_oauth_real.py` with your actual credentials
- Ensure credentials are for desktop application

## Development vs Production

### Development:
- Use test Google Cloud project
- Limited API quotas
- For testing only

### Production:
- Use production Google Cloud project
- Higher API quotas
- Proper security measures

## API Quotas

Gmail API has the following limits:
- **Per user per day**: 1,000,000,000 quota units
- **Per user per 100 seconds**: 250 quota units
- **Per user per 100 seconds per user**: 500 quota units

For most use cases, these limits are more than sufficient.

## Next Steps

1. **Set up Google Cloud project** (see steps above)
2. **Update credentials** in `google_oauth_real.py`
3. **Test the integration** with the test application
4. **Deploy to production** when ready

The real Google OAuth integration provides a much more secure and professional email solution! 