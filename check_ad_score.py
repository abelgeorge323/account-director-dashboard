import pandas as pd
from collections import defaultdict

def check_ad_score(ad_name):
    """Check overall score for a specific AD"""
    df = pd.read_csv("data/performance_reviews.csv", low_memory=False)
    
    # Split joint reviews
    expanded_rows = []
    for _, row in df.iterrows():
        name = str(row.get("Account Director Name", "")).strip()
        if "/" in name:
            names = [n.strip() for n in name.split("/")]
            for n in names:
                new_row = row.copy()
                new_row["Account Director Name"] = n
                expanded_rows.append(new_row)
        else:
            expanded_rows.append(row)
    
    df = pd.DataFrame(expanded_rows)
    
    # Get score columns
    score_cols = []
    for col in df.columns:
        if any(k in col for k in [
            "Key Projects", "Value Adds", "Cost Savings", 
            "Innovation", "Issues", "2026", "Personal Goals", 
            "Executive Presence"
        ]) and "Comment" not in col:
            score_cols.append(col)
    
    # Get AD's reviews
    ad_reviews = df[df["Account Director Name"].str.strip() == ad_name.strip()]
    
    if ad_reviews.empty:
        print(f"❌ No reviews found for {ad_name}")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 {ad_name} - Score Summary")
    print(f"{'='*60}\n")
    
    print(f"Reviewers: {len(ad_reviews)}")
    for _, row in ad_reviews.iterrows():
        reviewer = row.get("Enter Your Name", "Anonymous")
        print(f"  • {reviewer}")
    
    print(f"\n{'Section':<50} {'Avg Score':<10}")
    print("-" * 60)
    
    total_score = 0
    sections_scored = 0
    
    for col in score_cols:
        scores = []
        for _, row in ad_reviews.iterrows():
            score = row.get(col)
            if pd.notna(score) and score != "":
                try:
                    scores.append(float(score))
                except:
                    pass
        
        if scores:
            avg = sum(scores) / len(scores)
            total_score += avg
            sections_scored += 1
            print(f"{col[:48]:<50} {avg:.2f}/5.0")
        else:
            print(f"{col[:48]:<50} N/A")
    
    print("-" * 60)
    print(f"\n🎯 OVERALL SCORE: {total_score:.1f} / 40.0")
    print(f"   (Average: {total_score/8:.2f}/5.0 across {sections_scored} sections)\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        ad_name = " ".join(sys.argv[1:])
    else:
        ad_name = "Justin Homa"
    
    check_ad_score(ad_name)

