/**
 * Google Apps Script Trigger for Automatic Report Generation
 * 
 * This script automatically triggers report generation when new companies
 * are added to your Google Sheet (e.g., from Airtable automation).
 * 
 * Setup Instructions:
 * 1. Go to script.google.com
 * 2. Create a new project
 * 3. Paste this code
 * 4. Update YOUR_API_ENDPOINT below
 * 5. Set up trigger: Edit > Current project's triggers > Add trigger
 *    - Function: onNewRowAdded
 *    - Event source: From spreadsheet
 *    - Event type: On form submit OR On edit (choose based on how Airtable adds data)
 * 
 * This will call your report generation API immediately when new rows appear.
 */

// Configuration - UPDATE THESE VALUES
const API_ENDPOINT = 'YOUR_API_ENDPOINT_HERE'; // e.g., 'https://your-domain.com' or ngrok URL
const COMPANY_NAME_COLUMN = 'A'; // Column containing company names
const STATUS_COLUMN = 'B'; // Column containing status (e.g., "Reviewed - Promising")
const GENERATED_COLUMN = 'CV'; // Column that tracks if reports were generated (column 100)
const TARGET_STATUS = 'Reviewed - Promising'; // Status that should trigger report generation

/**
 * Main trigger function - called when spreadsheet is edited
 */
function onNewRowAdded(e) {
  try {
    console.log('🔔 Spreadsheet edit detected');
    
    // Get the edited range
    const range = e.range;
    const sheet = range.getSheet();
    const row = range.getRow();
    
    // Skip header row
    if (row <= 1) {
      console.log('📋 Header row edited, skipping');
      return;
    }
    
    // Get company data from the edited row
    const companyName = sheet.getRange(row, getColumnNumber(COMPANY_NAME_COLUMN)).getValue();
    const status = sheet.getRange(row, getColumnNumber(STATUS_COLUMN)).getValue();
    const generated = sheet.getRange(row, getColumnNumber(GENERATED_COLUMN)).getValue();
    
    console.log(`🏢 Row ${row}: ${companyName}, Status: ${status}, Generated: ${generated}`);
    
    // Check if this is a new company that needs processing
    if (companyName && 
        status === TARGET_STATUS && 
        (!generated || generated.toString().trim() === '')) {
      
      console.log(`✅ Triggering report generation for: ${companyName}`);
      triggerReportGeneration(companyName, row, sheet);
      
    } else {
      console.log(`⏭️ Skipping ${companyName}: already processed or wrong status`);
    }
    
  } catch (error) {
    console.error('❌ Error in onNewRowAdded:', error);
  }
}

/**
 * Trigger report generation via API call
 */
function triggerReportGeneration(companyName, rowNumber, sheet) {
  try {
    // Extract additional company data from the row
    const companyData = extractCompanyData(sheet, rowNumber);
    
    const payload = {
      sheet_id: sheet.getParent().getId(),
      worksheet_name: sheet.getName(),
      company_name: companyName,
      row_number: rowNumber,
      company_data: companyData,
      trigger_source: 'google_apps_script',
      timestamp: new Date().toISOString()
    };
    
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      payload: JSON.stringify(payload)
    };
    
    console.log('📡 Calling report generation API...');
    
    // Call your report generation endpoint
    const response = UrlFetchApp.fetch(`${API_ENDPOINT}/google-sheets-process`, options);
    const result = JSON.parse(response.getContentText());
    
    if (result.success) {
      console.log(`✅ Report generation triggered successfully for ${companyName}`);
      
      // Mark as processing started
      sheet.getRange(rowNumber, getColumnNumber(GENERATED_COLUMN))
           .setValue('Processing...');
      
    } else {
      console.error(`❌ Report generation failed for ${companyName}:`, result.error);
      
      // Mark as failed
      sheet.getRange(rowNumber, getColumnNumber(GENERATED_COLUMN))
           .setValue('Failed: ' + (result.error || 'Unknown error'));
    }
    
  } catch (error) {
    console.error('❌ Error calling report generation API:', error);
    
    // Mark as error in sheet
    sheet.getRange(rowNumber, getColumnNumber(GENERATED_COLUMN))
         .setValue('Error: ' + error.message);
  }
}

/**
 * Extract company data from the spreadsheet row
 */
function extractCompanyData(sheet, rowNumber) {
  // Get all data from the row
  const lastColumn = sheet.getLastColumn();
  const rowData = sheet.getRange(rowNumber, 1, 1, lastColumn).getValues()[0];
  const headers = sheet.getRange(1, 1, 1, lastColumn).getValues()[0];
  
  // Create company data object
  const companyData = {};
  
  for (let i = 0; i < headers.length && i < rowData.length; i++) {
    const header = headers[i];
    const value = rowData[i];
    
    if (header && value) {
      companyData[header] = value;
    }
  }
  
  return companyData;
}

/**
 * Convert column letter to number (A=1, B=2, etc.)
 */
function getColumnNumber(columnLetter) {
  let column = 0;
  for (let i = 0; i < columnLetter.length; i++) {
    column = column * 26 + (columnLetter.charCodeAt(i) - 'A'.charCodeAt(0) + 1);
  }
  return column;
}

/**
 * Test function - run this to test the setup
 */
function testTrigger() {
  console.log('🧪 Testing Google Apps Script trigger setup');
  console.log(`📊 API Endpoint: ${API_ENDPOINT}`);
  console.log(`📋 Target Status: ${TARGET_STATUS}`);
  
  // Test API connectivity
  try {
    const response = UrlFetchApp.fetch(`${API_ENDPOINT}/health`);
    console.log('✅ API is reachable');
  } catch (error) {
    console.error('❌ API not reachable:', error);
  }
}

/**
 * Manual trigger for specific row - useful for testing
 */
function manualTriggerForRow(rowNumber) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const companyName = sheet.getRange(rowNumber, getColumnNumber(COMPANY_NAME_COLUMN)).getValue();
  
  console.log(`🔧 Manual trigger for row ${rowNumber}: ${companyName}`);
  triggerReportGeneration(companyName, rowNumber, sheet);
} 