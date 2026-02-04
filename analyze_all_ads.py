import csv
from collections import defaultdict
import os

def analyze_reviews():
    """Comprehensive analysis of who has been reviewed."""
    
    # Read the cleaned performance reviews
    with open('data/performance_reviews.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reviews = list(reader)
    
    # Group reviews by Account Director (normalize names)
    ad_reviewers = defaultdict(list)
    
    for row in reviews:
        ad_name = row['Account Director Name'].strip()
        reviewer_name = row['Name'].strip()
        account = row['Account Name'].strip()
        
        if ad_name and reviewer_name:
            ad_reviewers[ad_name].append({
                'reviewer': reviewer_name,
                'account': account
            })
    
    # Get list of all AD CSV files
    ad_csv_dir = 'data/ad_csvs'
    all_ad_files = []
    if os.path.exists(ad_csv_dir):
        all_ad_files = [f.replace('.csv', '').replace('-', ' ').title() 
                       for f in os.listdir(ad_csv_dir) if f.endswith('.csv')]
    
    # Sort ADs alphabetically
    sorted_ads = sorted(ad_reviewers.keys())
    
    print("=" * 80)
    print("COMPLETE ANALYSIS: WHO HAS COMPLETED EOY REVIEWS")
    print("=" * 80)
    print(f"\nTotal Account Directors Reviewed: {len(sorted_ads)}")
    print(f"Total Reviews Conducted: {len(reviews)}")
    print(f"Total AD CSV Files Found: {len(all_ad_files)}")
    print("\n" + "=" * 80 + "\n")
    
    # Print detailed breakdown for each AD
    for i, ad in enumerate(sorted_ads, 1):
        reviews_list = ad_reviewers[ad]
        print(f"{i}. {ad}")
        print(f"   Total Reviews: {len(reviews_list)}")
        print(f"   Reviewed by:")
        
        for review in reviews_list:
            print(f"      - {review['reviewer']} (Account: {review['account']})")
        print()
    
    # Summary by reviewer
    print("\n" + "=" * 80)
    print("SUMMARY: REVIEWS COMPLETED BY EACH PERSON")
    print("=" * 80 + "\n")
    
    reviewer_counts = defaultdict(int)
    for ad, reviews_list in ad_reviewers.items():
        for review in reviews_list:
            reviewer_counts[review['reviewer']] += 1
    
    # Combine variations (Nick Viskovich vs NIck Viskovich, etc.)
    combined_counts = {}
    for reviewer, count in reviewer_counts.items():
        # Normalize
        normalized = reviewer.lower().strip()
        if 'viskovich' in normalized:
            key = 'Nick Viskovich'
        elif 'follman' in normalized:
            key = 'Shane Follmann'
        elif 'jedan' in normalized:
            key = 'Mike Jedan'
        else:
            key = reviewer
        
        combined_counts[key] = combined_counts.get(key, 0) + count
    
    for reviewer, count in sorted(combined_counts.items(), key=lambda x: x[1], reverse=True):
        if reviewer:  # Skip empty names
            print(f"{reviewer}: {count} reviews")
    
    print("\n" + "=" * 80)
    print("POTENTIAL MISSING ADs (have CSV files but no reviews recorded)")
    print("=" * 80 + "\n")
    
    # Check who might be missing
    reviewed_ads_normalized = {ad.lower().replace(' ', '').replace('-', '') 
                               for ad in sorted_ads}
    
    missing = []
    for ad_file in sorted(all_ad_files):
        ad_normalized = ad_file.lower().replace(' ', '').replace('-', '')
        if ad_normalized not in reviewed_ads_normalized:
            missing.append(ad_file)
    
    if missing:
        for ad in missing:
            print(f"  - {ad}")
        print(f"\nTotal potentially missing: {len(missing)}")
    else:
        print("  All ADs with CSV files have been reviewed!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    analyze_reviews()
