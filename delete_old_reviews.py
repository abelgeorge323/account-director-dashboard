import csv

# Read the CSV
with open('data/performance_reviews.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

print(f'Total rows before: {len(rows)}')

# Keep header and all rows except rows 10, 11, 31 (0-indexed: 10, 11, 31)
# Row 10 = Brian Davis - Valarie (1/9)
# Row 11 = Brian Davis - Marvin (1/9)
# Row 31 = Peggy Shum - Shane (1/15)
filtered_rows = [rows[0]]  # Keep header
filtered_rows.extend([r for i, r in enumerate(rows[1:], 1) if i not in [10, 11, 31]])

print(f'Total rows after: {len(filtered_rows)}')
print(f'Deleted: Row 10 (Brian-Valarie 1/9), Row 11 (Brian-Marvin 1/9), Row 31 (Peggy-Shane 1/15)')

# Write back to CSV
with open('data/performance_reviews.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(filtered_rows)

print('SUCCESS: Old reviews deleted from performance_reviews.csv')
