import json
import csv
import os

# User's revenue list (their source of truth)
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

# ADs we're interested in
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

# Normalize names for matching
def normalize_name(name):
    return name.lower().replace('-', ' ').replace('_', ' ').strip()

# Load accounts with actual ADs
with open('data/accounts_with_actual_ads.json') as f:
    accounts_data = json.load(f)

# Build mapping of AD to accounts (only manufacturing and only from user's list)
ad_accounts = {}

for account in accounts_data:
    if account['Vertical'] != 'MANUFACTURING':
        continue
    
    ad = account.get('Actual_AD', '')
    account_name = account['Account']
    
    # Check if this account is in user's list
    if account_name not in user_revenue:
        continue
    
    # Check if this AD is one we're looking for
    for target_ad in target_ads:
        if normalize_name(ad) == normalize_name(target_ad):
            if target_ad not in ad_accounts:
                ad_accounts[target_ad] = []
            ad_accounts[target_ad].append(account_name)
            break

# Calculate and display results
print("=" * 100)
print("MANUFACTURING REVENUE BY ACCOUNT DIRECTOR")
print("(Based on user's provided revenue list)")
print("=" * 100)
print()

grand_total = 0

for ad in target_ads:
    accounts = ad_accounts.get(ad, [])
    
    print(f"\n{ad.upper()}")
    print("-" * 100)
    
    if not accounts:
        print("  No Manufacturing accounts found")
        print(f"  TOTAL: $0")
        continue
    
    ad_total = 0
    for account in sorted(accounts):
        revenue = user_revenue.get(account, 0)
        ad_total += revenue
        
        if revenue > 0:
            print(f"  {account:50} ${revenue:>12,} (${revenue/1_000_000:>6.2f}M)")
        else:
            print(f"  {account:50} {'No revenue':>12}")
    
    print(f"\n  TOTAL: ${ad_total:,} = ${ad_total/1_000_000:.2f}M")
    grand_total += ad_total

print()
print("=" * 100)
print(f"GRAND TOTAL FOR ALL ADS: ${grand_total:,} = ${grand_total/1_000_000:.2f}M")
print("=" * 100)
