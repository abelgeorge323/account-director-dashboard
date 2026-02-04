import json

with open('data/accounts_with_actual_ads.json') as f:
    data = json.load(f)

# Find TBH accounts in MANUFACTURING
tbh_mfg = [a for a in data if a.get('Actual_AD', '').upper() == 'TBH' and a['Vertical'] == 'MANUFACTURING']

print(f'TBH Manufacturing Accounts: {len(tbh_mfg)}\n')

total = 0
for acc in tbh_mfg:
    account_name = acc['Account']
    rev = acc.get('KPIs', {}).get('Revenue ($)', {}).get('Dec-25')
    
    if rev and rev != '':
        rev_val = float(rev)
        print(f'  {account_name}: ${rev_val:,.0f}K')
        total += rev_val
    else:
        print(f'  {account_name}: No revenue data')

print(f'\nTotal TBH Manufacturing Revenue: ${total:,.0f}K = ${total/1000:.2f}M')
