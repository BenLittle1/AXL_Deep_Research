# 🔐 Google Cloud Authentication Alternatives

## 🚨 Issue: Service Account Key Creation Disabled

Your organization has the `iam.disableServiceAccountKeyCreation` policy enabled, which prevents creating service account keys for security reasons.

## 🛠️ Solution Options (Choose One)

### Option 1: Use Application Default Credentials (Recommended)

This uses your personal Google account instead of a service account.

#### Step 1.1: Install Google Cloud CLI
```bash
# Mac (with Homebrew)
brew install google-cloud-sdk

# Windows - Download from: https://cloud.google.com/sdk/docs/install
# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

#### Step 1.2: Authenticate with Your Account
```bash
gcloud auth login
gcloud auth application-default login
```

#### Step 1.3: Set Your Project
```bash
gcloud config set project YOUR_PROJECT_ID
```

#### Step 1.4: Update Your Environment Configuration
Edit your `.env` file and **remove** the Google Sheets credentials lines:
```bash
# Comment out or remove these lines:
# GOOGLE_SHEETS_CREDENTIALS=...
# GOOGLE_SHEETS_CREDENTIALS_FILE=...

# Keep these:
GOOGLE_SHEET_ID=your-sheet-id
GOOGLE_WORKSHEET_NAME=Sheet1
```

#### Step 1.5: Share Your Google Sheet
Since you're using your personal account, just make sure your Google account has access to the sheet (you probably already do).

---

### Option 2: Use a Different Google Account

Create a personal Google Cloud project with a different account.

#### Step 2.1: Create Personal Google Account Project
1. **Sign out** of your current Google account
2. **Sign in** with a personal Gmail account
3. **Go to** https://console.cloud.google.com/
4. **Create a new project** (follow the original guide)
5. **Enable APIs** and **create service account** as normal

#### Step 2.2: Use the Personal Account Credentials
Follow the original setup guide with your personal account - service account keys should work there.

---

### Option 3: Request Policy Exception (If You're Admin)

If you have organization admin access:

#### Step 3.1: Disable the Policy Temporarily
1. **Go to** https://console.cloud.google.com/iam-admin/orgpolicies
2. **Find** "Disable service account key creation"
3. **Click** on the policy
4. **Override** the policy for your project
5. **Set to** "Allow All"
6. **Save** and try creating the service account key again

#### Step 3.2: Re-enable After Setup
After getting your credentials, re-enable the policy for security.

---

### Option 4: Use OAuth 2.0 Flow (Advanced)

This requires code changes but is more secure.

#### Step 4.1: Create OAuth 2.0 Credentials
1. **Go to** APIs & Services → Credentials
2. **Click** "CREATE CREDENTIALS" → "OAuth client ID"
3. **Select** "Desktop application"
4. **Download** the JSON file

#### Step 4.2: Modify the Code
Update `startup-report-generator/backend/app/google_sheets.py`:

```python
# Add at the top
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

def _setup_client_oauth(self):
    """Set up client using OAuth 2.0 flow."""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    self.client = gspread.authorize(creds)
```

---

## 🚀 Recommended Approach

**For quick setup: Use Option 1 (Application Default Credentials)**

This is the easiest and most secure approach:

### Quick Setup Steps:

1. **Install Google Cloud CLI:**
   ```bash
   # Mac
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Update your .env file:**
   ```bash
   # Remove/comment out these lines:
   # GOOGLE_SHEETS_CREDENTIALS=...
   # GOOGLE_SHEETS_CREDENTIALS_FILE=...
   
   # Keep these:
   GOOGLE_SHEET_ID=your-sheet-id
   GOOGLE_WORKSHEET_NAME=Sheet1
   ```

4. **Make sure you have access to your Google Sheet** (you probably already do with your account)

5. **Test the connection:**
   ```bash
   curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID"
   ```

### Benefits of Application Default Credentials:
- ✅ **No service account keys** (more secure)
- ✅ **Uses your existing Google account**
- ✅ **Automatically refreshes tokens**
- ✅ **Works immediately**
- ✅ **No organization policy conflicts**

