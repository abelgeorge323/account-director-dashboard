import pandas as pd
import json

# Load the AD mapping from performance reviews
ad_mapping = pd.read_csv('data/ad_account_mapping.csv')

# Load all accounts KPIs
with open('data/all_accounts_kpis.json', 'r') as f:
    all_accounts = json.load(f)

# Create a mapping dictionary for easy lookup
# Account name -> AD from performance reviews
account_to_ad = {}
for _, row in ad_mapping.iterrows():
    account_to_ad[row['Account'].lower().strip()] = row['Account_Director']

# Now match accounts from CSVs to ADs from reviews
matched_accounts = []
unmatched_accounts = []

for account in all_accounts:
    account_name = account['Account'].lower().strip()
    csv_ad = account['Account_Director']
    
    # Try exact match first
    if account_name in account_to_ad:
        actual_ad = account_to_ad[account_name]
        account['Actual_AD'] = actual_ad
        account['CSV_AD'] = csv_ad
        matched_accounts.append(account)
    else:
        # Try fuzzy match
        matched = False
        for review_account, review_ad in account_to_ad.items():
            # Check if either contains the other
            if review_account in account_name or account_name in review_account:
                account['Actual_AD'] = review_ad
                account['CSV_AD'] = csv_ad
                matched_accounts.append(account)
                matched = True
                break
        
        if not matched:
            # This account wasn't in performance reviews
            # Keep the CSV AD (might be TBH or operational person)
            account['Actual_AD'] = csv_ad
            account['CSV_AD'] = csv_ad
            unmatched_accounts.append(account)

print(f"Matched accounts: {len(matched_accounts)}")
print(f"Unmatched accounts (keeping CSV AD): {len(unmatched_accounts)}")

# Combine all accounts
final_accounts = matched_accounts + unmatched_accounts

# Save to JSON
with open('data/accounts_with_actual_ads.json', 'w') as f:
    json.dump(final_accounts, f, indent=2)

print("\nSample mappings:")
for i, acc in enumerate(matched_accounts[:10]):
    print(f"{acc['Account']}: CSV_AD={acc['CSV_AD']} -> Actual_AD={acc['Actual_AD']}")

# Show which ADs manage multiple accounts
ad_account_count = {}
for acc in final_accounts:
    ad = acc['Actual_AD']
    if ad not in ad_account_count:
        ad_account_count[ad] = []
    ad_account_count[ad].append(acc['Account'])

print("\n\nADs with multiple accounts:")
for ad, accounts in sorted(ad_account_count.items()):
    if len(accounts) > 1 and ad != 'TBH':
        print(f"\n{ad} ({len(accounts)} accounts):")
        for acc in sorted(accounts):
            print(f"  - {acc}")

print(f"\n\nSaved to data/accounts_with_actual_ads.json")

