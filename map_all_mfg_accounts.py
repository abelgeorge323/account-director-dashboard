import json

# User's revenue list (all 75 accounts)
user_revenue = {
    "3M Corp": 4457,
    "ABB Supply": 0,
    "Aerospace District Lodge": 0,
    "Alfa Laval": 0,
    "American Medical Systems": 0,
    "Anheuser Busch": 59997,
    "Applied Materials": 0,
    "ASML Holding": 0,
    "Ball Corporation": 245912,
    "Boeing Company": 1001952,
    "Bombardier Learjet": 0,
    "Brown Forman": 0,
    "Caterpillar": 0,
    "Chemours Company": 28606,
    "Cinram": 0,
    "Clorox Company": 127070,
    "Coca-Cola": 195106,
    "Covestro": 46692,
    "Danfoss Power Solutions": 155881,
    "Duke Energy": 0,
    "DuPont": 42051,
    "Duracell": 0,
    "Encore Aerojet Rocketdyne": 0,
    "Exxon Mobile": 0,
    "Fanatics": 20387,
    "Flextronics": 0,
    "Gallo Wine": 159470,
    "GE Healthcare": 358847,
    "General Dynamics": 283466,
    "General Electric": 708291,
    "GE Power": 109325,
    "Hasbro": 47850,
    "Henkel": 0,
    "Honeywell International": 0,
    "Hughes Christensen": 0,
    "Hyliion": 13741,
    "JDS Uniphase Corporation": 0,
    "Jireh Semiconductor": 0,
    "John Deere": 0,
    "Johnson Controls": 0,
    "JSR Micro": 5475,
    "Lockheed Martin": 967738,
    "Mars": 738762,
    "Micro Motion": 0,
    "Molson Coors": 156052,
    "Mondi Jackson": 0,
    "Nestle": 645657,
    "Newell Brands": 31761,
    "Nilfisk": 0,
    "Northrop Grumman": 211679,
    "Omnivision": 0,
    "Otis Elevator Company": 0,
    "Parsons Corporation": 4197,
    "Philips": 0,
    "Piper Aircraft": 0,
    "Procter & Gamble Company": 733293,
    "Rolls Royce": 0,
    "S.C. Johnson": 86888,
    "Schneider Electric": 0,
    "Shell": 0,
    "Sikorsky": 0,
    "Solidigm": 0,
    "Spirit Aerosystems": 405520,
    "Stanley Black & Decker": 0,
    "Taiwan Semiconductor": 0,
    "Texas Instruments": 0,
    "Textron Aviation": 1504446,
    "Trane": 0,
    "UCAR": 75757,
    "United Technologies": 317579,
    "W.L. Gore": 39224,
    "Wabash National Corporation": 0,
    "Westinghouse": 326747,
    "Wieland Group": 54526,
    "Workspace Properties": 38940
}

# The 9 ADs we're tracking
target_ads = [
    "Nicholas Trenkamp",
    "Logan Newman",
    "Jennifer Segovia",
    "Kimberly Wittekind",
    "Kyle Wallace",
    "Justin Dallavis",
    "Benjamin Ehrenberg",
    "Aaron Simpson",
    "Ayesha Nasir"
]

# Load accounts with actual ADs
with open('data/accounts_with_actual_ads.json') as f:
    accounts_data = json.load(f)

# Normalize names for matching
def normalize_name(name):
    return name.lower().replace('-', ' ').replace('_', ' ').strip()

# Build mapping
ad_mapping = {}
unaccounted = []
not_in_system = []

for account_name, revenue in user_revenue.items():
    # Find this account in our system
    found = False
    account_ad = None
    
    for account in accounts_data:
        if account['Vertical'] != 'MANUFACTURING':
            continue
        if account['Account'] == account_name:
            account_ad = account.get('Actual_AD', 'Unknown')
            found = True
            break
    
    if not found:
        not_in_system.append((account_name, revenue))
        continue
    
    # Check if this AD is in our target list
    matched_ad = None
    for target_ad in target_ads:
        if normalize_name(account_ad) == normalize_name(target_ad):
            matched_ad = target_ad
            break
    
    if matched_ad:
        if matched_ad not in ad_mapping:
            ad_mapping[matched_ad] = []
        ad_mapping[matched_ad].append((account_name, revenue))
    else:
        unaccounted.append((account_name, revenue, account_ad))

# Calculate totals
print("=" * 100)
print("MANUFACTURING ACCOUNTS - OWNERSHIP MAPPING")
print("=" * 100)
print()

accounted_total = 0
for ad in target_ads:
    accounts = ad_mapping.get(ad, [])
    ad_total = sum(rev for _, rev in accounts)
    accounted_total += ad_total
    
    print(f"\n{ad.upper()}: ${ad_total:,} (${ad_total/1_000_000:.2f}M)")
    for account_name, revenue in sorted(accounts):
        if revenue > 0:
            print(f"  - {account_name:50} ${revenue:>12,}")
        else:
            print(f"  - {account_name:50} {'No revenue':>12}")

print()
print("=" * 100)
print("UNACCOUNTED ACCOUNTS (Other ADs or TBH)")
print("=" * 100)

unaccounted_total = sum(rev for _, rev, _ in unaccounted)
unaccounted_with_revenue = [(n, r, ad) for n, r, ad in unaccounted if r > 0]

print(f"\nTotal Unaccounted: ${unaccounted_total:,} (${unaccounted_total/1_000_000:.2f}M)")
print(f"Accounts: {len(unaccounted)}\n")

for account_name, revenue, ad in sorted(unaccounted_with_revenue, key=lambda x: x[1], reverse=True):
    print(f"  - {account_name:50} ${revenue:>12,}  (AD: {ad})")

# Accounts not in system
if not_in_system:
    print()
    print("=" * 100)
    print("NOT FOUND IN SYSTEM")
    print("=" * 100)
    not_in_system_total = sum(rev for _, rev in not_in_system)
    print(f"\nTotal: ${not_in_system_total:,} (${not_in_system_total/1_000_000:.2f}M)")
    for account_name, revenue in sorted(not_in_system, key=lambda x: x[1], reverse=True):
        if revenue > 0:
            print(f"  - {account_name:50} ${revenue:>12,}")

# Final summary
print()
print("=" * 100)
print("SUMMARY")
print("=" * 100)
total_revenue = sum(user_revenue.values())
print(f"\nTotal Manufacturing Revenue:        ${total_revenue:>12,} (${total_revenue/1_000_000:>6.2f}M)")
print(f"Accounted by 9 ADs:                 ${accounted_total:>12,} (${accounted_total/1_000_000:>6.2f}M) - {accounted_total/total_revenue*100:.1f}%")
print(f"Unaccounted (Other ADs/TBH):        ${unaccounted_total:>12,} (${unaccounted_total/1_000_000:>6.2f}M) - {unaccounted_total/total_revenue*100:.1f}%")

if not_in_system:
    not_in_system_total = sum(rev for _, rev in not_in_system)
    print(f"Not in System:                      ${not_in_system_total:>12,} (${not_in_system_total/1_000_000:>6.2f}M) - {not_in_system_total/total_revenue*100:.1f}%")

print("=" * 100)
