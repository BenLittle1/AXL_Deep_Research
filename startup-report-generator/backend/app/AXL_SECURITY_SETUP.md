# AXL Team Access Configuration for Reports

The system now supports **AXL organization-only access** to protect your startup research reports. Here's how to configure it:

## 🔧 Configuration File

Edit `startup-report-generator/backend/app/axl_config.py` to set up your team access:

### Option 1: Domain-Based Access (Recommended)
If AXL has a Google Workspace domain (e.g., @axl.vc):

```python
AXL_DOMAIN = "axl.vc"  # Your actual domain
PREFERRED_ACCESS_MODE = "domain"
```

**Pros:** Most secure and convenient. Anyone with an @axl.vc email can access.  
**Cons:** Requires Google Workspace subscription.

### Option 2: Individual Email Access
If you don't have Google Workspace, list specific team emails:

```python
AXL_DOMAIN = None  # Set to None
AXL_TEAM_EMAILS = [
    "ben.little@axl.vc",
    "first.last@axl.vc", 
    "analyst@axl.vc"
]
PREFERRED_ACCESS_MODE = "email"
```

**Pros:** Works with any email addresses.  
**Cons:** Must manually maintain email list.

### Option 3: Public Access (Not Recommended)
For testing or if you want the old behavior:

```python
PREFERRED_ACCESS_MODE = "public"
```

## 🔐 Security Levels

1. **Domain**: Only people with @axl.vc emails can access
2. **Email**: Only specific individuals you list can access  
3. **Public**: Anyone with the link can access (old behavior)

## 🚀 How It Works

1. When reports are uploaded to Google Drive, the system automatically sets permissions
2. **Domain mode**: Restricts to your organization domain
3. **Email mode**: Grants access to specific team members only
4. **Fallback**: If domain fails, tries email list; if email list empty, falls back to public

## ⚙️ Quick Setup

1. Open `axl_config.py`
2. Set your domain OR add team emails
3. Choose your preferred access mode
4. Run the report generation - permissions apply automatically!

## 🔍 Verification

After generating reports:
- Domain access: Try accessing with non-AXL email (should be denied)
- Email access: Only listed team members can view
- Check the console output for permission confirmation

---
**Security Note:** Domain-based access is most secure and scales automatically as your team grows! 