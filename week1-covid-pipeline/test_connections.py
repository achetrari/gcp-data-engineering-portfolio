#!/usr/bin/env python3
"""Test all connections"""

print("�� Testing Connections...")

# Test 1: Python environment
import sys
print(f"✅ Python: {sys.executable}")

# Test 2: GCP libraries
try:
    from google.cloud import bigquery, storage
    print("✅ GCP libraries imported")
except ImportError as e:
    print(f"❌ GCP libraries missing: {e}")

# Test 3: GCP authentication
try:
    client = bigquery.Client()
    print(f"✅ BigQuery connected to project: {client.project}")
except Exception as e:
    print(f"❌ BigQuery connection failed: {e}")

# Test 4: File system access
import os
print(f"✅ Current directory: {os.getcwd()}")
print(f"✅ Files in current directory: {os.listdir('.')}")

print("\n🎉 Connection test complete!")
