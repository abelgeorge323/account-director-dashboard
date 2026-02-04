import csv

print("=" * 80)
print("CALCULATING FINANCE VERTICAL TOTAL REVENUE (PROPER PARSING)")
print("=" * 80)
print()

# Parse using all_accounts_kpis.json which should have parsed this correctly
import json

with open('data/all_accounts_kpis.json') as f:
    all_accounts = json.load(f)

# Filter for Finance vertical
finance_accounts = {}

for account in all_accounts:
    if account.get('Vertical') == 'FINANCE':
        account_name = account['Account']
        kpis = account.get('KPIs', {})
        revenue_data = kpis.get('Revenue ($)', {})
        dec_revenue = revenue_data.get('Dec-25')
        
        if dec_revenue and dec_revenue != '' and dec_revenue != '-':
            try:
                revenue = float(dec_revenue)
                finance_accounts[account_name] = revenue
            except:
                pass

print(f"Found {len(finance_accounts)} accounts with revenue in FINANCE vertical\n")

# Calculate total
total_revenue = sum(finance_accounts.values())
accounts_with_revenue = len(finance_accounts)

print(f"Total Accounts with Revenue: {accounts_with_revenue}")
print(f"\nTOTAL FINANCE REVENUE: ${total_revenue:,.0f}K")
print(f"TOTAL FINANCE REVENUE: ${total_revenue/1000:.2f}M")

# Show all accounts sorted by revenue
print("\n" + "=" * 80)
print("ALL FINANCE ACCOUNTS BY REVENUE")
print("=" * 80)
sorted_accounts = sorted(finance_accounts.items(), key=lambda x: x[1], reverse=True)
for i, (account, revenue) in enumerate(sorted_accounts, 1):
    print(f"{i:2}. {account:60} ${revenue:>10,.0f}K (${revenue/1000:>6.2f}M)")

print("\n" + "=" * 80)
print(f"TOTAL: ${total_revenue:,.0f}K = ${total_revenue/1000:.2f}M")
print("=" * 80)
