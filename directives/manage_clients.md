# Client Management Directive

## Goal
Organize and track client information, workflows, and project history in a structured folder system.

## Client Folder Structure

Each client gets a dedicated folder:
```
clients/
├── {client-name}/
│   ├── info.json              # Client metadata
│   ├── notes.md               # General notes and updates
│   ├── workflows/             # Automation workflows built for this client
│   │   ├── workflow-name.md   # Workflow documentation
│   │   └── config.json        # Workflow configuration
│   ├── communications/        # Email templates, meeting notes
│   │   └── emails/
│   ├── deliverables/          # Links to Google Sheets, Slides, etc.
│   └── history.log            # Timeline of activities
```

## Client Info Schema (info.json)

```json
{
  "client_name": "Company Name",
  "contact_name": "Primary Contact",
  "contact_email": "email@company.com",
  "phone": "555-123-4567",
  "website": "https://company.com",
  "status": "active|onboarding|paused|completed",
  "start_date": "2025-01-15",
  "industry": "E-commerce",
  "tags": ["automation", "ecommerce", "shopify"],
  "workflows": [
    {
      "name": "Order Processing Automation",
      "status": "live",
      "created": "2025-01-20",
      "description": "Automated order fulfillment"
    }
  ],
  "deliverables": [
    {
      "name": "Project Dashboard",
      "type": "google_sheet",
      "url": "https://docs.google.com/spreadsheets/...",
      "created": "2025-01-20"
    }
  ],
  "notes": "Weekly check-ins on Fridays"
}
```

## Inputs
- `client_name`: Company name
- `contact_name`: Primary contact person (optional)
- `contact_email`: Email address
- `action`: create|update|archive|list

## Process

### Create New Client
Use: `execution/create_client.py`

1. Generate client slug (lowercase, no spaces)
2. Create folder structure
3. Initialize info.json with provided data
4. Create empty notes.md
5. Initialize history.log with creation timestamp
6. Return client folder path

### Update Client Info
Use: `execution/update_client.py`

1. Load existing info.json
2. Update specified fields
3. Log change to history.log
4. Save updated info.json

### Add Workflow
Use: `execution/add_workflow.py`

1. Create workflow documentation file
2. Update client's info.json workflows array
3. Log to history.log

### List Clients
Use: `execution/list_clients.py`

1. Scan clients/ directory
2. Read each info.json
3. Return summary table (name, status, workflows count, last activity)

### Archive Client
1. Update status to "archived"
2. Move to clients/_archived/
3. Log archive action

## Outputs
- Structured client folders
- JSON metadata for querying
- Activity history logs
- Easy-to-navigate file system

## Tools Used
1. `execution/create_client.py` - Initialize new client folder
2. `execution/update_client.py` - Update client information
3. `execution/add_workflow.py` - Document new workflow for client
4. `execution/list_clients.py` - View all clients and status
5. `execution/log_activity.py` - Add timestamped entries to history

## Edge Cases

### Duplicate Client
- Check if client folder exists
- Option to update existing or create with suffix

### Missing Data
- Only client_name and contact_email required
- Other fields optional with sensible defaults

### Migration
- Existing clients can be imported
- Bulk creation supported via CSV

## Best Practices

1. **Consistent Naming**: Use company name, not project name
2. **Regular Updates**: Log all significant interactions
3. **Workflow Documentation**: Document every automation built
4. **Deliverable Links**: Always link to Google Docs/Sheets
5. **Status Tracking**: Keep client status current

## Automation Integration

- **Onboarding**: Auto-create client folder when onboarding
- **Workflow Creation**: Auto-log when deploying new automation
- **Email Tracking**: Log all onboarding/update emails sent
- **Calendar Events**: Log meetings and calls

## Example Usage

```bash
# Create new client
python execution/create_client.py --name "Acme Corp" --email "john@acme.com" --contact "John Smith"

# Add workflow
python execution/add_workflow.py --client "acme-corp" --workflow "inventory-sync" --description "Sync inventory between Shopify and warehouse"

# List all clients
python execution/list_clients.py

# Update client status
python execution/update_client.py --client "acme-corp" --status "active"

# Log activity
python execution/log_activity.py --client "acme-corp" --message "Kickoff call completed - scoped 3 workflows"
```

## Success Criteria
- [ ] Easy to find any client's information
- [ ] Complete workflow documentation
- [ ] Activity history for reference
- [ ] Quick status overview of all clients
- [ ] Searchable and scalable

## Future Enhancements
- Web dashboard for client overview
- Automatic report generation
- Integration with time tracking
- Revenue tracking per client
- Workflow templates library
