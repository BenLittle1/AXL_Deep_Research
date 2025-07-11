/**
 * Google Sheets to Airtable Sync Script
 * 
 * This script automatically syncs your Google Sheet data to Airtable.
 * It can run on a schedule or be triggered by sheet changes.
 * 
 * Setup Instructions:
 * 1. Go to script.google.com
 * 2. Create a new project
 * 3. Paste this code
 * 4. Update the configuration below
 * 5. Set up triggers for automatic sync
 */

// ====== CONFIGURATION - UPDATE THESE VALUES ======
const AIRTABLE_CONFIG = {
  baseId: 'YOUR_AIRTABLE_BASE_ID',  // Find in Airtable API docs
  tableName: 'YOUR_TABLE_NAME',     // Name of your Airtable table
  apiKey: 'YOUR_AIRTABLE_API_KEY'   // Create in Airtable account settings
};

// Field mapping: Google Sheet column -> Airtable field name
const FIELD_MAPPING = {
  'Company Name': 'Company Name',
  'Status': 'Status', 
  'Website': 'Website',
  'Problem Statement': 'Problem Statement',
  'Problem Statement Commentary': 'Problem Commentary',
  'Problem Statement Score': 'Problem Score',
  'Industry': 'Industry',
  'Competitors': 'Competitors',
  'Target Audience': 'Target Audience',
  'MVP': 'MVP Status',
  'Progress': 'Product Progress',
  'Founder Fit': 'Founder Fit',
  'Team Growth': 'Team Growth',
  'Traction': 'Traction',
  'Pricing': 'Pricing Model',
  'Location': 'Location',
  'PDF_URL': 'PDF URL',
  'One-Pager': 'One-Pager Link',
  'Deep-Dive': 'Deep-Dive Link',
  'Generated': 'Reports Generated'
};

// Sync settings
const SYNC_CONFIG = {
  skipHeaderRow: true,
  batchSize: 10,  // Process 10 records at a time
  createNewRecords: true,
  updateExistingRecords: true,
  uniqueField: 'Company Name'  // Field to match existing records
};

/**
 * Main sync function - call this to sync all data
 */
async function syncToAirtable() {
  try {
    console.log('🔄 Starting Google Sheets to Airtable sync...');
    
    // Get the active spreadsheet and sheet
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getActiveSheet();
    
    // Get all data from the sheet
    const data = sheet.getDataRange().getValues();
    if (data.length === 0) {
      console.log('📭 No data found in sheet');
      return;
    }
    
    const headers = data[0];
    const rows = SYNC_CONFIG.skipHeaderRow ? data.slice(1) : data;
    
    console.log(`📊 Found ${rows.length} rows to sync`);
    
    // Get existing Airtable records to avoid duplicates
    const existingRecords = await getExistingAirtableRecords();
    console.log(`📋 Found ${existingRecords.length} existing Airtable records`);
    
    // Process rows in batches
    let processedCount = 0;
    let createdCount = 0;
    let updatedCount = 0;
    let errorCount = 0;
    
    for (let i = 0; i < rows.length; i += SYNC_CONFIG.batchSize) {
      const batch = rows.slice(i, i + SYNC_CONFIG.batchSize);
      
      console.log(`🔄 Processing batch ${Math.floor(i / SYNC_CONFIG.batchSize) + 1}...`);
      
      for (const row of batch) {
        try {
          const record = convertRowToAirtableRecord(headers, row);
          
          if (!record || !record.fields[SYNC_CONFIG.uniqueField]) {
            console.log('⏭️ Skipping empty or invalid row');
            continue;
          }
          
          // Check if record exists
          const existingRecord = findExistingRecord(existingRecords, record.fields[SYNC_CONFIG.uniqueField]);
          
          if (existingRecord && SYNC_CONFIG.updateExistingRecords) {
            // Update existing record
            await updateAirtableRecord(existingRecord.id, record.fields);
            updatedCount++;
            console.log(`✅ Updated: ${record.fields[SYNC_CONFIG.uniqueField]}`);
          } else if (!existingRecord && SYNC_CONFIG.createNewRecords) {
            // Create new record
            await createAirtableRecord(record.fields);
            createdCount++;
            console.log(`✅ Created: ${record.fields[SYNC_CONFIG.uniqueField]}`);
          } else {
            console.log(`⏭️ Skipped: ${record.fields[SYNC_CONFIG.uniqueField]}`);
          }
          
          processedCount++;
          
        } catch (error) {
          console.error(`❌ Error processing row: ${error.message}`);
          errorCount++;
        }
      }
      
      // Small delay between batches to avoid rate limits
      Utilities.sleep(500);
    }
    
    console.log('✅ Sync completed!');
    console.log(`📊 Summary: ${processedCount} processed, ${createdCount} created, ${updatedCount} updated, ${errorCount} errors`);
    
    // Optional: Send notification email
    // sendSyncNotification(createdCount, updatedCount, errorCount);
    
  } catch (error) {
    console.error('❌ Sync failed:', error.message);
    console.error(error.stack);
    
    // Optional: Send error notification
    // sendErrorNotification(error.message);
  }
}

