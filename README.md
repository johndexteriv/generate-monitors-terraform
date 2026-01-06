# Generate Terraform Monitors

A Python script that fetches monitors from the Groundcover API and generates Terraform configuration files for managing them as infrastructure-as-code.

## Overview

This script connects to the Groundcover API, retrieves all configured monitors, and converts them into Terraform resource definitions. The generated Terraform file can be used to manage your Groundcover monitors declaratively.

## Prerequisites

- Python 3.x
- Groundcover API Key
- Groundcover Backend ID
- Network access to your Groundcover instance

## Configuration

The script uses environment variables for configuration:

- `GROUNDCOVER_API_KEY`: Your Groundcover API key (required)
- `GROUNDCOVER_BACKEND_ID`: Your Groundcover backend ID (required)
- `GROUNDCOVER_BASE_URL`: Base URL for your Groundcover instance (defaults to `https://app.groundcover.com`)

## Usage

### 1. Set Environment Variables

```bash
export GROUNDCOVER_API_KEY="your-api-key-here"
export GROUNDCOVER_BACKEND_ID="your-backend-id-here"
```

### 2. Run the Script

```bash
python3 generate-terraform-monitors.py
```

Or make it executable and run directly:

```bash
chmod +x generate-terraform-monitors.py
./generate-terraform-monitors.py
```

### 3. Output

The script generates a `terraform.tf` file containing:

- Terraform provider configuration for Groundcover
- Variable definitions for API credentials
- Resource blocks for each monitor found in your Groundcover instance

### 4. Use the Generated Terraform

After generating the Terraform file, you can use it to manage your monitors:

```bash
# Set Terraform variables (or use terraform.tfvars)
export TF_VAR_groundcover_api_key="your-api-key-here"
export TF_VAR_groundcover_backend_id="your-backend-id-here"

# Initialize Terraform
terraform init

# Review the planned changes
terraform plan

# Apply the configuration
terraform apply
```

## How It Works

1. **API Connection**: The script attempts multiple API endpoints to fetch monitors from Groundcover
2. **Data Transformation**: Converts monitor JSON data into YAML format required by the Terraform provider
3. **Resource Generation**: Creates Terraform resource blocks with sanitized resource names
4. **File Output**: Writes all resources to `terraform.tf` with provider configuration included

## Features

- Automatically handles duplicate monitor names by appending counters
- Sanitizes monitor names to valid Terraform resource identifiers
- Converts monitor configurations to the correct YAML format
- Includes complete Terraform provider setup in the output
- Provides helpful error messages if API connection fails

## Troubleshooting

If the script fails to fetch monitors:

1. Verify your API credentials are correct
2. Check network connectivity to your Groundcover instance
3. Ensure the Backend ID is correct
4. Verify the API endpoint is accessible
5. Check that you have proper permissions to read monitors

## License

See LICENSE file for details.