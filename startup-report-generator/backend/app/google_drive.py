# app/google_drive.py
import os
import io
from typing import Dict, List, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth import default
import traceback

from .axl_config import AXL_DOMAIN, AXL_TEAM_EMAILS, PREFERRED_ACCESS_MODE

class GoogleDriveManager:
    """
    Manages Google Drive operations including uploading PDFs, setting permissions,
    and getting shareable links for AXL access.
    """
    
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.service = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Drive API client with authentication."""
        try:
            print("🔄 Initializing Google Drive client...")
            
            # Try Application Default Credentials first (for gcloud auth)
            try:
                credentials, project = default(scopes=self.SCOPES)
                print("✅ Using Application Default Credentials for Google Drive")
            except Exception as e:
                print(f"⚠️ Application Default Credentials failed: {e}")
                # You could add service account or other auth methods here
                raise Exception("Please run: gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/drive.file")
            
            # Build the service
            self.service = build('drive', 'v3', credentials=credentials)
            print("✅ Google Drive client initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Google Drive client: {e}")
            raise
    
    def upload_pdf_to_drive(
        self, 
        pdf_bytes: bytes, 
        filename: str, 
        folder_name: str = "AXL Startup Reports"
    ) -> Optional[Dict]:
        """
        Upload a PDF to Google Drive and return file info with shareable link.
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Name for the file in Drive
            folder_name: Drive folder to upload to (creates if doesn't exist)
            
        Returns:
            Dict with file_id, name, and shareable_link
        """
        try:
            print(f"📤 Uploading {filename} to Google Drive...")
            
            # Find or create the folder
            folder_id = self._get_or_create_folder(folder_name)
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id] if folder_id else []
            }
            
            # Upload the file
            media = MediaIoBaseUpload(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            file_id = file.get('id')
            print(f"✅ File uploaded successfully: {file_id}")
            
            # Set permissions for AXL access
            shareable_link = self._set_axl_permissions(file_id)
            
            return {
                'file_id': file_id,
                'name': filename,
                'shareable_link': shareable_link,
                'folder_name': folder_name
            }
            
        except Exception as e:
            print(f"❌ Error uploading {filename} to Drive: {e}")
            traceback.print_exc()
            return None
    
    def _get_or_create_folder(self, folder_name: str) -> Optional[str]:
        """Get existing folder or create new one."""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                folder_id = folders[0]['id']
                print(f"📁 Using existing folder: {folder_name} ({folder_id})")
                return folder_id
            else:
                # Create new folder
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                folder_id = folder.get('id')
                print(f"📁 Created new folder: {folder_name} ({folder_id})")
                return folder_id
                
        except Exception as e:
            print(f"❌ Error with folder operations: {e}")
            return None
    
    def _set_axl_permissions(self, file_id: str) -> str:
        """
        Set permissions for AXL organization access only and return shareable link.
        """
        try:
            print(f"🔐 Setting AXL organization-only permissions for file {file_id}...")
            
            # Get AXL configuration from config file
            axl_team_emails = AXL_TEAM_EMAILS
            axl_domain = AXL_DOMAIN
            access_mode = PREFERRED_ACCESS_MODE
            
            # Set permissions based on configured access mode
            if access_mode == "domain" and axl_domain:
                try:
                    # Domain-based permission (most secure and convenient)
                    print(f"🔒 Setting domain-based permission for {axl_domain}...")
                    domain_permission = {
                        'type': 'domain',
                        'role': 'reader',
                        'domain': axl_domain
                    }
                    
                    self.service.permissions().create(
                        fileId=file_id,
                        body=domain_permission
                    ).execute()
                    
                    print(f"✅ Domain permission set for {axl_domain}")
                    
                except Exception as domain_error:
                    print(f"⚠️ Domain permission failed: {domain_error}")
                    print("🔄 Falling back to individual email permissions...")
                    access_mode = "email"  # Fall back to email mode
            
            if access_mode == "email":
                if axl_team_emails:
                    print(f"🔒 Setting individual email permissions for {len(axl_team_emails)} team members...")
                    for email in axl_team_emails:
                        try:
                            email_permission = {
                                'type': 'user',
                                'role': 'reader',
                                'emailAddress': email
                            }
                            
                            self.service.permissions().create(
                                fileId=file_id,
                                body=email_permission,
                                sendNotificationEmail=False  # Don't spam team with notifications
                            ).execute()
                            
                            print(f"✅ Added permission for {email}")
                            
                        except Exception as email_error:
                            print(f"⚠️ Failed to add permission for {email}: {email_error}")
                else:
                    print("⚠️ No AXL team emails configured. Please add team emails to axl_config.py")
                    print("🔄 Using public access as fallback...")
                    access_mode = "public"  # Fall back to public
            
            if access_mode == "public":
                print("🔓 Setting public access (anyone with the link)...")
                public_permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                
                self.service.permissions().create(
                    fileId=file_id,
                    body=public_permission
                ).execute()
                
                print("✅ Public permission set")
            
            # Get the shareable link
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            shareable_link = file.get('webViewLink')
            print(f"✅ AXL organization permissions set. Shareable link: {shareable_link}")
            
            return shareable_link
            
        except Exception as e:
            print(f"❌ Error setting permissions: {e}")
            # Return a basic link even if permissions failed
            return f"https://drive.google.com/file/d/{file_id}/view"
    
    def batch_upload_reports(
        self, 
        report_files: List[Tuple[bytes, str]]
    ) -> List[Dict]:
        """
        Upload multiple PDF reports to Drive.
        
        Args:
            report_files: List of (pdf_bytes, filename) tuples
            
        Returns:
            List of upload results
        """
        results = []
        
        print(f"📤 Starting batch upload of {len(report_files)} reports...")
        
        for pdf_bytes, filename in report_files:
            result = self.upload_pdf_to_drive(pdf_bytes, filename)
            if result:
                results.append(result)
                print(f"✅ Uploaded: {filename}")
            else:
                print(f"❌ Failed: {filename}")
                results.append({
                    'name': filename,
                    'error': 'Upload failed'
                })
        
        print(f"📊 Batch upload completed: {len([r for r in results if 'error' not in r])}/{len(report_files)} successful")
        return results

def upload_reports_to_drive(
    report_data: List[Dict[str, any]]
) -> List[Dict]:
    """
    Convenience function to upload generated reports to Google Drive.
    
    Args:
        report_data: List of report dictionaries with 'pdf_bytes' and 'filename'
        
    Returns:
        List of upload results with shareable links
    """
    try:
        drive_manager = GoogleDriveManager()
        
        # Prepare files for upload
        files_to_upload = []
        for report in report_data:
            if 'pdf_bytes' in report and 'filename' in report:
                files_to_upload.append((report['pdf_bytes'], report['filename']))
        
        # Upload to Drive
        upload_results = drive_manager.batch_upload_reports(files_to_upload)
        
        return upload_results
        
    except Exception as e:
        print(f"❌ Error in upload_reports_to_drive: {e}")
        return [] 