/**
 * Convert Google Sheets row to Airtable record format
 */
function convertRowToAirtableRecord(headers, row) {
  const fields = {};
  
  for (let i = 0; i < headers.length && i < row.length; i++) {
    const sheetHeader = headers[i];
    const airtableField = FIELD_MAPPING[sheetHeader];
    
    if (airtableField && row[i] !== '') {
      let value = row[i];
      
      // Handle different data types
      if (value instanceof Date) {
        value = value.toISOString().split('T')[0]; // Convert to YYYY-MM-DD
      } else if (typeof value === 'number') {
        value = value.toString();
      } else {
        value = value.toString().trim();
      }
      
      fields[airtableField] = value;
    }
  }
  
  return { fields: fields };
}

/**
 * Get existing records from Airtable
 */
async function getExistingAirtableRecords() {
  try {
    const url = `https://api.airtable.com/v0/${AIRTABLE_CONFIG.baseId}/${AIRTABLE_CONFIG.tableName}`;
    
    const response = UrlFetchApp.fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${AIRTABLE_CONFIG.apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());
      return data.records || [];
    } else {
      console.error('❌ Failed to fetch existing records:', response.getContentText());
      return [];
    }
  } catch (error) {
    console.error('❌ Error fetching existing records:', error.message);
    return [];
  }
}

/**
 * Find existing record by unique field
 */
function findExistingRecord(existingRecords, uniqueValue) {
  return existingRecords.find(record => 
    record.fields[SYNC_CONFIG.uniqueField] === uniqueValue
  );
}

/**
 * Create new record in Airtable
 */
async function createAirtableRecord(fields) {
  const url = `https://api.airtable.com/v0/${AIRTABLE_CONFIG.baseId}/${AIRTABLE_CONFIG.tableName}`;
  
  const payload = {
    fields: fields
  };
  
  const response = UrlFetchApp.fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${AIRTABLE_CONFIG.apiKey}`,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  });
  
  if (response.getResponseCode() !== 200) {
    throw new Error(`Airtable API error: ${response.getContentText()}`);
  }
  
  return JSON.parse(response.getContentText());
}

/**
 * Update existing record in Airtable
 */
async function updateAirtableRecord(recordId, fields) {
  const url = `https://api.airtable.com/v0/${AIRTABLE_CONFIG.baseId}/${AIRTABLE_CONFIG.tableName}/${recordId}`;
  
  const payload = {
    fields: fields
  };
  
  const response = UrlFetchApp.fetch(url, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${AIRTABLE_CONFIG.apiKey}`,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload)
  });
  
  if (response.getResponseCode() !== 200) {
    throw new Error(`Airtable API error: ${response.getContentText()}`);
  }
  
  return JSON.parse(response.getContentText());
}

/**
 * Test function - run this to test the configuration
 */
function testAirtableConnection() {
  console.log('🧪 Testing Airtable connection...');
  
  try {
    const existingRecords = getExistingAirtableRecords();
    console.log(`✅ Connection successful! Found ${existingRecords.length} records`);
    
    // Test field mapping
    console.log('🔄 Testing field mapping...');
    const sheet = SpreadsheetApp.getActiveSheet();
    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    
    console.log('📋 Available Google Sheet columns:');
    headers.forEach((header, index) => {
      const mapped = FIELD_MAPPING[header];
      console.log(`  ${index + 1}. "${header}" -> ${mapped ? `"${mapped}"` : 'NOT MAPPED'}`);
    });
    
  } catch (error) {
    console.error('❌ Connection test failed:', error.message);
  }
}

/**
 * Sync only new/changed rows (efficient for scheduled runs)
 */
function syncRecentChanges() {
  // This function can be enhanced to only sync rows modified in the last X hours
  // For now, it calls the full sync
  syncToAirtable();
}

/**
 * Manual trigger for specific row - useful for testing
 */
function syncSpecificRow(rowNumber) {
  console.log(`🔧 Manual sync for row ${rowNumber}`);
  
  const sheet = SpreadsheetApp.getActiveSheet();
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const row = sheet.getRange(rowNumber, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  const record = convertRowToAirtableRecord(headers, row);
  console.log('📊 Record to sync:', record);
  
  // Add actual sync logic here if needed for testing
} 