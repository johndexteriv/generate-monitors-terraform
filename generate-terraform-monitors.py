#!/usr/bin/env python3
"""
Script to fetch Groundcover monitors and generate Terraform configuration.
Outputs to terraform.tf with provider configuration included.
Usage:
    python generate-terraform-monitors.py
"""

import os
import json
import urllib.request
import urllib.error
import time
import re
from typing import Optional, List, Dict, Tuple

# Configuration
API_KEY = os.getenv("GROUNDCOVER_API_KEY", "your-api-key-here")
BACKEND_ID = os.getenv("GROUNDCOVER_BACKEND_ID", "your-backend-id-here")
BASE_URL = os.getenv("GROUNDCOVER_BASE_URL", "https://app.groundcover.com")

def make_request(url: str, method: str = "GET", data: Optional[bytes] = None) -> Optional[Dict]:
    """Make an HTTP request with authentication."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Backend-Id": BACKEND_ID,
        "Content-Type": "application/json"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, data=data, method=method)
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            if status_code not in [200, 201]:
                error_body = response.read().decode('utf-8')
                return None
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
    except Exception:
        return None

def fetch_monitors() -> Tuple[Optional[List[Dict]], Optional[str]]:
    """Fetch monitors from Groundcover API.
    
    Returns:
        Tuple of (monitors_list, successful_endpoint) or (None, None) if failed.
    """
    endpoint = f"{BASE_URL}/api/monitors/summary/query"
    method = "POST"
    post_data = json.dumps({}).encode('utf-8')
    
    monitors = make_request(endpoint, method=method, data=post_data)
    successful_endpoint = f"{method} {endpoint}"
    
    if monitors is None:
        return None, None
    
    if isinstance(monitors, list):
        return monitors, successful_endpoint
    elif isinstance(monitors, dict):
        for key in ['results', 'data', 'monitors', 'items']:
            if key in monitors:
                return monitors[key], successful_endpoint
        return [monitors], successful_endpoint
    return None, None

def sanitize_resource_name(name: str) -> str:
    """Convert monitor name to valid Terraform resource name."""
    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    if name and not name[0].isalpha():
        name = 'monitor_' + name
    if not name:
        name = 'monitor'
    return name

def format_yaml_value(value) -> str:
    """Format a value for YAML output."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if any(char in value for char in ['"', "'", '\n', '\r', '\\', ':', '#']):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        return value
    else:
        return str(value)

def dict_to_yaml(data: dict, indent: int = 0) -> str:
    """Convert dictionary to YAML string format."""
    lines = []
    indent_str = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{indent_str}{key}:")
            nested = dict_to_yaml(value, indent + 1)
            if nested:
                lines.append(nested)
        elif isinstance(value, list):
            if not value:
                lines.append(f"{indent_str}{key}: []")
            else:
                lines.append(f"{indent_str}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{indent_str}  -")
                        nested = dict_to_yaml(item, indent + 2)
                        if nested:
                            nested_lines = nested.split('\n')
                            for nl in nested_lines:
                                if nl.strip():
                                    lines.append(f"  {nl}")
                    else:
                        lines.append(f"{indent_str}  - {format_yaml_value(item)}")
        else:
            lines.append(f"{indent_str}{key}: {format_yaml_value(value)}")
    
    return "\n".join(lines)

def convert_interval_to_yaml(interval_obj: dict) -> dict:
    """Convert interval object to YAML format."""
    if not interval_obj:
        return {"interval": "1m0s", "pendingFor": "0s"}
    return {
        "interval": interval_obj.get("interval", "1m0s"),
        "pendingFor": interval_obj.get("for", "0s")
    }

def convert_query_to_yaml(query: dict) -> dict:
    """Convert query object to YAML format."""
    yaml_query = {}
    
    if "name" in query:
        yaml_query["name"] = query["name"]
    
    if "dataType" in query:
        yaml_query["dataType"] = query["dataType"]
    elif "datasourceType" in query:
        ds_type = query["datasourceType"]
        if ds_type == "prometheus":
            yaml_query["dataType"] = "metrics"
        elif ds_type == "logs":
            yaml_query["dataType"] = "logs"
        elif ds_type == "traces":
            yaml_query["dataType"] = "traces"
        else:
            yaml_query["dataType"] = ds_type
    
    if "expression" in query:
        yaml_query["expr"] = query["expression"]
    elif "expr" in query:
        yaml_query["expr"] = query["expr"]
    
    if "editorMode" in query:
        yaml_query["editorMode"] = query["editorMode"]
    elif "mode" in query:
        yaml_query["editorMode"] = query["mode"]
    
    if "pipeline" in query:
        yaml_query["pipeline"] = query["pipeline"]
    
    return yaml_query

