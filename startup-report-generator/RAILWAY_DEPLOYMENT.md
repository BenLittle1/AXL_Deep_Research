# Railway Deployment Guide

## 🚄 Deploy Your Startup Report Generator to Railway

### Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:

```bash
# If not already done
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Deploy to Railway

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login** with your GitHub account
3. **Click "Deploy from GitHub repo"**
4. **Select your repository**: `BenLittle1/AXL_Deep_Research`
5. **Select the service**: Choose "Deploy" 

### Step 3: Configure Environment Variables

In your Railway dashboard:

1. **Go to Variables tab**
2. **Add these environment variables:**
   ```
   PERPLEXITY_API_KEY=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
   PORT=8000
   ```

### Step 4: Configure Build Settings

Railway should automatically detect your Python app, but if needed:

1. **Go to Settings tab**
2. **Set Build Command**: `cd backend && pip install -r requirements.txt`
3. **Set Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 5: Deploy and Get Your URL

1. **Railway will automatically build and deploy**
2. **Get your deployment URL** (something like: `https://your-app-name.railway.app`)
3. **Test the health endpoint**: `https://your-app-name.railway.app/health`

### Step 6: Update Your Airtable Script

Replace the `apiUrl` in your Airtable script with your Railway URL:

```javascript
// Replace this line in your Airtable script:
let apiUrl = 'https://your-app-name.railway.app/airtable-webhook';
```

### Step 7: Test the Integration

1. **Test API directly:**
   ```bash
   curl -X POST "https://your-app-name.railway.app/airtable-webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "Tesla",
       "company_url": "https://tesla.com", 
       "generate_both": true
     }'
   ```

2. **Test Airtable trigger:**
   - Change a company status to "Reviewed - Promising"
   - Check Railway logs for processing
   - Verify webhook returns success

## 🔧 Troubleshooting

### Common Issues:

1. **Build fails**: Check that `requirements.txt` is in the `backend/` folder
2. **App won't start**: Verify the start command includes `cd backend &&`
3. **CORS errors**: The CORS is set to allow all origins (`"*"`)
4. **Timeout**: Large companies may take 30+ seconds - this is normal

### Railway Logs:

Monitor your app in Railway dashboard:
- **Build logs**: See if dependencies install correctly
- **Deploy logs**: Check for startup errors  
- **App logs**: Monitor API requests and responses

### Expected Response Format:

Successful webhook response:
```json
{
  "success": true,
  "company_name": "Tesla",
  "total_reports": 2,
  "reports_generated": [
    {
      "type": "one_pager",
      "filename": "Tesla_one_pager.pdf", 
      "size_bytes": 25600,
      "status": "generated"
    },
    {
      "type": "deep_dive", 
      "filename": "Tesla_deep_dive.pdf",
      "size_bytes": 51200,
      "status": "generated"
    }
  ]
}
```

## 🎉 Next Steps

Once deployed:
1. ✅ Update Airtable script with Railway URL
2. ✅ Test with a few companies manually  
3. ✅ Monitor Railway logs during processing
4. ✅ Scale up to automated processing
5. 🔄 Consider adding file storage (AWS S3) for generated PDFs 