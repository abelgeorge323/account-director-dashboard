import pandas as pd
import json
from pathlib import Path

# Load accounts with actual ADs
with open('data/accounts_with_actual_ads.json', 'r') as f:
    all_accounts = json.load(f)

# Create summary statistics
summary_data = []

# Group by AD
ad_accounts = {}
for account in all_accounts:
    ad = account['Actual_AD']
    if ad not in ad_accounts:
        ad_accounts[ad] = []
    ad_accounts[ad].append(account)

for ad, accounts in sorted(ad_accounts.items()):
    if ad == 'TBH':
        continue
    
    # Calculate aggregated metrics
    total_revenue_dec25 = 0
    total_headcount_dec25 = 0
    csat_values = []
    turnover_values = []
    
    account_list = []
    verticals = set()
    
    for account in accounts:
        account_list.append(account['Account'])
        verticals.add(account['Vertical'])
        kpis = account['KPIs']
        
        # Get Dec-25 values
        if 'Revenue ($)' in kpis and 'Dec-25' in kpis['Revenue ($)']:
            rev = kpis['Revenue ($)']['Dec-25']
            if rev:
                try:
                    total_revenue_dec25 += float(rev.replace(',', ''))
                except:
                    pass
        
        if 'Headcount' in kpis and 'Dec-25' in kpis['Headcount']:
            hc = kpis['Headcount']['Dec-25']
            if hc:
                try:
                    total_headcount_dec25 += int(float(hc.replace(',', '')))
                except:
                    pass
        
        if 'CSAT' in kpis and 'Dec-25' in kpis['CSAT']:
            csat = kpis['CSAT']['Dec-25']
            if csat:
                try:
                    csat_values.append(float(csat))
                except:
                    pass
        
        if 'Turnover (%)' in kpis and 'Dec-25' in kpis['Turnover (%)']:
            turnover = kpis['Turnover (%)']['Dec-25']
            if turnover:
                try:
                    turnover_values.append(float(turnover))
                except:
                    pass
    
    avg_csat = sum(csat_values) / len(csat_values) if csat_values else None
    avg_turnover = sum(turnover_values) / len(turnover_values) if turnover_values else None
    
    summary_data.append({
        'Account_Director': ad,
        'Num_Accounts': len(accounts),
        'Accounts': ', '.join(sorted(account_list)),
        'Verticals': ', '.join(sorted(verticals)),
        'Total_Revenue_Dec25_K': f"${total_revenue_dec25:,.0f}" if total_revenue_dec25 > 0 else 'N/A',
        'Total_Headcount_Dec25': total_headcount_dec25 if total_headcount_dec25 > 0 else 'N/A',
        'Avg_CSAT_Dec25': f"{avg_csat:.2f}" if avg_csat else 'N/A',
        'Avg_Turnover_Dec25': f"{avg_turnover:.1f}%" if avg_turnover else 'N/A'
    })

# Create DataFrame and save
df = pd.DataFrame(summary_data)
df = df.sort_values('Account_Director')
df.to_csv('data/ad_summary_report.csv', index=False)

print("AD Summary Report")
print("=" * 100)
print(df.to_string(index=False))
print(f"\nSaved to data/ad_summary_report.csv")

