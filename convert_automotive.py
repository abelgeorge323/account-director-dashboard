"""
Convert AUTOMOTIVE.csv to standard format for Jacob Reed
"""
import pandas as pd
import re

# Read the automotive data (skip the header rows)
df = pd.read_csv('data/AUTOMOTIVE.csv', skiprows=5)

# Initialize list to store standardized rows
standardized_rows = []

# Process the data
current_account = None
kpi_map = {
    'Revenue ($)': 'Revenue ($)',
    'Growth (%)': 'Growth (%)',
    'Gap ($)': 'Gap ($)',
    'Red Sites ($)': 'Red Sites ($)',
    'Red Sites (#)': 'Red Sites (#)',
    'Headcount': 'Headcount',
    'Separations': 'Separations',
    'Turnover (%)': 'Turnover (%)',
    'CSAT': 'CSAT',
    'YTD Claims': 'YTD Claims',
    'YTD Recordables': 'YTD Recordables',
    'TRIR': 'TRIR'
}

for idx, row in df.iterrows():
    first_col = str(row.iloc[0]).strip()
    
    # Check if this is an account name (no numbers in the row)
    if pd.notna(first_col) and first_col and first_col not in kpi_map:
        # This is an account name
        current_account = first_col
    elif current_account and first_col in kpi_map:
        # This is a KPI row
        kpi = kpi_map[first_col]
        
        # Create row for each month
        row_data = {
            'Account': current_account,
            'Vertical': 'AUTOMOTIVE',
            'KPI': kpi
        }
        
        # Add monthly data (Dec-24 through Dec-25)
        for col in df.columns[1:14]:  # Skip first column and last column
            val = row[col]
            # Clean the value
            if pd.isna(val) or val == '-' or val == '':
                val = ''
            else:
                # Remove % signs, commas, parentheses
                val = str(val).replace('%', '').replace(',', '').replace('(', '-').replace(')', '').strip()
            row_data[col] = val
        
        standardized_rows.append(row_data)

# Create standardized DataFrame
result_df = pd.DataFrame(standardized_rows)

# Save to jacob-reed.csv
result_df.to_csv('data/ad_csvs/jacob-reed.csv', index=False)

print(f"SUCCESS: Converted AUTOMOTIVE.csv to jacob-reed.csv")
print(f"  - {len(result_df)} rows")
print(f"  - Accounts: {result_df['Account'].nunique()}")
print(f"\nFirst few rows:")
print(result_df.head(15).to_string())
