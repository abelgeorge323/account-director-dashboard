import json

print("=" * 100)
print("FINANCE REVENUE BY ACCOUNT DIRECTOR")
print("=" * 100)
print()

# Load accounts with actual ADs
with open('data/accounts_with_actual_ads.json') as f:
    accounts_data = json.load(f)

# Filter for Finance vertical
finance_accounts = {}

for account in accounts_data:
    if account['Vertical'] == 'FINANCE':
        account_name = account['Account']
        ad = account.get('Actual_AD', 'Unknown')
        
        # Get revenue
        kpis = account.get('KPIs', {})
        revenue_data = kpis.get('Revenue ($)', {})
        dec_revenue = revenue_data.get('Dec-25')
        
        revenue = 0
        if dec_revenue and dec_revenue != '' and dec_revenue != '-':
            try:
                revenue = float(dec_revenue)
            except:
                pass
        
        if ad not in finance_accounts:
            finance_accounts[ad] = []
        finance_accounts[ad].append((account_name, revenue))

# Calculate totals per AD
ad_totals = {}
for ad, accounts in finance_accounts.items():
    ad_totals[ad] = sum(rev for _, rev in accounts)

# Sort ADs by total revenue
sorted_ads = sorted(ad_totals.items(), key=lambda x: x[1], reverse=True)

grand_total = 0

for ad, total in sorted_ads:
    accounts = finance_accounts[ad]
    
    print(f"\n{ad.upper()}: ${total:,.0f}K (${total/1000:.2f}M)")
    print("-" * 100)
    
    for account_name, revenue in sorted(accounts, key=lambda x: x[1], reverse=True):
        if revenue > 0:
            print(f"  - {account_name:60} ${revenue:>10,.0f}K (${revenue/1000:>6.2f}M)")
        else:
            print(f"  - {account_name:60} {'No revenue':>10}")
    
    grand_total += total

print()
print("=" * 100)
print(f"TOTAL FINANCE REVENUE: ${grand_total:,.0f}K = ${grand_total/1000:.2f}M")
print("=" * 100)

# Summary by AD
print()
print("=" * 100)
print("SUMMARY BY AD")
print("=" * 100)
for i, (ad, total) in enumerate(sorted_ads, 1):
    num_accounts = len(finance_accounts[ad])
    accounts_with_rev = sum(1 for _, rev in finance_accounts[ad] if rev > 0)
    pct = (total / grand_total * 100) if grand_total > 0 else 0
    print(f"{i:2}. {ad:40} ${total:>10,.0f}K (${total/1000:>5.2f}M) - {pct:>5.1f}% | {accounts_with_rev}/{num_accounts} accounts")
print("=" * 100)
