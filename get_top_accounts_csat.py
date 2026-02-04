"""
Get top 20 accounts by revenue with their CSAT scores
"""

import pandas as pd
from pathlib import Path

def get_top_accounts_by_revenue():
    """Extract top 20 accounts by revenue with CSAT scores"""
    
    ad_csvs_dir = Path('data/ad_csvs')
    
    accounts_data = {}
    
    # Read all AD CSV files
    for csv_file in ad_csvs_dir.glob('*.csv'):
        try:
            df = pd.read_csv(csv_file)
            
            # Process each row
            for _, row in df.iterrows():
                account = str(row.get('Account', '')).strip()
                kpi = str(row.get('KPI', '')).strip()
                
                # Skip empty or invalid accounts
                if not account or account == '' or pd.isna(account):
                    continue
                
                # Get Dec-25 data (most recent)
                dec_25_value = row.get('Dec-25', None)
                
                # Initialize account if not exists
                if account not in accounts_data:
                    accounts_data[account] = {
                        'Account': account,
                        'Revenue': 0,
                        'CSAT': None
                    }
                
                # Extract Revenue
                if kpi == 'Revenue ($)':
                    try:
                        revenue = float(dec_25_value) if not pd.isna(dec_25_value) else 0
                        accounts_data[account]['Revenue'] = revenue
                    except:
                        pass
                
                # Extract CSAT
                elif kpi == 'CSAT':
                    try:
                        csat = float(dec_25_value) if not pd.isna(dec_25_value) else None
                        accounts_data[account]['CSAT'] = csat
                    except:
                        pass
        
        except Exception as e:
            print(f"Error reading {csv_file.name}: {e}")
            continue
    
    # Convert dictionary to DataFrame
    df_accounts = pd.DataFrame(list(accounts_data.values()))
    
    # Filter out accounts with zero revenue
    df_accounts = df_accounts[df_accounts['Revenue'] > 0]
    
    # Sort by revenue
    df_accounts = df_accounts.sort_values('Revenue', ascending=False)
    
    # Get top 21 to see the next account
    top_21 = df_accounts.head(21)
    
    print("\n" + "="*70)
    print("TOP 21 ACCOUNTS BY REVENUE (December 2025)")
    print("="*70)
    print(f"\n{'Rank':<6} {'Account':<40} {'Revenue':<12} {'CSAT':<8}")
    print("-"*70)
    
    for idx, row in enumerate(top_21.itertuples(), 1):
        revenue_str = f"${row.Revenue:,.0f}K"
        csat_str = f"{row.CSAT:.2f}" if pd.notna(row.CSAT) else "N/A"
        note = " <-- No CSAT (rank 7)" if pd.isna(row.CSAT) and idx == 7 else ""
        note = " <-- 21st account (replacement)" if idx == 21 else note
        print(f"{idx:<6} {row.Account:<40} {revenue_str:<12} {csat_str:<8}{note}")
    
    print("="*70)
    
    # Show replacement suggestion
    print("\n** REPLACEMENT SUGGESTION **")
    print(f"Tesla Inc - Jacob Reed (Rank 7) has no CSAT data.")
    rank_21 = top_21.iloc[20]
    print(f"Replace with: {rank_21['Account']} - ${rank_21['Revenue']:,.0f}K, CSAT: {rank_21['CSAT']:.2f}")
    
    # Save to CSV
    output_file = 'top_20_accounts_by_revenue.csv'
    top_21.to_csv(output_file, index=False)
    print(f"\nSaved to: {output_file}")
    
    return top_21

if __name__ == '__main__':
    get_top_accounts_by_revenue()
