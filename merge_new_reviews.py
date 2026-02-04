import csv

def merge_new_reviews():
    """Merge new reviews from the unclean file into cleaned file."""
    
    # Read cleaned file
    print("Reading cleaned file...")
    with open('data/performance_reviews.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cleaned_reviews = list(reader)
        fieldnames = reader.fieldnames
    
    print(f"Cleaned file has {len(cleaned_reviews)} entries")
    last_id = int(cleaned_reviews[-1]['Id'])
    print(f"Last ID in cleaned file: {last_id}")
    
    # Read new file
    print("\nReading new file...")
    with open('data/Year-End Review_ Account Director Leadership Evaluation(Sheet1) (5) (1).csv', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_reviews = list(reader)
        new_fieldnames = reader.fieldnames
    
    print(f"New file has {len(all_reviews)} entries")
    
    # Find entries with ID > last_id
    new_entries = [r for r in all_reviews if int(r['Id']) > last_id]
    print(f"\nFound {len(new_entries)} new entries (IDs {last_id + 1} to {int(all_reviews[-1]['Id'])})")
    
    if len(new_entries) == 0:
        print("No new entries to add!")
        return
    
    # Clean the new entries - use "Enter Your Name" field as the reviewer name
    print("\nCleaning new entries...")
    cleaned_new = []
    for entry in new_entries:
        # Create cleaned entry
        cleaned_entry = {}
        for field in fieldnames:
            if field == 'Name':
                # Use "Enter Your Name" field if available, otherwise use "Name" field
                reviewer_name = entry.get('Enter Your Name', '').strip()
                if not reviewer_name:
                    reviewer_name = entry.get('Name', '').strip()
                cleaned_entry['Name'] = reviewer_name
            else:
                cleaned_entry[field] = entry.get(field, '')
        
        cleaned_new.append(cleaned_entry)
        print(f"  ID {cleaned_entry['Id']}: {cleaned_entry['Name']} -> {cleaned_entry['Account Director Name']}")
    
    # Append to cleaned file
    print(f"\nAppending {len(cleaned_new)} new entries to performance_reviews.csv...")
    with open('data/performance_reviews.csv', 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(cleaned_new)
    
    print(f"\n[SUCCESS] Successfully added {len(cleaned_new)} new reviews!")
    print(f"   performance_reviews.csv now has {len(cleaned_reviews) + len(cleaned_new)} total entries")
    
    # Show summary
    print("\n" + "=" * 80)
    print("NEW ENTRIES ADDED:")
    print("=" * 80)
    
    from collections import defaultdict
    ad_counts = defaultdict(int)
    reviewer_counts = defaultdict(int)
    
    for entry in cleaned_new:
        ad_counts[entry['Account Director Name'].strip()] += 1
        reviewer_counts[entry['Name'].strip()] += 1
    
    print("\nAccount Directors with new reviews:")
    for ad, count in sorted(ad_counts.items()):
        if ad:
            print(f"  - {ad}: {count} new review(s)")
    
    print("\nReviewers who added reviews:")
    for reviewer, count in sorted(reviewer_counts.items()):
        if reviewer:
            print(f"  - {reviewer}: {count} review(s)")

if __name__ == "__main__":
    merge_new_reviews()
