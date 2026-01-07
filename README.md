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

The script generates a `monitors_terraform` directory containing:

- `terraform.tf` - Terraform provider configuration and variable definitions
- `monitor_{resource_name}.tf` - Individual Terraform resource files for each monitor

Each monitor gets its own file, making it easier to manage and version control individual monitor configurations.

### 4. Use the Generated Terraform

After generating the Terraform files, navigate to the output directory and use Terraform to manage your monitors:

```bash
# Navigate to the generated directory
cd monitors_terraform

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

1. **API Connection**: The script makes a POST request to `/api/monitors/summary/query` to fetch monitors from Groundcover
2. **Data Transformation**: Converts monitor JSON data into YAML format required by the Terraform provider
3. **Resource Generation**: Creates Terraform resource blocks with sanitized resource names
4. **File Output**: 
   - Creates a `monitors_terraform` directory
   - Writes provider configuration to `terraform.tf`
   - Creates individual `monitor_{resource_name}.tf` files for each monitor

## Features

- Automatically handles duplicate monitor names by appending counters
- Sanitizes monitor names to valid Terraform resource identifiers
- Converts monitor configurations to the correct YAML format
- Creates individual files for each monitor resource for easier management
- Organizes all Terraform files in a dedicated `monitors_terraform` directory
- Includes complete Terraform provider setup in the output
- Provides helpful error messages if API connection fails

## Troubleshooting

If the script fails to fetch monitors:

1. Verify your API credentials are correct
2. Check network connectivity to your Groundcover instance
3. Ensure the Backend ID is correct
4. Verify the API endpoint (`/api/monitors/summary/query`) is accessible
5. Check that you have proper permissions to read monitors

## License

See LICENSE file for details.