"""
Modal Webhook for Skills Dashboard
Executes skills via directives + execution scripts
"""
import modal
import json
import sys
import os
from pathlib import Path

app = modal.App("claude-orchestrator")

# Mount the entire workspace so we can access directives and execution scripts
workspace_mount = modal.Mount.from_local_dir(
    Path(__file__).parent.parent,
    remote_path="/workspace"
)

@app.function(
    image=modal.Image.debian_slim().pip_install(
        "requests", "beautifulsoup4", "lxml", "pandas", 
        "openai", "anthropic", "google-generativeai",
        "apify-client", "python-dotenv"
    ),
    mounts=[workspace_mount],
    secrets=[modal.Secret.from_name("automation-secrets")],
    timeout=600
)
@modal.web_endpoint(method="POST")
def directive(data: dict):
    """
    Execute a skill via its directive and script
    
    Expected POST body:
    {
        "slug": "amazon_product_scraper",  # skill ID
        "inputs": { "keyword": "wireless mouse", "max_results": 10 }
    }
    """
    try:
        slug = data.get("slug")
        inputs = data.get("inputs", {})
        
        if not slug:
            return {
                "success": False,
                "error": "Missing 'slug' parameter"
            }
        
        # Load webhooks.json to find the right script
        webhooks_path = Path("/workspace/execution/webhooks.json")
        
        if not webhooks_path.exists():
            return {
                "success": False,
                "error": "webhooks.json not found",
                "tip": "Create execution/webhooks.json to map skills to scripts"
            }
        
        with open(webhooks_path) as f:
            webhooks = json.load(f)
        
        if slug not in webhooks:
            return {
                "success": False,
                "error": f"Skill '{slug}' not configured in webhooks.json",
                "available_skills": list(webhooks.keys())
            }
        
        config = webhooks[slug]
        script_path = Path(f"/workspace/{config['script']}")
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script not found: {config['script']}",
                "tip": "Create the execution script or update webhooks.json"
            }
        
        # Execute the Python script with inputs
        import subprocess
        result = subprocess.run(
            [sys.executable, str(script_path), json.dumps(inputs)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd="/workspace"
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or "Script execution failed",
                "stdout": result.stdout,
                "returncode": result.returncode
            }
        
        # Try to parse output as JSON, fallback to raw text
        try:
            output_data = json.loads(result.stdout)
        except:
            output_data = {"raw_output": result.stdout}
        
        return {
            "success": True,
            "skill": slug,
            "result": output_data,
            "timestamp": modal.utils.now_utc().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }


@app.function()
@modal.web_endpoint(method="GET")
def list_webhooks():
    """List all available skills"""
    try:
        webhooks_path = Path("/workspace/execution/webhooks.json")
        with open(webhooks_path) as f:
            webhooks = json.load(f)
        return {
            "success": True,
            "skills": webhooks
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
