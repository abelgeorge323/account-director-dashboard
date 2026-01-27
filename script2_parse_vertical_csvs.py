import pandas as pd
import numpy as np
import os
from pathlib import Path
import json
import csv

def parse_kpi_csv(filepath):
    """
    Parse a KPI CSV file and extract account-level data.
    Returns a list of dictionaries with account info and KPIs.
    """
    # Read the CSV
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the header row (starts with ,Dec-24,Jan-25...)
    header_row = None
    for i, line in enumerate(lines):
        if 'Dec-24' in line and 'Jan-25' in line:
            header_row = i
            break
    
    if header_row is None:
        print(f"Could not find header row in {filepath}")
        return []
    
    # Parse the months from header using proper CSV parsing
    reader = csv.reader([lines[header_row]])
    header_parts = next(reader)
    months = [col.strip() for col in header_parts[1:] if col.strip()]
    
    # Now parse each account section
    accounts_data = []
    current_account = None
    current_ad = None
    current_kpis = {}
    
    for i in range(header_row + 1, len(lines)):
        line = lines[i]
        # Use proper CSV parsing to handle quoted commas
        reader = csv.reader([line])
        parts = [p.strip() for p in next(reader)]
        
        # Check if this is an account header (has " - " in it)
        if ' - ' in parts[0] and parts[0]:
            # Save previous account if exists
            if current_account:
                accounts_data.append({
                    'Account': current_account,
                    'Account_Director': current_ad,
                    'Vertical': Path(filepath).stem,
                    'KPIs': current_kpis
                })
            
            # Parse new account
            account_info = parts[0].split(' - ')
            current_account = account_info[0].strip()
            current_ad = account_info[1].strip() if len(account_info) > 1 else 'Unknown'
            current_kpis = {}
            
        # Otherwise it's a KPI row
        elif parts[0] and current_account:
            kpi_name = parts[0].strip()
            # Get values for each month (skip empty first column)
            values = []
            for val in parts[1:len(months)+1]:
                # Clean the value
                cleaned = val.replace(',', '').replace('$', '').replace('%', '').replace(' ', '').strip()
                if cleaned == '-' or cleaned == '':
                    cleaned = None
                elif cleaned.startswith('(') and cleaned.endswith(')'):
                    # Negative number
                    cleaned = '-' + cleaned[1:-1]
                values.append(cleaned)
            
            current_kpis[kpi_name] = dict(zip(months, values))
    
    # Don't forget the last account
    if current_account:
        accounts_data.append({
            'Account': current_account,
            'Account_Director': current_ad,
            'Vertical': Path(filepath).stem,
            'KPIs': current_kpis
        })
    
    return accounts_data

# Parse all vertical CSVs
vertical_files = [
    'data/DISTRIBUTION.csv',
    'data/FINANCE.csv',
    'data/TECHNOLOGY.csv',
    'data/MANUFACTURING.csv',
    'data/LIFE SCIENCE.csv'
]

all_accounts = []
for filepath in vertical_files:
    print(f"Parsing {filepath}...")
    accounts = parse_kpi_csv(filepath)
    all_accounts.extend(accounts)
    print(f"  Found {len(accounts)} accounts")

print(f"\nTotal accounts parsed: {len(all_accounts)}")

# Save parsed data to JSON for easier processing
with open('data/all_accounts_kpis.json', 'w') as f:
    json.dump(all_accounts, f, indent=2)

print("Saved to data/all_accounts_kpis.json")

