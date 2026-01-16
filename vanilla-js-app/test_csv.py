import pandas as pd

# Load CSV
df = pd.read_csv('../data/performance_reviews.csv', low_memory=False)

print("=" * 60)
print("COLUMN STRUCTURE CHECK")
print("=" * 60)

# Show first 10 columns
print(f"\nTotal columns: {len(df.columns)}")
print(f"\nFirst 10 column names:")
for i, col in enumerate(df.columns[:10]):
    print(f"  Col {i}: {col[:60]}...")  # Truncate long names

# Show columns 8-15 (the scoring columns)
print(f"\nColumns 8-15 (scoring area):")
for i in range(8, min(16, len(df.columns))):
    col_name = df.columns[i]
    print(f"  Col {i}: {col_name[:80]}")

# Test first data row
print("\n" + "=" * 60)
print("FIRST DATA ROW (Benjamin Ehrenberg)")
print("=" * 60)

row = df.iloc[0]
print(f"\nAccount Director: {row['Account Director Name']}")
print(f"Reviewer: {row['Name']}")

print(f"\nFirst 4 feedback/score pairs:")
for i in range(8, 16, 2):
    feedback_col = df.columns[i]
    score_col = df.columns[i+1]
    
    feedback_val = str(row.iloc[i])[:60] + "..." if len(str(row.iloc[i])) > 60 else row.iloc[i]
    score_val = row.iloc[i+1]
    
    print(f"\n  Section: {score_col}")
    print(f"  Feedback: {feedback_val}")
    print(f"  Score: {score_val}")

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)

