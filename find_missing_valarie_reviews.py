import pandas as pd

print("=" * 80)
print("ANALYZING VALARIE BARNETT'S REVIEWS")
print("=" * 80)
print()

# Load performance reviews
df = pd.read_csv('data/performance_reviews.csv')

# Get all unique ADs
all_ads = set(df['Account Director Name'].unique())

# Get ADs Valarie has reviewed
valarie_reviews = df[df['Name'].str.contains('Valarie', na=False, case=False)]
valarie_ads = set(valarie_reviews['Account Director Name'].unique())

# Find who's missing
missing_ads = all_ads - valarie_ads

print(f"Total ADs in system: {len(all_ads)}")
print(f"ADs Valarie has reviewed: {len(valarie_ads)}")
print(f"ADs Valarie has NOT reviewed: {len(missing_ads)}")
print()

# Show who Valarie HAS reviewed
print("=" * 80)
print("ADs VALARIE HAS REVIEWED:")
print("=" * 80)
for ad in sorted(valarie_ads):
    accounts = df[(df['Account Director Name'] == ad) & (df['Name'].str.contains('Valarie', na=False, case=False))]['Account Name'].unique()
    print(f"\n[DONE] {ad}")
    for acc in accounts:
        print(f"    - {acc}")

# Show who Valarie HAS NOT reviewed
print()
print("=" * 80)
print("ADs VALARIE HAS NOT REVIEWED YET:")
print("=" * 80)
if len(missing_ads) == 0:
    print("\n[ALL COMPLETE] Valarie has reviewed everyone!")
else:
    for ad in sorted(missing_ads):
        accounts = df[df['Account Director Name'] == ad]['Account Name'].unique()
        print(f"\n[MISSING] {ad}")
        for acc in accounts:
            print(f"    - {acc}")
        
        # Show who DID review them
        reviewers = df[df['Account Director Name'] == ad]['Name'].dropna().unique()
        reviewer_names = [str(r) for r in reviewers if str(r) != 'nan']
        if reviewer_names:
            print(f"    Reviewed by: {', '.join(reviewer_names)}")

print()
print("=" * 80)
