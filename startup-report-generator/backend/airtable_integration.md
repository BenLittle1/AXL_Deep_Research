# Airtable Integration Guide

## Overview
This guide explains how to set up automated report generation triggered by Airtable status changes.

## Required Airtable Fields

Your Airtable base should have these fields for optimal integration:

### Core Fields
- **Company Name** (`name`, `company_name`, or `Company`) - Required
- **Website** (`website`, `url`, or `Website`) - Optional
- **Workflow Status** - Should include "Reviewed - Promising" option

### Optional Fields for Enhanced Reports
- **Pitch Deck Notes** (`pitch_deck_notes`, `pitch_deck`) - Extracted content from pitch decks
- **Internal Notes** (`internal_notes`, `notes`, `Notes`) - Your team's research notes
- **Reports Generated** - Timestamp field to track when reports were created
- **Report Status** - Status field to track generation progress

## Airtable Automation Setup

### 1. Create Trigger
- **Type**: "When record matches conditions"
- **Table**: Your company tracking table
- **Condition**: When "Workflow" is "Reviewed - Promising"

### 2. Add Script Action
```javascript
// Get the triggered record data
let record = input.config();

// Extract company information
let companyName = record.name || record.company_name || record.Company;
let companyUrl = record.website || record.url || record.Website || '';
let pitchDeckContent = record.pitch_deck_notes || record.pitch_deck || '';
let internalNotes = record.internal_notes || record.notes || record.Notes || '';
let recordId = record.id || '';

// API Configuration
let apiUrl = 'YOUR_API_ENDPOINT_HERE/airtable-webhook';

let payload = {
    company_name: companyName,
    company_url: companyUrl,
    pitch_deck_content: pitchDeckContent,
    internal_notes: internalNotes,
    airtable_record_id: recordId,
    generate_both: true
};

console.log('Generating reports for:', companyName);

try {
    let response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    let result = await response.json();
    
    if (result.success) {
        console.log(`✅ Generated ${result.total_reports} reports for ${result.company_name}`);
        
        // Optional: Update record with generation timestamp
        // You can create these fields in Airtable:
        // - Reports Generated (Date field)
        // - Report Status (Single select: Pending, Generated, Failed)
        
    } else {
        console.error(`❌ Failed: ${result.error}`);
    }
    
} catch (error) {
    console.error('❌ Network error:', error.message);
}
```

## API Endpoints

### `/airtable-webhook` (POST)
Endpoint specifically designed for Airtable integration.

**Request Body:**
```json
{
    "company_name": "Tesla",
    "company_url": "https://tesla.com",
    "pitch_deck_content": "Optional pitch deck notes...",
    "internal_notes": "Optional internal research...",
    "airtable_record_id": "rec123abc",
    "generate_both": true
}
```

**Response:**
```json
{
    "success": true,
    "company_name": "Tesla",
    "airtable_record_id": "rec123abc",
    "reports_generated": [
        {
            "type": "one_pager",
            "filename": "Tesla_one_pager.pdf",
            "size_bytes": 25600
        },
        {
            "type": "deep_dive",
            "filename": "Tesla_deep_dive.pdf",
            "size_bytes": 51200
        }
    ],
    "total_reports": 2,
    "company_data": {
        "tagline": "Accelerating the world's transition to sustainable energy",
        "founded_year": "2003",
        "total_funding": "$25.5B",
        "valuation": "$800B",
        "team_size": 15
    }
}
```

## Deployment Options

### Development (ngrok)
```bash
# Terminal 1: Start backend
cd startup-report-generator/backend
uvicorn app.main:app --reload

# Terminal 2: Expose with ngrok
ngrok http 8000
# Use the https URL in your Airtable script
```

### Production Deployment
Recommended platforms:
- **Heroku**: Easy deployment with free tier
- **Railway**: Modern platform with automatic deployments
- **Render**: Free tier with automatic builds
- **DigitalOcean App Platform**: Scalable with competitive pricing

## Testing Your Integration

1. **Test the API directly:**
   ```bash
   curl -X POST "YOUR_API_URL/airtable-webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "Test Company",
       "company_url": "https://test.com",
       "generate_both": true
     }'
   ```

2. **Test the Airtable trigger:**
   - Change a company's status to "Reviewed - Promising"
   - Check the automation logs in Airtable
   - Verify reports are generated in your backend directory

## Troubleshooting

### Common Issues
1. **CORS errors**: Ensure `allow_origins=["*"]` is set in backend
2. **Field mapping**: Check that your Airtable field names match the script
3. **API timeout**: Large companies may take 30+ seconds to process
4. **Rate limiting**: Perplexity API has rate limits - space out multiple triggers

### Debug Tips
- Check Airtable automation logs for script errors
- Monitor backend logs for API errors
- Test individual companies first before bulk processing
- Verify your Perplexity API key is working

## Security Considerations

- Use HTTPS endpoints in production
- Consider adding API authentication for production use
- Store sensitive data (API keys) in environment variables
- Implement rate limiting to prevent abuse

## Next Steps

1. Complete your current Airtable trigger setup
2. Deploy your backend to a cloud service
3. Test with a few companies manually
4. Scale up to automated processing
5. Consider adding email notifications or file storage integration 