### For Production:
When you deploy to Railway/production, you'll need to either:
- Use a service account from a different Google Cloud project (personal account)
- Or implement OAuth 2.0 flow for production authentication

---

## 🧪 Testing Your Setup

After choosing your authentication method:

1. **Start your server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Test Google Sheets access:**
   ```bash
   curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID"
   ```

3. **If successful, try processing:**
   ```bash
   curl -X POST "http://localhost:8000/google-sheets-process" \
     -H "Content-Type: application/json" \
     -d '{"sheet_id": "YOUR_SHEET_ID", "worksheet_name": "Sheet1"}'
   ```

## 🔧 Code Changes Needed

Update your `google_sheets.py` to handle the case where no credentials are provided:

```python
def _setup_client(self):
    """Set up the Google Sheets client using available credentials."""
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Try service account credentials first
        credentials_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
        credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE')
        
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
        elif credentials_file and os.path.exists(credentials_file):
            credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        else:
            # Fall back to Application Default Credentials
            print("🔄 Using Application Default Credentials")
            credentials, project = google.auth.default(scopes=scopes)
        
        self.client = gspread.authorize(credentials)
        print("✅ Google Sheets client initialized successfully")
        
    except Exception as e:
        print(f"❌ Error setting up Google Sheets client: {str(e)}")
        self.client = None
```

This approach will try service account credentials first, then fall back to your personal credentials automatically! 

## 🔧 Fix the Quota Project Warning

The warning means your Application Default Credentials are using a different project for quota/billing. Let's fix this:

```bash
gcloud auth application-default set-quota-project axl-research-automation
```

## 🚀 Complete Your Setup

Now run these commands in order:

### Step 1: Enable Required APIs
```bash
gcloud services enable sheets.googleapis.com
gcloud services enable drive.googleapis.com
```

### Step 2: Re-authenticate (to ensure clean credentials)
```bash
gcloud auth application-default login
```

This will:
- Open your browser
- Ask you to sign in with your Google account
- Set up the credentials properly with the correct project

### Step 3: Verify Everything is Working
```bash
# Check your project
gcloud config get-value project

# Check your authenticated account
gcloud auth list

# Verify the quota project is set correctly
gcloud auth application-default print-access-token
```

You should see:
```
Project: axl-research-automation
Account: your-email@gmail.com (active)
```

## 📝 Update Your .env File

Now update your `.env` file with your project details:

```bash
# AI API Configuration (keep your existing values)
AI_API_KEY=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
PERPLEXITY_API_KEY=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
AI_API_ENDPOINT=https://api.perplexity.ai/chat/completions

# Google Sheets Integration
GOOGLE_SHEET_ID=your-actual-sheet-id-here
GOOGLE_WORKSHEET_NAME=Sheet1

# Application Configuration
PORT=8000
LOGGING_LEVEL=INFO
```

**Make sure to:**
- Replace `your-actual-sheet-id-here` with your Google Sheet ID
- Remove any `GOOGLE_SHEETS_CREDENTIALS` lines (we don't need them with Application Default Credentials)

## 🧪 Test Your Setup

### Step 1: Start Your Server
```bash
cd /Users/benlittle/Desktop/Stuff/Projects/AXL/AXL_Ventures_Deep_Research/startup-report-generator/backend
uvicorn app.main:app --reload
```

### Step 2: Test Google Sheets Connection
In another terminal:
```bash
curl "http://localhost:8000/google-sheets-info/YOUR_SHEET_ID"
```

Replace `YOUR_SHEET_ID` with your actual Google Sheet ID.

## 🎯 If You Need Your Google Sheet ID

If you don't have your Google Sheet ID yet:

1. **Open your Google Sheet** that AirTable writes to
2. **Look at the URL:**
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
   ```
3. **Copy the long string** between `/d/` and `/edit`:
   ```
   1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
   ```

## ✅ Expected Results

After running the quota project command and re-authenticating, you should see:
- ✅ No more warnings when using gcloud commands
- ✅ Successful connection to Google Sheets
- ✅ Your server can read from your Google Sheet

Let me know the results of these commands and we'll move to testing your Google Sheets connection! 