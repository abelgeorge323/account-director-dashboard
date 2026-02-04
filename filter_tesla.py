"""
Filter jacob-reed.csv to only include Tesla
"""
import pandas as pd

# Read the full automotive data
df = pd.read_csv('data/ad_csvs/jacob-reed.csv')

# Filter to Tesla only
tesla_df = df[df['Account'] == 'Tesla Inc - Jacob Reed'].copy()

# Save
tesla_df.to_csv('data/ad_csvs/jacob-reed.csv', index=False)

print(f"SUCCESS: Filtered jacob-reed.csv to Tesla only")
print(f"  - {len(tesla_df)} rows (Tesla data only)")
print(f"\nSample:")
print(tesla_df.head(10).to_string())
