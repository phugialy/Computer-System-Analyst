# Resources Directory

This directory contains configuration files and resources for the Computer Inspector application.

## Files

### `client_secrets.json` (Required for Google OAuth)
This file contains your Google OAuth 2.0 credentials for Gmail API integration.

**How to create this file:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file
5. Rename the downloaded file to `client_secrets.json`
6. Place it in this `res/` directory

**File structure should look like:**
```json
{
  "installed": {
    "client_id": "your-actual-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-actual-client-secret",
    "redirect_uris": ["http://localhost:8080"]
  }
}
```

### `client_secrets_template.json` (Template)
A template file showing the required structure. Copy this to `client_secrets.json` and fill in your actual credentials.

## Security Notes

- Keep your `client_secrets.json` file secure
- Don't commit this file to version control
- The file contains sensitive credentials
- Only share with trusted team members

## Usage

Once you have `client_secrets.json` in this directory, the application will be able to:
- Authenticate users with Google OAuth
- Send emails via Gmail API
- Store tokens securely for future use 