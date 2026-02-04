import csv

# Read all rows
with open('data/performance_reviews.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    all_rows = list(reader)

print(f'Before: {len(all_rows)} total rows')

# Check what's in rows 10, 11
print(f'\nRow 10 ID: {all_rows[10][0] if len(all_rows) > 10 else "N/A"}')
print(f'Row 11 ID: {all_rows[11][0] if len(all_rows) > 11 else "N/A"}')

# Find rows with Brian Davis 1/9 reviews (old ones)
rows_to_delete = []
for i, row in enumerate(all_rows[1:], 1):  # Skip header
    if len(row) > 6:
        date = row[1]  # Start time
        ad_name = row[6]  # Account Director Name
        
        if 'Brian Davis' in ad_name and date.startswith('1/9/2026'):
            rows_to_delete.append(i)
            print(f'Found old Brian review: Row {i}, ID={row[0]}, Date={date[:10]}')

# Also find old Peggy review
for i, row in enumerate(all_rows[1:], 1):
    if len(row) > 6:
        date = row[1]
        ad_name = row[6]
        reviewer = row[4]  # Name column
        
        if 'Peggy Shum' in ad_name and date.startswith('1/15/2026') and 'Shane' in reviewer:
            rows_to_delete.append(i)
            print(f'Found old Peggy review: Row {i}, ID={row[0]}, Date={date[:10]}, Reviewer={reviewer}')

print(f'\nRows to delete: {sorted(set(rows_to_delete))}')

# Keep header and all rows except the ones to delete
filtered_rows = [all_rows[0]]
filtered_rows.extend([row for i, row in enumerate(all_rows[1:], 1) if i not in rows_to_delete])

print(f'After: {len(filtered_rows)} rows')

# Write back
with open('data/performance_reviews.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(filtered_rows)

print('SUCCESS: Deleted old reviews')
