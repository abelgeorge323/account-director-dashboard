import pandas as pd
from pathlib import Path

ad_dir = Path('data/ad_csvs')
total_revenue = 0
breakdown = []

print('=== MANUFACTURING BREAKDOWN (Excluding Jeremy Johnson) ===\n')

for csv_file in sorted(ad_dir.glob('*.csv')):
    df = pd.read_csv(csv_file)
    mfg_rows = df[df['Vertical'] == 'MANUFACTURING']
    
    if not mfg_rows.empty:
        ad_name = csv_file.stem.replace('-', ' ').title()
        
        # Skip Jeremy Johnson
        if ad_name.lower() == 'jeremy johnson':
            continue
        
        accounts = mfg_rows['Account'].unique()
        
        print(f'{ad_name}:')
        ad_total = 0
        
        for acc in accounts:
            acc_data = mfg_rows[mfg_rows['Account'] == acc]
            rev = acc_data[acc_data['KPI'] == 'Revenue ($)']['Dec-25'].values
            
            if len(rev) > 0 and pd.notna(rev[0]):
                acc_revenue = float(rev[0])
                print(f'  - {acc}: ${acc_revenue:,.0f}K')
                ad_total += acc_revenue
                total_revenue += acc_revenue
        
        print(f'  TOTAL: ${ad_total:,.0f}K = ${ad_total/1000:.2f}M')
        print()
        
        breakdown.append({
            'AD': ad_name,
            'Total': ad_total
        })

print('\n' + '='*60)
print(f'MANUFACTURING TOTAL (Without Jeremy Johnson): ${total_revenue:,.0f}K = ${total_revenue/1000:.2f}M')
print('='*60)
