import pandas as pd

df = pd.read_csv('top_20_accounts_by_revenue.csv')

# Filter out accounts without CSAT data and get top 20
df_with_csat = df[df['CSAT'].notna()].head(20)

avg = df_with_csat['CSAT'].mean()
highest = df_with_csat['CSAT'].max()
lowest = df_with_csat['CSAT'].min()
highest_account = df_with_csat.loc[df_with_csat['CSAT'].idxmax(), 'Account']
lowest_account = df_with_csat.loc[df_with_csat['CSAT'].idxmin(), 'Account']

print("\n" + "="*60)
print("CSAT ANALYSIS - TOP 20 ACCOUNTS BY REVENUE")
print("(Excluding Tesla - No CSAT Data)")
print("="*60)
print(f"\nAverage CSAT:  {avg:.2f}")
print(f"Highest CSAT:  {highest:.2f}  ({highest_account})")
print(f"Lowest CSAT:   {lowest:.2f}  ({lowest_account})")
print(f"\nTotal Accounts: {len(df_with_csat)}")
print("="*60 + "\n")
