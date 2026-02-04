import csv
from collections import defaultdict

def compile_reviewers(filename='data/performance_reviews.csv'):
    """Compile who reviewed each Account Director."""
    
    # Read the performance reviews
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Group reviews by Account Director
    ad_reviewers = defaultdict(list)
    
    for row in data:
        ad_name = row['Account Director Name'].strip()
        reviewer_name = row['Name'].strip()
        account = row['Account Name'].strip()
        
        if ad_name and reviewer_name:
            ad_reviewers[ad_name].append({
                'reviewer': reviewer_name,
                'account': account
            })
    
    # Sort ADs alphabetically
    sorted_ads = sorted(ad_reviewers.keys())
    
    print("=" * 80)
    print("ACCOUNT DIRECTORS REVIEWED - WITH ALL REVIEWERS")
    print("=" * 80)
    print(f"\nTotal Account Directors Reviewed: {len(sorted_ads)}")
    print(f"Total Reviews Conducted: {len(data)}")
    print("\n" + "=" * 80 + "\n")
    
    # Print detailed breakdown
    for i, ad in enumerate(sorted_ads, 1):
        reviews = ad_reviewers[ad]
        print(f"{i}. {ad}")
        print(f"   Total Reviews: {len(reviews)}")
        print(f"   Reviewed by:")
        
        for review in reviews:
            print(f"      - {review['reviewer']} (Account: {review['account']})")
        print()
    
    # Summary by reviewer
    print("\n" + "=" * 80)
    print("SUMMARY: REVIEWS COMPLETED BY EACH PERSON")
    print("=" * 80 + "\n")
    
    reviewer_counts = defaultdict(int)
    for ad, reviews in ad_reviewers.items():
        for review in reviews:
            reviewer_counts[review['reviewer']] += 1
    
    for reviewer, count in sorted(reviewer_counts.items(), key=lambda x: x[1], reverse=True):
        if reviewer:  # Skip empty names
            print(f"{reviewer}: {count} reviews")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ANALYZING: data/performance_reviews.csv (CLEANED FILE)")
    print("=" * 80)
    compile_reviewers('data/performance_reviews.csv')
    
    print("\n\n" + "=" * 80)
    print("ANALYZING: NEW FILE (ALL ENTRIES)")
    print("=" * 80)
    compile_reviewers('data/Year-End Review_ Account Director Leadership Evaluation(Sheet1) (5) (1).csv')
