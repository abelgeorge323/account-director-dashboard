import pandas as pd
import re

# Read performance reviews to get the AD mapping
df = pd.read_csv('data/performance_reviews.csv')

# Extract Account Name and Account Director Name
ad_mapping = df[['Account Name', 'Account Director Name']].copy()
ad_mapping = ad_mapping.dropna()
ad_mapping.columns = ['Account', 'Account_Director']

# Clean up account names
ad_mapping['Account'] = ad_mapping['Account'].str.strip()
ad_mapping['Account_Director'] = ad_mapping['Account_Director'].str.strip()

# Split accounts that have multiple (like "LinkedIn/Uber")
expanded_rows = []
for _, row in ad_mapping.iterrows():
    accounts = [a.strip() for a in row['Account'].split('/')]
    for account in accounts:
        expanded_rows.append({
            'Account': account,
            'Account_Director': row['Account_Director']
        })

ad_mapping_expanded = pd.DataFrame(expanded_rows)

# Remove duplicates
ad_mapping_expanded = ad_mapping_expanded.drop_duplicates()

print("AD to Account Mapping:")
print(ad_mapping_expanded.sort_values('Account_Director'))
print(f"\nTotal unique ADs: {ad_mapping_expanded['Account_Director'].nunique()}")
print(f"\nAD List:\n{sorted(ad_mapping_expanded['Account_Director'].unique())}")

# Save to CSV
ad_mapping_expanded.to_csv('data/ad_account_mapping.csv', index=False)
print("\nSaved to data/ad_account_mapping.csv")

