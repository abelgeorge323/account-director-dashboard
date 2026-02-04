import csv

# Parse the MANUFACTURING.csv file
print("Reading MANUFACTURING.csv...")
mfg_data = {}

with open('data/MANUFACTURING.csv', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    
    current_account = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('KPIs'):
            continue
        
        parts = [p.strip() for p in line.split(',')]
        
        # Check if this is an account header line (has " - " in it or ends with specific patterns)
        if len(parts) > 0 and parts[0] and 'Revenue ($)' not in parts[0] and 'Growth' not in parts[0]:
            # This might be an account name
            if ' - ' in parts[0] or (len(parts) < 3 or not parts[1]):
                current_account = parts[0].replace(' - TBH', '').replace(' - ', ' ').strip()
                continue
        
        # Check if this is a Revenue row
        if len(parts) > 0 and parts[0] == 'Revenue ($)' and current_account:
            # Dec-25 is column 14 (index 13, but with split we need to check)
            if len(parts) >= 14:
                dec_value = parts[13].strip()
                if dec_value and dec_value != '-':
                    try:
                        # Remove any parentheses and convert
                        dec_value = dec_value.replace('(', '').replace(')', '').replace(',', '')
                        revenue = float(dec_value)
                        mfg_data[current_account] = revenue
                    except:
                        pass

print(f"Found {len(mfg_data)} accounts with revenue in MANUFACTURING.csv\n")

# User's list
user_list = {
    "3M Corp": 4457,
    "Anheuser Busch": 59997,
    "Ball Corporation": 245912,
    "Boeing Company": 1001952,
    "Chemours Company": 28606,
    "Clorox Company": 127070,
    "Coca-Cola": 195106,
    "Covestro": 46692,
    "Danfoss Power Solutions": 155881,
    "DuPont": 42051,
    "Fanatics": 20387,
    "Gallo Wine": 159470,
    "GE Healthcare": 358847,
    "General Dynamics": 283466,
    "General Electric": 708291,
    "GE Power": 109325,
    "Hasbro": 47850,
    "Hyliion": 13741,
    "JSR Micro": 5475,
    "Lockheed Martin": 967738,
    "Mars": 738762,
    "Molson Coors": 156052,
    "Nestle": 645657,
    "Newell Brands": 31761,
    "Northrop Grumman": 211679,
    "Parsons Corporation": 4197,
    "Procter & Gamble Company": 733293,
    "S.C. Johnson": 86888,
    "Spirit Aerosystems": 405520,
    "Textron Aviation": 1504446,
    "UCAR": 75757,
    "United Technologies": 317579,
    "W.L. Gore": 39224,
    "Westinghouse": 326747,
    "Wieland Group": 54526,
    "Workspace Properties": 38940
}

print("Comparing the two sources:\n")
print("=" * 80)

matches = 0
differences = 0
only_in_user = 0
only_in_csv = 0

# Check user list against CSV
for account, user_revenue in sorted(user_list.items()):
    csv_revenue = None
    # Try to find in CSV (exact match or close match)
    for csv_account, csv_rev in mfg_data.items():
        if account.lower() in csv_account.lower() or csv_account.lower() in account.lower():
            csv_revenue = csv_rev
            break
    
    if csv_revenue is not None:
        # Convert user's dollar value to thousands for comparison
        user_in_thousands = user_revenue / 1000
        if abs(csv_revenue - user_in_thousands) < 1:  # Within $1K
            matches += 1
            print(f"[MATCH] {account:40} User: ${user_revenue:>10,} | CSV: ${csv_revenue:>8,.0f}K")
        else:
            differences += 1
            print(f"[DIFF]  {account:40} User: ${user_revenue:>10,} | CSV: ${csv_revenue:>8,.0f}K")
    else:
        only_in_user += 1
        print(f"[USER]  {account:40} User: ${user_revenue:>10,} | CSV: Not found")

print("\n" + "=" * 80)
print(f"\nSummary:")
print(f"  Matches: {matches}")
print(f"  Differences: {differences}")
print(f"  Only in user list: {only_in_user}")
print(f"  Only in CSV: {len(mfg_data) - matches - differences}")
