# 🚀 Google Sheets Automation Setup - Quick Start

## 📋 What We've Built

Your new automation flow:
```
AirTable → Google Sheets → Your Report System → PDF Reports
```

## 🗂️ Files Created

1. **`backend/app/google_sheets.py`** - Google Sheets integration module
2. **`backend/google_sheets_integration.md`** - Complete setup guide  
3. **`backend/environment_template.txt`** - Environment configuration template
4. **Updated `backend/app/main.py`** - Added new API endpoints
5. **Updated `backend/requirements.txt`** - Added Google Sheets dependencies

## 🏃‍♂️ Quick Setup Steps

### 1. Install Dependencies
```bash
cd startup-report-generator/backend
pip install -r requirements.txt
```

### 2. Set Up Google Cloud & Service Account
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create project → Enable Sheets & Drive APIs → Create service account → Download JSON

### 3. Create Your Google Sheet
Template structure:
| Company Name | Website | Status | Pitch Deck Content | Internal Notes | Processed | Reports Generated | Error |
|--------------|---------|--------|-------------------|----------------|-----------|-------------------|-------|

### 4. Configure Environment
```bash
cp backend/environment_template.txt backend/.env
# Edit .env with your credentials
```

### 5. Share Your Google Sheet with Service Account
- Get the service account email from your JSON credentials file (like: `axl-sheets-automation@your-project.iam.gserviceaccount.com`)
- Share your existing Google Sheet with this email address
- Give it Editor permissions

### 6. Test the System
```bash
# Start your backend
cd startup-report-generator/backend
uvicorn app.main:app --reload

# Test Google Sheets connectivity
curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID"

# Process companies from sheets
curl -X POST "http://localhost:8000/google-sheets-process" \
  -H "Content-Type: application/json" \
  -d '{"sheet_id": "YOUR_SHEET_ID", "worksheet_name": "Sheet1"}'
```

## 🎯 New API Endpoints

### Process Companies from Google Sheets
```http
POST /google-sheets-process
{
  "sheet_id": "your-sheet-id",
  "worksheet_name": "Sheet1"
}
```

### Get Sheet Information
```http
GET /google-sheets-info/{sheet_id}?worksheet_name=Sheet1
```

## 🔧 Key Benefits

✅ **Visibility** - See all companies and processing status in Google Sheets  
✅ **Control** - Process companies manually or on schedule  
✅ **Debugging** - Clear error messages and status tracking  
✅ **Batch Processing** - Handle multiple companies at once  
✅ **Audit Trail** - Track when reports were generated  

## 🚦 Next Steps

1. **Test locally** with a few sample companies from your existing Google Sheet
2. **Deploy to Railway/Render** with Google Sheets credentials
3. **Set up scheduled processing** (cron job or GitHub Actions) 
4. **Monitor and iterate** based on results

## 📞 Need Help?

Check the detailed documentation in:
- `backend/google_sheets_integration.md` - Complete setup guide

The system is now ready for Google Sheets automation! 🎉 