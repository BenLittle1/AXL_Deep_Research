# 🚀 Railway Deployment Guide - 24/7 Automated Report Generator

This guide will help you deploy your AXL automated report generator to Railway, ensuring it runs **24/7 in the cloud** and automatically processes companies marked as "Promising" regardless of whether your local machine is running.

## 🎯 **What This Deployment Does**

✅ **Web App**: FastAPI server for manual report generation  
✅ **Automated Processor**: Monitors Google Sheets every 2 minutes  
✅ **24/7 Uptime**: Always available in the cloud  
✅ **Health Monitoring**: Automatic restart if services fail  
✅ **Centralized Logs**: View all activity in Railway dashboard  

---

## 📋 **Prerequisites**

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Environment Variables**: API keys and credentials ready
3. **Google Cloud Project**: Service account with proper permissions
4. **Repository Access**: Your code pushed to GitHub/GitLab

---

## 🚀 **Step 1: Prepare for Deployment**

### **1.1 Environment Variables You'll Need:**

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-...

# Google Cloud Credentials (entire JSON as string)
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Google Drive (optional, if using Drive upload)
GOOGLE_DRIVE_PARENT_FOLDER_ID=1ABC...

# Perplexity API (optional, for enhanced research)  
PERPLEXITY_API_KEY=pplx-...

# Custom AI API (if using instead of OpenAI)
AI_API_KEY=your-key
AI_API_ENDPOINT=https://your-api-endpoint.com

# Google Sheets Configuration
GOOGLE_SHEET_ID=1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo
GOOGLE_WORKSHEET_NAME=Sheet1
```

### **1.2 Get Your Google Credentials JSON:**

```bash
# If you have the service account file:
cat path/to/your/service-account.json | tr -d '\n'

# Copy the entire output (it should be one long line)
```

---

## 🚀 **Step 2: Deploy to Railway**

### **2.1 Connect Repository:**

1. **Go to [railway.app](https://railway.app)**
2. **Click "Start a New Project"**
3. **Choose "Deploy from GitHub repo"**
4. **Select your repository**
5. **Choose the `startup-report-generator` folder** as the source

### **2.2 Configure Build Settings:**

Railway will automatically detect the configuration from `railway.json`, but verify:

- **Root Directory**: `startup-report-generator`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python railway_start.py`

### **2.3 Set Environment Variables:**

In Railway dashboard:

1. **Go to your project**
2. **Click "Variables" tab**
3. **Add each environment variable:**

```
OPENAI_API_KEY = sk-proj-your-key-here
GOOGLE_CREDENTIALS_JSON = {"type":"service_account","project_id":"your-project"...}
GOOGLE_SHEET_ID = 1z8Uv-EVDQ4aGar0hKaHlEMsbhmyhWDjsJnrcqAhMKFo
GOOGLE_WORKSHEET_NAME = Sheet1
```

**🚨 Important**: Make sure `GOOGLE_CREDENTIALS_JSON` is the **entire JSON file as a single line** (no line breaks)

---

## 🚀 **Step 3: Deploy and Monitor**

### **3.1 Initial Deployment:**

1. **Click "Deploy"** in Railway
2. **Watch the build logs** for any errors
3. **Wait for "Deployment successful"** message

### **3.2 Verify Services Are Running:**

1. **Check the logs** in Railway dashboard
2. **Look for these startup messages:**
   ```
   🚀==================================================
      AXL VENTURES - RAILWAY DEPLOYMENT  
   ==================================================🚀
   
   ✅ Environment variables validated
   🌐 Starting web server process...
   🤖 Starting automation processor...
   ✅ Both services started successfully!
   ```

3. **Visit your Railway URL** to confirm web app is working

### **3.3 Test the Automation:**

1. **Add a test company** to your Google Sheet
2. **Set Status to "Promising"**
3. **Check Railway logs** within 2 minutes
4. **Verify reports are generated**

---

## 📊 **Step 4: Monitor Your Deployment**

### **4.1 Railway Dashboard:**

- **Logs**: View real-time application logs
- **Metrics**: CPU, memory, and network usage
- **Deployments**: History of all deployments
- **Variables**: Manage environment variables

### **4.2 Key Log Messages to Watch:**

