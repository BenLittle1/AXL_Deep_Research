# 📋 Extremely Detailed Google Sheets Automation Setup

## 🎯 What We're Building

```
Your AirTable → Google Sheets → Your Report System → PDF Reports
     (existing)     (existing)        (new part)        (existing)
```

When AirTable marks a company as "promising", it adds a row to your Google Sheet. Our new system will:
1. Read companies from that Google Sheet
2. Generate reports for unprocessed companies
3. Mark them as processed in the sheet

## 📝 Prerequisites Checklist

Before we start, make sure you have:
- [ ] Your existing Google Sheet that AirTable writes to
- [ ] Access to Google Cloud Console
- [ ] Your existing backend system running
- [ ] Terminal/command line access

## 🔧 Part 1: Google Cloud Setup (15 minutes)

### Step 1.1: Create Google Cloud Project

1. **Open your browser** and go to https://console.cloud.google.com/
2. **Sign in** with your Google account
3. **Look for the project selector** at the top of the page (it might say "Select a project")
4. **Click "NEW PROJECT"** (top right of the project selector dropdown)
5. **Fill out the form:**
   - Project name: `axl-sheets-automation` (or any name you prefer)
   - Organization: Leave as is (usually your email domain)
   - Location: Leave as is
6. **Click "CREATE"**
7. **Wait for creation** (30-60 seconds)
8. **Select your new project** from the project dropdown

✅ **Checkpoint:** You should see your project name in the top bar

### Step 1.2: Enable Required APIs

1. **In the left sidebar**, click "APIs & Services" → "Library"
2. **Search for "Google Sheets API"**
3. **Click on "Google Sheets API"** from the results
4. **Click "ENABLE"** (blue button)
5. **Wait for it to enable** (10-20 seconds)
6. **Go back to the Library** (click "Library" in the left sidebar again)
7. **Search for "Google Drive API"**
8. **Click on "Google Drive API"** from the results
9. **Click "ENABLE"** (blue button)

✅ **Checkpoint:** Both APIs should show as "Enabled" if you go to "APIs & Services" → "Enabled APIs & services"

### Step 1.3: Create Service Account

1. **In the left sidebar**, click "APIs & Services" → "Credentials"
2. **Click "CREATE CREDENTIALS"** (blue button at the top)
3. **Select "Service account"** from the dropdown
4. **Fill out Service account details:**
   - Service account name: `axl-sheets-automation`
   - Service account ID: (auto-filled, leave as is)
   - Description: `Service account for AXL report generation from Google Sheets`
5. **Click "CREATE AND CONTINUE"**
6. **Grant service account access:**
   - Role: Click the dropdown and search for "Editor"
   - Select "Editor" (gives read/write access to everything)
   - Click "CONTINUE"
7. **Grant users access:** Skip this step, click "DONE"

✅ **Checkpoint:** You should see your new service account in the credentials list

### Step 1.4: Create and Download Service Account Key

1. **Find your service account** in the credentials list (should be the one you just created)
2. **Click on the service account name** (not the email, the name)
3. **Go to the "Keys" tab**
4. **Click "ADD KEY"** → "Create new key"
5. **Select "JSON"** format
6. **Click "CREATE"**
7. **A JSON file will download automatically** - this is your credentials file!
8. **IMPORTANT:** Move this file to a secure location and remember where it is

✅ **Checkpoint:** You should have a JSON file downloaded (something like `axl-sheets-automation-abc123.json`)

### Step 1.5: Note Your Service Account Email

1. **Look at the JSON file you just downloaded** (open it in a text editor)
2. **Find the "client_email" field** - it looks like: `axl-sheets-automation@your-project-123456.iam.gserviceaccount.com`
3. **Copy this email address** - you'll need it in the next part

## 🗂️ Part 2: Google Sheets Setup (5 minutes)

### Step 2.1: Open Your Existing Google Sheet

