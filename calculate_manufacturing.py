import pandas as pd
import os
from pathlib import Path

ad_dir = Path('data/ad_csvs')
mfg_revenue = 0
mfg_headcount = 0
mfg_accounts = []
ad_details = []

print('=== MANUFACTURING VERTICAL ANALYSIS ===\n')

for csv_file in sorted(ad_dir.glob('*.csv')):
    df = pd.read_csv(csv_file)
    mfg_rows = df[df['Vertical'] == 'MANUFACTURING']
    
    if not mfg_rows.empty:
        ad_name = csv_file.stem.replace('-', ' ').title()
        accounts = mfg_rows['Account'].unique()
        ad_revenue = 0
        ad_headcount = 0
        
        for acc in accounts:
            acc_data = mfg_rows[mfg_rows['Account'] == acc]
            
            # Revenue
            rev = acc_data[acc_data['KPI'] == 'Revenue ($)']['Dec-25'].values
            if len(rev) > 0 and pd.notna(rev[0]):
                ad_revenue += float(rev[0])
            
            # Headcount
            hc = acc_data[acc_data['KPI'] == 'Headcount']['Dec-25'].values
            if len(hc) > 0 and pd.notna(hc[0]):
                ad_headcount += int(float(hc[0]))
        
        mfg_accounts.extend(accounts.tolist())
        
        print(f'{ad_name}:')
        print(f'  Accounts: {", ".join(accounts)}')
        print(f'  Revenue: ${ad_revenue:,.0f}K = ${ad_revenue/1000:.2f}M')
        print(f'  Headcount: {ad_headcount:,} employees')
        print()
        
        ad_details.append({
            'AD': ad_name,
            'Accounts': len(accounts),
            'Revenue_K': ad_revenue,
            'Headcount': ad_headcount
        })
        
        mfg_revenue += ad_revenue
        mfg_headcount += ad_headcount

print('\n' + '='*60)
print('TOTAL MANUFACTURING VERTICAL:')
print('='*60)
print(f'Total Revenue: ${mfg_revenue:,.0f}K = ${mfg_revenue/1000:.2f}M')
print(f'Total Headcount: {mfg_headcount:,} employees')
print(f'Unique Accounts: {len(set(mfg_accounts))}')
print(f'Account Directors: {len(ad_details)}')
