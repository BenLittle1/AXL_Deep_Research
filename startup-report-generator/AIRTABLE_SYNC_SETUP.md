# 🔄 Google Sheets to Airtable Sync Setup Guide

This guide provides multiple options for syncing your Google Sheets data to Airtable, from simple built-in solutions to advanced custom integrations.

## 📋 **Prerequisites**

Before starting, you'll need:

1. **Access to your Google Sheet** with company data
2. **Airtable account** with the destination base
3. **Airtable API credentials** (for Options 3 & 4)

---

## 🌟 **Option 1: Airtable Sync (Recommended - Easiest)**

### **✅ Best For:** 
- Quick setup (5 minutes)
- Non-technical users
- Built-in reliability
- Minimal maintenance

### **📋 Setup Steps:**

1. **Open your Airtable base**
2. **Click the "+" button** to add a new table
3. **Select "Sync with external data"**
4. **Choose "Google Sheets"** from the options
5. **Authenticate with Google** when prompted
6. **Select your specific Google Sheet** and worksheet
7. **Configure sync settings:**
   - **Sync frequency:** Every 15 minutes, hourly, or daily
   - **Primary key field:** Usually "Company Name"
   - **Field mapping:** Map Google Sheet columns to Airtable fields

### **⚙️ Configuration Options:**
- **One-way sync:** Google Sheets → Airtable
- **Two-way sync:** Changes sync both directions
- **Field transformation:** Data type conversion and formatting
- **Filtering:** Only sync rows that meet certain criteria

### **💰 Cost:** Free (included with all Airtable plans)

---

## 🔗 **Option 2: Zapier/Make Integration**

### **✅ Best For:**
- Real-time sync
- Advanced automation workflows
- Multiple trigger conditions
- Integration with other tools

### **📋 Setup Steps:**

#### **Using Zapier:**
1. **Go to zapier.com** and create an account
2. **Create a new Zap:**
   - **Trigger:** Google Sheets - "New or Updated Spreadsheet Row"
   - **Action:** Airtable - "Create Record" or "Update Record"
3. **Connect your Google Sheets account**
4. **Select your spreadsheet and worksheet**
5. **Connect your Airtable account**
6. **Select your Airtable base and table**
7. **Map fields** between Google Sheets and Airtable
8. **Add filters** (optional) to only sync certain rows
9. **Test the Zap** and turn it on

#### **Using Make (formerly Integromat):**
1. **Go to make.com** and create an account
2. **Create a new scenario**
3. **Add Google Sheets module** as trigger
4. **Add Airtable module** as action
5. **Configure field mapping and filters**
6. **Test and activate scenario**

### **💰 Cost:**
- **Zapier:** Free tier (100 tasks/month), paid plans from $19.99/month
- **Make:** Free tier (1,000 operations/month), paid plans from $9/month

---

## 🛠️ **Option 3: Google Apps Script (Advanced)**

### **✅ Best For:**
- Custom business logic
- Advanced field transformations
- Scheduled automation
- Free solution with Google Workspace

### **📋 Setup Steps:**

1. **Get Airtable API credentials:**
   ```
   1. Go to https://airtable.com/account
   2. Generate a personal access token
   3. Note your Base ID from https://airtable.com/api
   ```

2. **Set up Google Apps Script:**
   ```
   1. Go to script.google.com
   2. Create new project
   3. Copy the provided script code
   4. Update configuration variables
   ```

3. **Configure the script:**
   ```javascript
   const AIRTABLE_CONFIG = {
     baseId: 'appXXXXXXXXXXXXXX',      // Your Airtable Base ID
     tableName: 'Companies',          // Your table name
     apiKey: 'patXXXXXXXXXXXXXX'      // Your API key
   };
   ```

4. **Test the connection:**
   ```javascript
   // Run this function first
   testAirtableConnection()
   ```

5. **Set up automatic triggers:**
   ```
   1. In Apps Script, go to Triggers (clock icon)
   2. Add trigger for syncToAirtable()
   3. Choose time-driven trigger
   4. Set frequency (hourly, daily, etc.)
   ```

### **🔧 Advanced Features:**
- **Custom field mapping** and data transformations
- **Batch processing** for efficiency
- **Error handling** and logging
- **Conditional sync** based on row data
- **Email notifications** for sync status

### **💰 Cost:** Free (with Google Workspace)

---

## 🐍 **Option 4: Python Script Integration**

### **✅ Best For:**
- Integration with existing Python workflow
- Advanced data processing
- Custom business logic
- Local or server deployment

### **📋 Setup Steps:**

1. **Install required packages:**
   ```bash
   cd startup-report-generator/backend
   pip install requests python-dotenv
   ```

