#!/bin/bash

echo "🏗️  Creating GCP Data Engineering Bootcamp Project Structure..."

# Create main directories
mkdir -p week1-covid-pipeline/{data,sql,scripts,docs}
mkdir -p week2-kubernetes-composer/{k8s,dags,scripts,docs}
mkdir -p week3-dbt-analytics/{models,macros,tests,docs}
mkdir -p week4-streaming-pipeline/{streaming,pubsub,dataflow,docs}
mkdir -p week5-mlops-platform/{models,pipelines,notebooks,docs}

# Create .vscode directory
mkdir -p .vscode

# Create VS Code settings
cat > .vscode/settings.json << 'VSCODE_EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "cloudcode.gcp.project": "data-engineering-bootcamp",
    "files.exclude": {
        "**/__pycache__": true,
        "**/venv": true,
        "**/.pytest_cache": true
    },
    "python.terminal.activateEnvironment": true,
    "cloudcode.kubernetes": {
        "useKubectl": true
    }
}
VSCODE_EOF

# Create VS Code launch configuration
cat > .vscode/launch.json << 'LAUNCH_EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "GOOGLE_CLOUD_PROJECT": "data-engineering-bootcamp"
            }
        }
    ]
}
LAUNCH_EOF

# Create master requirements.txt
cat > requirements.txt << 'REQ_EOF'
# Core GCP libraries
google-cloud-bigquery==3.11.4
google-cloud-storage==2.10.0
google-cloud-pubsub==2.18.1

# Data processing
pandas==2.0.3
numpy==1.24.3

# Utilities
requests==2.31.0
python-dotenv==1.0.0

# Development
pytest==7.4.0
black==23.7.0
REQ_EOF

# Create week-specific requirements
cat > week1-covid-pipeline/requirements.txt << 'W1_EOF'
google-cloud-bigquery==3.11.4
google-cloud-storage==2.10.0
pandas==2.0.3
requests==2.31.0
python-dotenv==1.0.0
W1_EOF

# Create .gitignore
cat > .gitignore << 'GIT_EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.env
data/raw/*
!data/raw/.gitkeep
temp/

# GCP
*.json
!**/schema.json
service-account-key.json
GIT_EOF

# Create placeholder files to preserve directory structure
touch week1-covid-pipeline/data/.gitkeep
touch week2-kubernetes-composer/k8s/.gitkeep
touch week3-dbt-analytics/models/.gitkeep
touch week4-streaming-pipeline/streaming/.gitkeep
touch week5-mlops-platform/models/.gitkeep

# Create main README
cat > README.md << 'README_EOF'
# GCP Data Engineering Portfolio

A 5-week intensive bootcamp covering modern data engineering practices on Google Cloud Platform.

## Project Structure

- **Week 1**: COVID Data Pipeline (BigQuery + Cloud Storage + Data Studio)
- **Week 2**: Kubernetes + Cloud Composer + E-commerce Analytics
- **Week 3**: dbt + Advanced BigQuery + Customer Segmentation
- **Week 4**: Real-time Streaming (Pub/Sub + Dataflow + IoT)
- **Week 5**: MLOps + Vertex AI + Integrated ML Platform

## Setup

1. Create virtual environment: `python3 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure GCP: `gcloud auth login`

## Progress Tracking

- [ ] Week 1: COVID Data Pipeline
- [ ] Week 2: Kubernetes & Composer
- [ ] Week 3: dbt Analytics
- [ ] Week 4: Streaming Pipeline
- [ ] Week 5: MLOps Platform
README_EOF

# Create individual week READMEs
for week in week{1..5}-*; do
    if [ -d "$week" ]; then
        week_num=$(echo $week | grep -o 'week[0-9]')
        cat > "$week/README.md" << WEEK_README_EOF
# $week

## Overview
[Add project description here]

## Setup
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage
[Add usage instructions here]

## Architecture
[Add architecture diagram/description here]
WEEK_README_EOF
    fi
done

echo "✅ Project structure created successfully!"
echo ""
echo "📁 Structure created:"
tree -I 'venv|__pycache__|*.pyc' . 2>/dev/null || find . -type d -not -path './venv*' -not -path './.git*' | sort

echo ""
echo "🔄 Next steps:"
echo "1. Run: python3 -m venv venv"
echo "2. Run: source venv/bin/activate"
echo "3. Run: pip install -r requirements.txt"
echo "4. Open in VS Code: code ."
