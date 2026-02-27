"""
List top 50 accounts by revenue (Dec-25) and their Account Director owner.
Uses data from ad_csvs - revenue is in $K.
"""
import pandas as pd
from pathlib import Path

def main():
    ad_csvs_dir = Path("data/ad_csvs")
    account_data = []  # (account, revenue, owner)

    for csv_file in sorted(ad_csvs_dir.glob("*.csv")):
        ad_name = csv_file.stem.replace('-', ' ').title()
        if ad_name == "Gregory Demedio":
            ad_name = "Gregory DeMedio"
        if ad_name == "Michael Barry":
            ad_name = "Mike Barry"

        try:
            df = pd.read_csv(csv_file)
            accounts = df['Account'].unique().tolist()

            for account in accounts:
                account_df = df[df['Account'] == account]
                rev_row = account_df[account_df['KPI'] == 'Revenue ($)']
                revenue = 0
                if not rev_row.empty and 'Dec-25' in rev_row.columns:
                    val = rev_row['Dec-25'].values[0]
                    if pd.notna(val) and str(val).strip():
                        try:
                            revenue = float(str(val).replace(',', ''))
                        except (ValueError, TypeError):
                            pass
                account_data.append((account, revenue, ad_name))
        except Exception as e:
            print(f"  Skip {csv_file.name}: {e}")

    # Sort by revenue descending
    account_data.sort(key=lambda x: x[1], reverse=True)

    # Top 50
    print("Top 50 Accounts by Revenue (Dec-25, $K)\n")
    print(f"{'Rank':<5} {'Account':<45} {'Revenue ($K)':>12} {'Owner (AD)':<25}")
    print("-" * 90)
    for i, (account, rev, owner) in enumerate(account_data[:50], 1):
        rev_str = f"${rev:,.0f}" if rev > 0 else "N/A"
        print(f"{i:<5} {account[:44]:<45} {rev_str:>12} {owner:<25}")

if __name__ == "__main__":
    main()