2. **Configure environment variables:**
   Create/update `.env` file:
   ```bash
   # Airtable Configuration
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   AIRTABLE_TABLE_NAME=Companies
   AIRTABLE_API_KEY=patXXXXXXXXXXXXXX
   
   # Google Sheets (if different from current)
   GOOGLE_SHEET_ID=1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo
   GOOGLE_WORKSHEET_NAME=Sheet1
   ```

3. **Test the connection:**
   ```bash
   python airtable_sync.py
   ```

4. **Integrate with existing workflow:**
   ```python
   from airtable_sync import AirtableSync
   
   # In your automated_processor.py
   sync = AirtableSync()
   result = sync.sync_to_airtable()
   ```

5. **Schedule automatic sync:**
   Add to your automation system or run separately:
   ```bash
   # Add to crontab for hourly sync
   0 * * * * cd /path/to/project && python airtable_sync.py
   ```

### **🔧 Advanced Features:**
- **Smart deduplication** using company names
- **Rate limiting** to respect API limits
- **Batch processing** for large datasets
- **Integration** with existing Google Sheets workflow
- **Custom field mapping** and data validation

### **💰 Cost:** Free (server costs if deployed)

---

## 🎯 **Recommendation Matrix**

| Need | Best Option | Why |
|------|-------------|-----|
| **Quick & Easy** | Option 1 (Airtable Sync) | Built-in, reliable, no coding |
| **Real-time Updates** | Option 2 (Zapier) | Instant triggers, visual setup |
| **Advanced Logic** | Option 3 (Apps Script) | Custom code, free with Google |
| **Python Integration** | Option 4 (Python Script) | Works with existing system |
| **Enterprise Scale** | Option 3 or 4 | Better control and monitoring |

---

## 🔑 **Getting Airtable API Credentials**

### **Step 1: Create Personal Access Token**
1. Go to https://airtable.com/account
2. In the "Personal access tokens" section, click "Create token"
3. Name it "Google Sheets Sync"
4. Add these scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema.bases:read`
5. Add access to your specific base
6. Click "Create token"
7. **Copy and save the token** (starts with `pat`)

### **Step 2: Find Your Base ID**
1. Go to https://airtable.com/api
2. Select your base
3. The Base ID is shown in the URL and examples (starts with `app`)

### **Step 3: Note Your Table Name**
- This is the exact name of your table in Airtable
- Case-sensitive (e.g., "Companies", "Startups", etc.)

---

## 🏃 **Quick Start (Recommended)**

For fastest setup, I recommend **Option 1 (Airtable Sync)**:

1. **Open Airtable** → Your base
2. **Click "+"** → "Sync with external data" → "Google Sheets"
3. **Authenticate and select** your Google Sheet
4. **Configure sync** frequency and field mapping
5. **Done!** 🎉

This gives you automatic syncing without any coding or complex setup.

---

## 🔧 **Field Mapping Reference**

| Google Sheets Column | Airtable Field | Data Type |
|---------------------|----------------|-----------|
| Company Name | Company Name | Text |
| Status | Status | Single Select |
| Website | Website | URL |
| Problem Statement | Problem Statement | Long Text |
| Problem Statement Commentary | Problem Commentary | Long Text |
| Problem Statement Score | Problem Score | Number |
| Industry | Industry | Text |
| Competitors | Competitors | Long Text |
| Target Audience | Target Audience | Long Text |
| MVP | MVP Status | Text |
| Progress | Product Progress | Text |
| Founder Fit | Founder Fit | Long Text |
| Team Growth | Team Growth | Text |
| Traction | Traction | Long Text |
| Pricing | Pricing Model | Text |
| Location | Location | Text |
| PDF_URL | PDF URL | URL |
| One-Pager | One-Pager Link | URL |
| Deep-Dive | Deep-Dive Link | URL |
| Generated | Reports Generated | Checkbox |

---

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"Base not found" error:**
   - Check your Base ID (starts with `app`)
   - Ensure your API token has access to this base

2. **"Table not found" error:**
   - Check table name spelling and case
   - Ensure table exists in your base

3. **"Field not found" error:**
   - Verify field names match exactly
   - Check that fields exist in your Airtable table

4. **Sync not working:**
   - Test API credentials manually
   - Check rate limits (5 requests/second for Airtable)
   - Verify Google Sheets permissions

### **Getting Help:**
- **Airtable Support:** https://support.airtable.com
- **Zapier Help:** https://help.zapier.com
- **Google Apps Script:** https://developers.google.com/apps-script

---

## 📈 **Next Steps**

1. **Choose your preferred option** based on your needs
2. **Follow the setup steps** for your chosen method
3. **Test with a few records** before full sync
4. **Set up monitoring** to track sync status
5. **Document your configuration** for team members

Would you like me to help you set up any of these options? 