1. **Open your existing Google Sheet** that AirTable writes to
2. **Look at the column structure** - we need to understand what columns you have

### Step 2.2: Check/Add Required Columns

Your sheet needs these columns (add them if missing):

**Required columns:**
- `Company Name` (AirTable probably creates this)
- `Status` (AirTable probably sets this to "Reviewed - Promising")

**Optional but helpful columns:**
- `Website` or `Company URL`
- `Pitch Deck Content` or `Pitch Deck Notes`
- `Internal Notes` or `Notes`

**Columns our system will add/update:**
- `Processed` (we'll mark as "✓ Processed" or "❌ Failed")
- `Reports Generated` (timestamp when we process)
- `Error` (error message if processing fails)

**To add missing columns:**
1. **Right-click on any column header**
2. **Select "Insert 1 right"**
3. **Type the column name** in the new header cell
4. **Repeat for each missing column**

### Step 2.3: Share Sheet with Service Account

1. **Click the "Share" button** (top right of your Google Sheet)
2. **In the "Add people and groups" field**, paste the service account email you copied earlier
3. **Change permission to "Editor"** (click the pencil icon dropdown)
4. **Uncheck "Notify people"** (we don't want to spam the service account)
5. **Click "Share"**

✅ **Checkpoint:** The service account email should appear in the sheet's sharing list

### Step 2.4: Get Your Sheet ID

1. **Look at the URL of your Google Sheet**
2. **Find the sheet ID** - it's the long string between `/d/` and `/edit`
   - Example: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit`
   - Sheet ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`
3. **Copy this sheet ID** - you'll need it for configuration

## ⚙️ Part 3: Backend Configuration (10 minutes)

### Step 3.1: Install Dependencies

1. **Open Terminal/Command Prompt**
2. **Navigate to your project:**
   ```bash
   cd /Users/benlittle/Desktop/Stuff/Projects/AXL/AXL_Ventures_Deep_Research/startup-report-generator/backend
   ```
3. **Install new dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Wait for installation** (1-2 minutes)

✅ **Checkpoint:** No error messages, installation completes successfully

### Step 3.2: Create Environment Configuration

1. **In the backend directory**, copy the environment template:
   ```bash
   cp environment_template.txt .env
   ```
2. **Open the .env file** in a text editor:
   ```bash
   nano .env
   # or use VS Code, TextEdit, etc.
   ```

### Step 3.3: Configure Environment Variables

Edit your `.env` file with your actual values:

```bash
# ==============================================
# AI API Configuration (keep your existing values)
# ==============================================
AI_API_KEY=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
PERPLEXITY_API_KEY=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
AI_API_ENDPOINT=https://api.perplexity.ai/chat/completions

# ==============================================
# Google Sheets Integration (NEW - add these)
# ==============================================
# OPTION 1: Put the full JSON content here (recommended for production)
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account","project_id":"your-project-123456","private_key_id":"abc123...","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhki...","client_email":"axl-sheets-automation@your-project-123456.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/axl-sheets-automation%40your-project-123456.iam.gserviceaccount.com"}

# OPTION 2: OR point to the JSON file (easier for local development)
GOOGLE_SHEETS_CREDENTIALS_FILE=google_sheets_credentials.json

# Your Google Sheet details
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_WORKSHEET_NAME=Sheet1

# ==============================================
# Application Configuration
# ==============================================
PORT=8000
LOGGING_LEVEL=INFO
```

**For the credentials, choose ONE option:**

**Option A (Easier for local testing):** 
1. Copy your downloaded JSON file to the backend directory
2. Rename it to `google_sheets_credentials.json`
3. Use the `GOOGLE_SHEETS_CREDENTIALS_FILE` option

**Option B (Better for production):**
1. Open your downloaded JSON file
2. Copy the ENTIRE contents (it's one long line)
3. Paste it as the value for `GOOGLE_SHEETS_CREDENTIALS`

**Replace these placeholders:**
- `GOOGLE_SHEET_ID`: Your actual sheet ID from Step 2.4
- `GOOGLE_WORKSHEET_NAME`: Usually "Sheet1", but check your sheet's tab name

### Step 3.4: Save the Configuration

1. **Save the .env file** (Ctrl+S or Cmd+S)
2. **Make sure it's saved in the backend directory**

✅ **Checkpoint:** Your .env file exists and has all the values filled in

## 🧪 Part 4: Testing (15 minutes)

### Step 4.1: Start Your Backend

1. **In Terminal, from the backend directory:**
   ```bash
   uvicorn app.main:app --reload
   ```
2. **You should see:**
   ```
   INFO:     Will watch for changes in these directories: ['/path/to/backend']
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process [12345] using WatchFiles
   INFO:     Started server process [12346]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

✅ **Checkpoint:** Server starts without errors

### Step 4.2: Test Basic Connectivity

1. **Open a new Terminal window** (keep the server running in the first one)
2. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
3. **You should see:**
   ```json
   {"status":"healthy","timestamp":"2024-01-15T10:30:00Z"}
   ```

✅ **Checkpoint:** Health check returns successfully

### Step 4.3: Test Google Sheets Connectivity

1. **Test sheet info** (replace `YOUR_SHEET_ID` with your actual sheet ID):
   ```bash
   curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID?worksheet_name=Sheet1"
   ```
2. **You should see something like:**
   ```json
   {
     "success": true,
     "sheet_info": {
       "sheet_title": "AXL Company Pipeline",
       "worksheet_title": "Sheet1",
       "row_count": 10,
       "col_count": 8
     },
     "pending_companies": 2,
     "timestamp": "2024-01-15 10:30:00"
   }
   ```

✅ **Checkpoint:** You can successfully read your Google Sheet

**If you get an error:**
- Check that the sheet ID is correct
- Verify the service account has access to the sheet
- Make sure your credentials are correct in the .env file

### Step 4.4: Add Test Data to Your Sheet

1. **Go to your Google Sheet**
2. **Add a test company row** with these values:
   - Company Name: `Test Company`
   - Status: `Reviewed - Promising` (or whatever status you use)
   - Website: `https://example.com`
   - Pitch Deck Content: `This is a test company for automation`
   - Internal Notes: `Testing our new automation system`
   - Processed: (leave empty)
   - Reports Generated: (leave empty)
   - Error: (leave empty)

### Step 4.5: Test Processing

1. **Run the processing command:**
   ```bash
   curl -X POST "http://localhost:8000/google-sheets-process" \
     -H "Content-Type: application/json" \
     -d '{
       "sheet_id": "YOUR_SHEET_ID",
       "worksheet_name": "Sheet1"
     }'
   ```
2. **You should see detailed output** in both:
   - The terminal running your server (lots of processing logs)
   - The curl response (JSON with processing results)

3. **Check your Google Sheet** - the test company row should now have:
   - Processed: `✓ Processed`
   - Reports Generated: (timestamp)

✅ **Checkpoint:** Test company gets processed successfully

## 🚀 Part 5: Production Setup (10 minutes)

### Step 5.1: Set Up Scheduled Processing

You can process companies automatically using several methods:

**Option A: Manual Processing (Recommended to start)**
Just run the curl command whenever you want to process new companies:
```bash
curl -X POST "http://localhost:8000/google-sheets-process" \
  -H "Content-Type: application/json" \
  -d '{"sheet_id": "YOUR_SHEET_ID", "worksheet_name": "Sheet1"}'
```

**Option B: Scheduled with cron (Unix/Mac/Linux)**
1. **Open crontab:**
   ```bash
   crontab -e
   ```
2. **Add this line** (runs every hour):
   ```bash
   0 * * * * curl -X POST "http://localhost:8000/google-sheets-process" -H "Content-Type: application/json" -d '{"sheet_id":"YOUR_SHEET_ID","worksheet_name":"Sheet1"}' >> /tmp/axl-processing.log 2>&1
   ```

**Option C: GitHub Actions (if your code is on GitHub)**
Create `.github/workflows/process-companies.yml`:
```yaml
name: Process Companies
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - name: Process Companies
        run: |
          curl -X POST "${{ secrets.API_URL }}/google-sheets-process" \
            -H "Content-Type: application/json" \
            -d '{"sheet_id":"${{ secrets.SHEET_ID }}","worksheet_name":"Sheet1"}'
```

### Step 5.2: Deploy to Production

**For Railway deployment:**
1. **Push your code** to GitHub
2. **Connect Railway** to your repo
3. **Add environment variables** in Railway dashboard:
   - `GOOGLE_SHEETS_CREDENTIALS` (the full JSON)
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_WORKSHEET_NAME`
   - All your existing variables

**For local production:**
1. **Use a process manager** like PM2:
   ```bash
   npm install -g pm2
   pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name axl-backend
   ```

## 🔍 Part 6: Monitoring & Troubleshooting

### Common Issues and Solutions

**1. "Google Sheets credentials not found"**
- Check your `.env` file has the correct credentials
- Verify JSON format is valid (use a JSON validator)
- Make sure the file path is correct if using file option

**2. "Failed to connect to Google Sheet"**
- Verify sheet ID is correct (copy from URL)
- Check that service account email has Editor access
- Ensure Google Sheets API is enabled

**3. "No pending companies found"**
- Check companies have status "Pending" or "Reviewed - Promising"
- Verify "Processed" column is empty for those companies
- Check column names match expected format

**4. Processing fails**
- Check your Perplexity API key is valid
- Verify you have sufficient API credits
- Check server logs for detailed error messages

### Monitoring Commands

**Check sheet status:**
```bash
curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID"
```

**Check server logs:**
```bash
# If running with uvicorn directly, logs appear in terminal
# If using PM2:
pm2 logs axl-backend
```

**Check processing results:**
The Google Sheet itself shows the status of each company.

## 🎯 Part 7: Understanding the Workflow

### How It Works Daily

1. **AirTable marks company as promising** → Automatically adds to Google Sheet
2. **Your scheduled process runs** (hourly/daily) → Checks for new companies
3. **System processes each company:**
   - Runs research agent (gathers data)
   - Runs formatting agent (creates reports)
   - Generates PDF files
   - Updates Google Sheet with status
4. **You review results** in Google Sheet and generated reports

### Key Benefits

- ✅ **Full visibility**: See all companies and their status
- ✅ **Error tracking**: Failed processes show error messages
- ✅ **Batch processing**: Handle multiple companies at once
- ✅ **Manual control**: Process on-demand when needed
- ✅ **Audit trail**: Timestamps show when processing happened

## 🚨 Emergency Procedures

**If something breaks:**

1. **Check the Google Sheet** - does it show error messages?
2. **Check server logs** - what error messages appear?
3. **Test connectivity:**
   ```bash
   curl "http://localhost:8000/health"
   curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID"
   ```
4. **Restart the server:**
   ```bash
   # If running directly:
   Ctrl+C to stop, then: uvicorn app.main:app --reload
   
   # If using PM2:
   pm2 restart axl-backend
   ```

**If you need to reprocess a company:**
1. Clear the "Processed" column for that company in Google Sheets
2. Run the processing command again

## 🎉 You're Done!

Your Google Sheets automation is now fully set up! The system will:

1. ✅ Read companies from your existing Google Sheet
2. ✅ Process them through your AI research system
3. ✅ Generate professional PDF reports
4. ✅ Track status and errors in the sheet
5. ✅ Run automatically on your chosen schedule

**Next steps:**
- Add some real companies to test with
- Set up your preferred scheduling method
- Monitor the first few runs to ensure everything works smoothly
- Deploy to production when ready

Need help with any step? Check the logs and error messages - they're designed to be helpful! 