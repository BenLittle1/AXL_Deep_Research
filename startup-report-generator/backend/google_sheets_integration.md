# 📊 Google Sheets Integration Guide

## 🔄 New Automation Workflow

**Previous Flow:** AirTable → Direct Webhook → Your System  
**New Flow:** AirTable → Google Sheets → Your System → Report Generation

This approach gives you more control and visibility over the automation process.

## 📋 Complete Setup Guide

### Step 1: Set Up Google Cloud Project & Service Account

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select an existing one
3. **Enable APIs:**
   - Go to "APIs & Services" > "Library"
   - Search for and enable:
     - Google Sheets API
     - Google Drive API

4. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name: `axl-sheets-automation`
   - Role: `Editor` (or create a custom role with Sheets/Drive access)
   - Click "Create and Continue"

5. **Generate Service Account Key:**
   - Click on your new service account
   - Go to "Keys" tab > "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file (keep it secure!)

### Step 2: Set Up Your Google Sheet

Create a Google Sheet with the following structure:

| Company Name | Website | Status | Pitch Deck Content | Internal Notes | Processed | Reports Generated | Error |
|--------------|---------|--------|-------------------|----------------|-----------|-------------------|-------|
| Tesla | https://tesla.com | Reviewed - Promising | Brief about Tesla... | Our research notes... | | | |
| OpenAI | https://openai.com | Pending | AI company focused on... | Strong team... | | | |

**Required Columns:**
- **Company Name** (required)
- **Status** (should include "Reviewed - Promising" or "Pending")
- **Processed** (will be updated by the system)

**Optional Columns:**
- **Website** / **Company URL**
- **Pitch Deck Content** / **Pitch Deck Notes**  
- **Internal Notes** / **Notes**
- **Reports Generated** (timestamp when processed)
- **Error** (error messages if processing fails)

### Step 3: Share Sheet with Service Account

1. **Get the service account email** from your JSON credentials file (looks like: `axl-sheets-automation@your-project.iam.gserviceaccount.com`)
2. **Share your Google Sheet** with this email address
3. **Give Editor permissions** so the system can update the sheet

### Step 4: Configure Your Environment

Add these environment variables to your `.env` file:

```bash
# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account","project_id":"your-project",...}
# OR for local development:
GOOGLE_SHEETS_CREDENTIALS_FILE=google_sheets_credentials.json

# Your Google Sheet details
GOOGLE_SHEET_ID=1a2b3c4d5e6f7g8h9i0j...
GOOGLE_WORKSHEET_NAME=Sheet1
```

**Option A: Environment Variable (Recommended for Production)**
Copy the entire contents of your JSON credentials file into the `GOOGLE_SHEETS_CREDENTIALS` environment variable.

**Option B: File (For Local Development)**
Place your JSON credentials file in the backend directory and set `GOOGLE_SHEETS_CREDENTIALS_FILE`.

### Step 5: Set Up Processing Automation

You have several options for triggering the processing:

#### Option A: Manual Processing (Recommended to start)
Call the API endpoint manually when you want to process companies:

```bash
curl -X POST "http://localhost:8000/google-sheets-process" \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "your-google-sheet-id",
    "worksheet_name": "Sheet1"
  }'
```

#### Option B: Scheduled Processing (Using cron or GitHub Actions)
Set up a scheduled job to check for new companies every hour:

```bash
# Add to your crontab (runs every hour)
0 * * * * curl -X POST "http://your-api-url/google-sheets-process" -H "Content-Type: application/json" -d '{"sheet_id":"your-sheet-id"}'
```

#### Option C: Webhook Trigger (Advanced)
Set up a webhook that gets triggered when Google Sheets changes using Google Apps Script.

### Step 6: Test the Integration

1. **Test connectivity:**
```bash
curl "http://localhost:8000/google-sheets-info/your-sheet-id?worksheet_name=Sheet1"
```

2. **Add a test company to your Google Sheet**

3. **Run processing:**
```bash
curl -X POST "http://localhost:8000/google-sheets-process" \
  -H "Content-Type: application/json" \
  -d '{
    "sheet_id": "your-google-sheet-id",
    "worksheet_name": "Sheet1"
  }'
```

4. **Check results:**
   - Your Google Sheet should be updated with processing status
   - Check the API response for generated reports

## 🛠️ API Endpoints

### Process Companies from Google Sheets
```http
POST /google-sheets-process
Content-Type: application/json

{
  "sheet_id": "1a2b3c4d5e6f7g8h9i0j...",
  "worksheet_name": "Sheet1"
}
```

**Response:**
```json
{
  "success": true,
  "companies_processed": 2,
  "companies_failed": 0,
  "errors": [],
  "processed_companies": [
    {
      "company_name": "Tesla",
      "reports": [
        {"type": "one_pager", "status": "generated", "size_bytes": 25600},
        {"type": "deep_dive", "status": "generated", "size_bytes": 51200}
      ],
      "row_number": 2
    }
  ]
}
```

### Get Sheet Information
```http
GET /google-sheets-info/{sheet_id}?worksheet_name=Sheet1
```

**Response:**
```json
{
  "success": true,
  "sheet_info": {
    "sheet_title": "AXL Company Pipeline",
    "worksheet_title": "Sheet1",
    "row_count": 100,
    "col_count": 8
  },
  "pending_companies": 5,
  "timestamp": "2024-01-15 10:30:00"
}
```

## 🔧 Troubleshooting

### Common Issues

1. **"Google Sheets credentials not found"**
   - Check your `.env` file has the correct credentials
   - Verify the JSON format is valid

2. **"Failed to connect to Google Sheet"**
   - Verify the sheet ID is correct
   - Ensure the service account has access to the sheet
   - Check that the APIs are enabled in Google Cloud

3. **"No pending companies found"**
   - Check your sheet has companies with status "Pending" or "Reviewed - Promising"
   - Verify the "Processed" column is empty for those companies
   - Check column names match expected format

4. **Permission denied errors**
   - Make sure the service account email has Editor access to your sheet
   - Verify Google Sheets API and Drive API are enabled

### Debugging

Enable detailed logging by setting:
```bash
export LOGGING_LEVEL=DEBUG
```

Check your sheet structure:
```bash
curl "http://localhost:8000/google-sheets-info/your-sheet-id"
```

## 🚀 Deployment

### Railway/Render/Heroku
Add environment variables in your deployment platform:

```bash
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}
GOOGLE_SHEET_ID=your-sheet-id
```

### Docker
```dockerfile
# Add to your Dockerfile
COPY google_sheets_credentials.json /app/
ENV GOOGLE_SHEETS_CREDENTIALS_FILE=/app/google_sheets_credentials.json
```

## 🔄 Integration with Your Existing AirTable Setup

Since you already have AirTable automatically creating entries in Google Sheets when companies are marked as "promising":

1. **Keep your existing `/airtable-webhook` endpoint** for compatibility
2. **Set up Google Sheets API access** following this guide  
3. **Use the new Google Sheets processing endpoints** to read from your existing sheet
4. **Test the new flow** with companies already in your Google Sheet
5. **Set up scheduled processing** to automatically handle new companies

This gives you much more control and visibility into the automation process!

## 📈 Benefits of Google Sheets Approach

- ✅ **Visibility**: See all companies and their processing status
- ✅ **Control**: Manually trigger processing when needed
- ✅ **Debugging**: Easy to see what failed and why
- ✅ **Batch Processing**: Process multiple companies at once
- ✅ **Audit Trail**: Track when reports were generated
- ✅ **Flexibility**: Easy to modify company data before processing 