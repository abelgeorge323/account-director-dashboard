import pandas as pd
import json
import os
from pathlib import Path

# Load accounts with actual ADs
with open('data/accounts_with_actual_ads.json', 'r') as f:
    all_accounts = json.load(f)

# Group by Actual_AD
ad_accounts = {}
for account in all_accounts:
    ad = account['Actual_AD']
    if ad not in ad_accounts:
        ad_accounts[ad] = []
    ad_accounts[ad].append(account)

# Create output directory
output_dir = Path('data/ad_csvs')
output_dir.mkdir(exist_ok=True)

print(f"Creating CSV files for {len(ad_accounts)} Account Directors...")

for ad, accounts in ad_accounts.items():
    # Skip TBH accounts
    if ad == 'TBH':
        continue
    
    # Create a CSV for this AD
    rows = []
    
    for account in accounts:
        account_name = account['Account']
        vertical = account['Vertical']
        kpis = account['KPIs']
        
        # For each KPI, create a row
        for kpi_name, monthly_values in kpis.items():
            row = {
                'Account': account_name,
                'Vertical': vertical,
                'KPI': kpi_name
            }
            # Add monthly values
            row.update(monthly_values)
            rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Save to CSV
    filename = ad.lower().replace(' ', '-') + '.csv'
    filepath = output_dir / filename
    df.to_csv(filepath, index=False)
    
    print(f"Created {filename} with {len(accounts)} accounts, {len(rows)} KPI rows")

print(f"\nAll AD CSV files saved to {output_dir}/")

