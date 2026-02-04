import csv

print("=" * 80)
print("CALCULATING FINANCE VERTICAL TOTAL REVENUE")
print("=" * 80)
print()

# Parse the FINANCE.csv file
finance_accounts = {}

with open('data/FINANCE.csv', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    
    current_account = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('KPIs'):
            continue
        
        parts = [p.strip() for p in line.split(',')]
        
        # Check if this is an account header line
        if len(parts) > 0 and parts[0] and 'Revenue ($)' not in parts[0] and 'Growth' not in parts[0]:
            # This might be an account name
            if ' - ' in parts[0] or (len(parts) < 3 or not parts[1]):
                current_account = parts[0].replace(' - TBH', '').replace(' - ', ' ').strip()
                continue
        
        # Check if this is a Revenue row
        if len(parts) > 0 and parts[0] == 'Revenue ($)' and current_account:
            # Dec-25 is column 14 (index 13)
            if len(parts) >= 14:
                dec_value = parts[13].strip()
                if dec_value and dec_value != '-':
                    try:
                        # Remove any parentheses and convert
                        dec_value = dec_value.replace('(', '').replace(')', '').replace(',', '')
                        revenue = float(dec_value)
                        finance_accounts[current_account] = revenue
                    except:
                        pass

print(f"Found {len(finance_accounts)} accounts with revenue in FINANCE.csv\n")

# Calculate total
total_revenue = sum(finance_accounts.values())
accounts_with_revenue = len(finance_accounts)

print(f"Total Accounts with Revenue: {accounts_with_revenue}")
print(f"\nTOTAL FINANCE REVENUE: ${total_revenue:,.0f}K")
print(f"TOTAL FINANCE REVENUE: ${total_revenue/1000:.2f}M")

# Show top 10
print("\n" + "=" * 80)
print("TOP 10 ACCOUNTS BY REVENUE")
print("=" * 80)
sorted_accounts = sorted(finance_accounts.items(), key=lambda x: x[1], reverse=True)
for i, (account, revenue) in enumerate(sorted_accounts[:10], 1):
    print(f"{i:2}. {account:50} ${revenue:>10,.0f}K (${revenue/1000:>6.2f}M)")

print("\n" + "=" * 80)