def convert_model_to_yaml(model: dict) -> dict:
    """Convert model object to YAML format."""
    yaml_model = {}
    
    if "queries" in model:
        yaml_model["queries"] = [convert_query_to_yaml(q) for q in model["queries"]]
    
    if "thresholds" in model:
        yaml_model["thresholds"] = model["thresholds"]
    
    return yaml_model

def monitor_to_yaml(monitor: dict) -> str:
    """Convert monitor JSON to YAML string for Terraform."""
    yaml_data = {}
    
    if "title" in monitor:
        yaml_data["title"] = monitor["title"]
    
    display = {}
    if "header" in monitor:
        display["header"] = monitor["header"]
    if "resourceLabels" in monitor:
        display["resourceHeaderLabels"] = monitor["resourceLabels"]
    if "contextLabels" in monitor:
        display["contextHeaderLabels"] = monitor["contextLabels"]
    if "description" in monitor:
        display["description"] = monitor.get("description", "")
    
    if display:
        yaml_data["display"] = display
    
    if "severity" in monitor:
        severity = monitor["severity"]
        yaml_data["severity"] = severity.upper() if isinstance(severity, str) else severity
    
    if "measurementType" in monitor:
        yaml_data["measurementType"] = monitor["measurementType"]
    
    if "model" in monitor:
        yaml_data["model"] = convert_model_to_yaml(monitor["model"])
    
    if "executionErrorState" in monitor:
        yaml_data["executionErrorState"] = monitor["executionErrorState"]
    
    if "interval" in monitor:
        yaml_data["evaluationInterval"] = convert_interval_to_yaml(monitor["interval"])
    
    return dict_to_yaml(yaml_data)

def generate_terraform_resource(monitor: dict, resource_name: str) -> str:
    """Generate Terraform resource block for a monitor."""
    monitor_yaml = monitor_to_yaml(monitor)
    
    return f'''resource "groundcover_monitor" "{resource_name}" {{
  monitor_yaml = <<-YAML
{monitor_yaml}  YAML
}}
'''

def main():
    """Main function."""
    print("🚀 Fetching monitors from Groundcover API...")
    print(f"Using Backend ID: {BACKEND_ID}\n")
    
    monitors, successful_endpoint = fetch_monitors()
    
    if monitors is None or len(monitors) == 0:
        print("❌ Error: Failed to fetch monitors from API")
        print("\nPossible issues:")
        print("   1. Check your API credentials (API_KEY and BACKEND_ID)")
        print("   2. Verify network connectivity")
        print("   3. Check API endpoint availability")
        print(f"   4. Verify Backend ID is correct: {BACKEND_ID}")
        exit(1)
    
    print(f"✅ Found {len(monitors)} monitor(s)")
    if successful_endpoint:
        print(f"📡 Successfully fetched from: {successful_endpoint}")
    print(f"🔄 Converting to Terraform format...\n")
    
    # Generate Terraform resources
    terraform_resources = []
    resource_names = set()
    
    for i, monitor in enumerate(monitors, 1):
        title = monitor.get('title', 'unnamed')
        resource_name = sanitize_resource_name(title)
        
        # Handle duplicates
        original_name = resource_name
        counter = 1
        while resource_name in resource_names:
            resource_name = f"{original_name}_{counter}"
            counter += 1
        
        resource_names.add(resource_name)
        terraform = generate_terraform_resource(monitor, resource_name)
        terraform_resources.append(terraform)
        
        print(f"  [{i}/{len(monitors)}] {title} -> {resource_name}")
    
    # Write to terraform.tf
    output_file = "terraform.tf"
    print(f"\n💾 Writing to {output_file}...")
    
    with open(output_file, 'w') as f:
        # Write Terraform configuration header
        f.write('''terraform {
  required_providers {
    groundcover = {
      source  = "registry.terraform.io/groundcover-com/groundcover"
      version = ">= 0.0.0"
    }
  }
}

provider "groundcover" {
  api_key    = var.groundcover_api_key
  backend_id = var.groundcover_backend_id
}

variable "groundcover_api_key" {
  type        = string
  description = "groundcover API Key"
  sensitive   = true
}

variable "groundcover_backend_id" {
  type        = string
  description = "groundcover Backend ID"
}

''')
        
        # Write all monitor resources
        for terraform in terraform_resources:
            f.write(terraform)
            f.write("\n")
    
    print(f"✅ Successfully generated {len(terraform_resources)} Terraform resources")
    print(f"📄 Saved to: {output_file}")
    print(f"\n💡 To use this file:")
    print(f"   export TF_VAR_groundcover_api_key='{API_KEY}'")
    print(f"   export TF_VAR_groundcover_backend_id='{BACKEND_ID}'")
    print(f"   terraform init")
    print(f"   terraform plan")

if __name__ == "__main__":
    main()