✅ **Normal Operation:**
```
🔍 Checking for new companies in Google Sheets...
📋 Found 0 pending companies
⏳ Waiting 2 minutes until next check...
```

✅ **Processing Company:**
```
🎯 Found pending company: YourCompany
🤖 AGENT 1: RESEARCH ANALYST STARTED
📊 AGENT 2: FORMATTING SPECIALIST STARTED
✅ Report generation completed successfully!
```

❌ **Errors to Watch:**
```
❌ Error connecting to Google Sheets
❌ OpenAI API error
❌ Missing environment variable
```

### **4.3 Health Monitoring:**

Railway automatically monitors your app using the `/health` endpoint:
- **Healthy**: Green status, services running
- **Unhealthy**: Red status, automatic restart triggered

---

## 🔧 **Step 5: Troubleshooting**

### **5.1 Common Issues:**

**Issue**: "Module not found" errors
```
🔧 Solution: Check that all dependencies are in requirements.txt
```

**Issue**: "Google Sheets authentication failed"
```
🔧 Solution: Verify GOOGLE_CREDENTIALS_JSON is correct single-line JSON
```

**Issue**: "OpenAI API key invalid"
```
🔧 Solution: Check OPENAI_API_KEY in Railway variables
```

**Issue**: "No companies found in sheet"
```
🔧 Solution: Verify GOOGLE_SHEET_ID and GOOGLE_WORKSHEET_NAME
```

### **5.2 Restart Services:**

If something goes wrong:
1. **Go to Railway dashboard**
2. **Click "Deployments" tab**
3. **Click "Redeploy"** to restart everything

### **5.3 Check Logs:**

```bash
# In Railway dashboard, you can:
# 1. View live logs in real-time
# 2. Search logs by keyword
# 3. Download log files
# 4. Set up log alerts
```

---

## 🎉 **Step 6: You're Live!**

Once deployed successfully, your system will:

### **🔄 Automatic Processing:**
- **Monitor Google Sheets** every 2 minutes
- **Detect companies** with Status = "Promising"
- **Generate reports** using AI research + PDF extraction
- **Upload to Google Drive** (if configured)
- **Update sheet** with report links
- **Mark as "Generated"**

### **🌐 Web App Access:**
- **Railway URL**: `https://your-app-name.railway.app`
- **Health Check**: `https://your-app-name.railway.app/health`
- **Manual Reports**: Use the API endpoints

### **📊 24/7 Monitoring:**
- **Health checks** every 30 seconds
- **Automatic restarts** if services fail
- **Resource monitoring** in Railway dashboard
- **Log aggregation** for debugging

---

## 💰 **Railway Pricing**

- **Starter Plan**: $5/month (includes 512MB RAM, sufficient for this app)
- **Pro Plan**: $20/month (includes 8GB RAM, better for high volume)
- **Usage-based billing** for CPU and network

**Estimated Cost**: ~$5-10/month for typical usage

---

## 🔐 **Security Best Practices**

✅ **Environment Variables**: Never commit API keys to code  
✅ **HTTPS**: Railway provides SSL certificates automatically  
✅ **Service Account**: Use least-privilege Google Cloud permissions  
✅ **API Keys**: Rotate keys regularly  
✅ **Access Control**: Limit Railway project access  

---

## 📈 **Scaling Options**

### **If you need more capacity:**

1. **Upgrade Railway plan** for more RAM/CPU
2. **Add database** for storing processing history
3. **Add Redis** for caching and job queues
4. **Multiple regions** for global availability

### **If you need custom domains:**

1. **Add custom domain** in Railway dashboard
2. **Configure DNS** to point to Railway
3. **SSL certificates** handled automatically

---

## 🆘 **Getting Help**

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Community support
- **Railway Support**: Email support for paid plans
- **AXL Team**: Internal support for configuration issues

---

## 🎯 **Quick Deployment Checklist**

- [ ] Railway account created
- [ ] Repository connected to Railway
- [ ] All environment variables set
- [ ] `GOOGLE_CREDENTIALS_JSON` formatted correctly (single line)
- [ ] Build and deployment successful
- [ ] Health check endpoint responding
- [ ] Automation logs showing "Checking for new companies..."
- [ ] Test company processed successfully
- [ ] Reports generated and uploaded
- [ ] Google Sheet updated with links

**🎉 Once all items are checked, your 24/7 automated report generator is live!** 