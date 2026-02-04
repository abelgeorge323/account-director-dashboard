"""
Comprehensive Account Director Account Audit
Scans all vertical CSV files to find accounts, revenue, and headcount for each AD
"""
import pandas as pd
import csv
from pathlib import Path
from collections import defaultdict

def normalize_ad_name(name):
    """Normalize AD names for consistent matching"""
    if not name or pd.isna(name):
        return ""
    
    name_map = {
        "Mike Barry": "Michael Barry",
        "Gisell Langelier": "Giselle Langelier",
        "Collen Doles": "Colleen Doles",
        "RJ Ober": "Russell Ober",
        "Sid Shah": "Siddarth Shah",
        "Peggy McElwee": "Peggy Shum",
        "Dave Pergola": "David Pergola",
        "Nick Trenkamp": "Nicholas Trenkamp",
    }
    
    name_str = str(name).strip()
    return name_map.get(name_str, name_str)

def clean_numeric_value(val):
    """Clean numeric values from CSV (handles commas, quotes, dashes)"""
    if pd.isna(val) or val == '' or val == ' - ':
        return None
    
    try:
        # Remove quotes, commas, spaces
        cleaned = str(val).replace('"', '').replace(',', '').replace(' ', '')
        if cleaned == '-' or cleaned == '':
            return None
        return float(cleaned)
    except:
        return None

def scan_csv_for_ad(csv_path, ad_name):
    """Scan a CSV file for accounts belonging to a specific AD"""
    accounts = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_account = None
        current_revenue_row = None
        current_headcount_row = None
        
        for i, line in enumerate(lines):
            # Check if this line contains an account assignment (has " - " separator)
            if ' - ' in line and ',' in line:
                # Extract account name (format: "Account Name - AD Name")
                parts = line.split(',')[0].strip()
                if ' - ' in parts:
                    account_parts = parts.split(' - ')
                    if len(account_parts) >= 2:
                        # Check if AD name matches (normalize both sides)
                        line_ad_name = account_parts[-1].strip()
                        if normalize_ad_name(line_ad_name) == normalize_ad_name(ad_name):
                            current_account = ' - '.join(account_parts[:-1]).strip()
                            current_revenue_row = None
                            current_headcount_row = None
            
            # If we found an account, look for Revenue and Headcount rows
            if current_account:
                if i < len(lines) - 1:
                    # Check next lines for Revenue and Headcount
                    if 'Revenue ($)' in line:
                        current_revenue_row = line
                    elif 'Headcount,' in line or 'Headcount ' in line:
                        current_headcount_row = line
                        
                        # Process when we have both revenue and headcount
                        if current_revenue_row and current_headcount_row:
                            # Parse the rows
                            revenue_values = current_revenue_row.split(',')
                            headcount_values = current_headcount_row.split(',')
                            
                            # Dec-25 is the last column (index -1 or -2 depending on trailing comma)
                            dec_25_revenue = None
                            dec_25_headcount = None
                            
                            if len(revenue_values) >= 14:
                                dec_25_revenue = clean_numeric_value(revenue_values[-2] if revenue_values[-1].strip() == '' else revenue_values[-1])
                            
                            if len(headcount_values) >= 14:
                                dec_25_headcount = clean_numeric_value(headcount_values[-2] if headcount_values[-1].strip() == '' else headcount_values[-1])
                            
                            accounts.append({
                                'account': current_account,
                                'csv_file': csv_path.name,
                                'revenue': dec_25_revenue if dec_25_revenue else 0,
                                'headcount': dec_25_headcount if dec_25_headcount else 0,
                                'zero_revenue': dec_25_revenue is None or dec_25_revenue == 0
                            })
                            
                            # Reset for next account
                            current_account = None
                            current_revenue_row = None
                            current_headcount_row = None
    
    except Exception as e:
        print(f"  Error scanning {csv_path.name}: {e}")
    
    return accounts

