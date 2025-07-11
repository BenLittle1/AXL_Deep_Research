"""
AXL Team Configuration for Google Drive Access
"""

# AXL Organization Settings
AXL_DOMAIN = "axl.vc"  # AXL's actual domain

# AXL Team Email Addresses
# Add all AXL team members who should have access to the reports
AXL_TEAM_EMAILS = [
    # Add team email addresses here, for example:
    # "ben.little@axl.vc",
    # "first.last@axl.vc",
    # "analyst@axl.vc",
    # "partner@axl.vc"
]

# Access Level Settings
# "domain" - Anyone in the AXL domain (requires Google Workspace)
# "email" - Only specific email addresses listed above
# "public" - Anyone with the link (least secure, not recommended)
PREFERRED_ACCESS_MODE = "domain"  # Change to "email" if no Google Workspace domain 