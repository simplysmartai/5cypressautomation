#!/usr/bin/env python3
"""
Add a workflow definition to a client project.
Usage: python add_workflow.py <client_slug> <workflow_name> [--description DESC]
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Get the project root (parent of execution/)
PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"


def add_workflow(slug: str, workflow_name: str, description: str = None, 
                 systems: list = None, triggers: list = None) -> dict:
    """
    Add a workflow definition to a client's project.
    
    Args:
        slug: Client slug/folder name
        workflow_name: Name of the workflow
        description: Description of what the workflow does
        systems: List of systems involved
        triggers: List of trigger events
    
    Returns:
        Created workflow metadata
    """
    client_dir = CLIENTS_DIR / slug
    workflows_dir = client_dir / "workflows"
    
    if not client_dir.exists():
        raise FileNotFoundError(f"Client '{slug}' not found at {client_dir}")
    
    # Create workflows directory if it doesn't exist
    workflows_dir.mkdir(exist_ok=True)
    
    # Create slug from workflow name
    workflow_slug = workflow_name.lower().replace(" ", "-").replace("_", "-")
    workflow_dir = workflows_dir / workflow_slug
    workflow_dir.mkdir(exist_ok=True)
    
    # Create workflow metadata
    workflow = {
        "name": workflow_name,
        "slug": workflow_slug,
        "description": description or f"Workflow: {workflow_name}",
        "status": "planned",  # planned, in-progress, testing, deployed
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "systems": systems or [],
        "triggers": triggers or [],
        "files": {
            "documentation": f"workflows/{workflow_slug}/README.md",
            "implementation": f"workflows/{workflow_slug}/implementation/"
        }
    }
    
    # Save workflow.json
    workflow_file = workflow_dir / "workflow.json"
    with open(workflow_file, "w") as f:
        json.dump(workflow, f, indent=2)
    
    # Create README template
    readme_content = f"""# {workflow_name}

## Overview

{description or 'Description of this workflow.'}

## Trigger

What initiates this workflow:
- {', '.join(triggers) if triggers else 'TBD'}

## Systems Involved

{chr(10).join(f'- {s}' for s in systems) if systems else '- TBD'}

## Process Flow

```
[Trigger] → [Step 1] → [Step 2] → [Output]
```

### Step 1: [Name]

Description of step 1.

### Step 2: [Name]

Description of step 2.

## Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| | | | |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| | | |

## Error Handling

- **Error scenario 1:** How it's handled
- **Error scenario 2:** How it's handled

## Testing

How to test this workflow.

## Deployment

Steps to deploy this workflow.

## Changelog

| Date | Change | By |
|------|--------|-----|
| {datetime.now().strftime('%Y-%m-%d')} | Initial creation | SSA |
"""
    
    readme_file = workflow_dir / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Create implementation directory
    impl_dir = workflow_dir / "implementation"
    impl_dir.mkdir(exist_ok=True)
    
    # Update info.json with workflow reference
    client_file = client_dir / "info.json"
    if client_file.exists():
        with open(client_file, "r") as f:
            client_data = json.load(f)
        
        if "workflows" not in client_data:
            client_data["workflows"] = []
        
        client_data["workflows"].append({
            "name": workflow_name,
            "slug": workflow_slug,
            "status": "planned",
            "added_at": datetime.now().isoformat()
        })
        client_data["updated_at"] = datetime.now().isoformat()
        
        with open(client_file, "w") as f:
            json.dump(client_data, f, indent=2)
    
    print(f"✅ Workflow '{workflow_name}' created for {slug}")
    print(f"   📁 Location: {workflow_dir}")
    print(f"   📄 README: {readme_file}")
    print(f"   📋 Metadata: {workflow_file}")
    
    return workflow


def main():
    parser = argparse.ArgumentParser(description="Add a workflow to a client project")
    parser.add_argument("slug", help="Client slug (folder name)")
    parser.add_argument("workflow_name", help="Name of the workflow")
    parser.add_argument("--description", "-d", help="Workflow description")
    parser.add_argument("--system", "-s", action="append", 
                        help="System involved (can be used multiple times)")
    parser.add_argument("--trigger", "-t", action="append",
                        help="Trigger event (can be used multiple times)")
    
    args = parser.parse_args()
    
    try:
        add_workflow(
            slug=args.slug,
            workflow_name=args.workflow_name,
            description=args.description,
            systems=args.system,
            triggers=args.trigger
        )
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