def audit_all_ads():
    """Main audit function"""
    print("=" * 80)
    print("COMPREHENSIVE ACCOUNT DIRECTOR ACCOUNT AUDIT")
    print("=" * 80)
    print()
    
    # Load ADs from verticals.csv
    verticals_df = pd.read_csv("data/verticals.csv")
    all_ads = verticals_df["Account Director"].tolist()
    
    print(f"Found {len(all_ads)} Account Directors in verticals.csv")
    print()
    
    # Define CSV files to scan
    csv_files = [
        Path("data/LIFE SCIENCE.csv"),
        Path("data/TECHNOLOGY.csv"),
        Path("data/MANUFACTURING.csv"),
        Path("data/DISTRIBUTION.csv"),
        Path("data/FINANCE.csv"),
        Path("data/AUTOMOTIVE.csv"),
        Path("data/(01.22.26) VL & AD Rankings w RD Metrics (December 2025) PR.csv"),
    ]
    
    # Check which files exist
    existing_files = [f for f in csv_files if f.exists()]
    print(f"Scanning {len(existing_files)} CSV files:")
    for f in existing_files:
        print(f"  - {f.name}")
    print()
    
    # Results storage
    ad_results = {}
    
    # Scan each AD
    for ad_name in all_ads:
        normalized_name = normalize_ad_name(ad_name)
        print(f"Scanning: {normalized_name}")
        
        all_accounts = []
        
        # Scan each CSV file
        for csv_file in existing_files:
            accounts = scan_csv_for_ad(csv_file, normalized_name)
            all_accounts.extend(accounts)
        
        # Calculate totals
        total_revenue = sum(acc['revenue'] for acc in all_accounts)
        total_headcount = sum(acc['headcount'] for acc in all_accounts)
        zero_revenue_accounts = [acc for acc in all_accounts if acc['zero_revenue']]
        
        ad_results[normalized_name] = {
            'accounts': all_accounts,
            'total_revenue': total_revenue,
            'total_headcount': total_headcount,
            'num_accounts': len(all_accounts),
            'zero_revenue_accounts': zero_revenue_accounts
        }
        
        # Print summary
        if all_accounts:
            print(f"  [OK] Found {len(all_accounts)} account(s)")
            print(f"    Total Revenue: ${total_revenue:,.0f}K")
            print(f"    Total Headcount: {total_headcount:,.0f}")
            if zero_revenue_accounts:
                print(f"    [!] {len(zero_revenue_accounts)} account(s) with $0 revenue (flag for removal)")
        else:
            print(f"  [!] No accounts found")
        print()
    
    # Generate detailed report
    print("=" * 80)
    print("DETAILED REPORT BY ACCOUNT DIRECTOR")
    print("=" * 80)
    print()
    
    for ad_name in sorted(ad_results.keys()):
        result = ad_results[ad_name]
        
        print(f"\n{'=' * 80}")
        print(f"{ad_name}")
        print(f"{'=' * 80}")
        print(f"Total Accounts: {result['num_accounts']}")
        print(f"Total Revenue: ${result['total_revenue']:,.0f}K")
        print(f"Total Headcount: {result['total_headcount']:,.0f}")
        print()
        
        if result['accounts']:
            print("ACCOUNTS:")
            for acc in result['accounts']:
                status = "[!] $0 REVENUE - REMOVE" if acc['zero_revenue'] else "[OK]"
                print(f"  {status} {acc['account']}")
                print(f"      Source: {acc['csv_file']}")
                print(f"      Revenue: ${acc['revenue']:,.0f}K")
                print(f"      Headcount: {acc['headcount']:,.0f}")
                print()
        else:
            print("  [!] NO ACCOUNTS FOUND")
        
        if result['zero_revenue_accounts']:
            print(f"[!] ACTION REQUIRED: Remove {len(result['zero_revenue_accounts'])} account(s) with $0 revenue")
            print()
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    ads_with_accounts = sum(1 for r in ad_results.values() if r['num_accounts'] > 0)
    ads_without_accounts = len(ad_results) - ads_with_accounts
    total_accounts = sum(r['num_accounts'] for r in ad_results.values())
    total_zero_revenue = sum(len(r['zero_revenue_accounts']) for r in ad_results.values())
    
    print(f"ADs with accounts: {ads_with_accounts}")
    print(f"ADs without accounts: {ads_without_accounts}")
    print(f"Total accounts found: {total_accounts}")
    print(f"Accounts with $0 revenue (to remove): {total_zero_revenue}")
    print()
    
    # Export to CSV
    export_path = "AD_Account_Audit_Report.csv"
    with open(export_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Account Director', 'Account Name', 'Source File', 'Revenue ($K)', 'Headcount', 'Zero Revenue Flag', 'Total Revenue', 'Total Headcount'])
        
        for ad_name in sorted(ad_results.keys()):
            result = ad_results[ad_name]
            
            if result['accounts']:
                for i, acc in enumerate(result['accounts']):
                    writer.writerow([
                        ad_name if i == 0 else '',
                        acc['account'],
                        acc['csv_file'],
                        acc['revenue'],
                        acc['headcount'],
                        'YES - REMOVE' if acc['zero_revenue'] else 'NO',
                        result['total_revenue'] if i == 0 else '',
                        result['total_headcount'] if i == 0 else ''
                    ])
            else:
                writer.writerow([ad_name, 'NO ACCOUNTS FOUND', '', 0, 0, '', 0, 0])
    
    print(f"[OK] Detailed report exported to: {export_path}")
    print()

if __name__ == "__main__":
    audit_all_ads()
