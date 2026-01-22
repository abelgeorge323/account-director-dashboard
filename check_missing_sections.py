import pandas as pd
from collections import defaultdict
from generate_report import load_data, get_score_columns, calculate_rankings

df, _, _ = load_data()
rankings = calculate_rankings(df)

print(f'Total sections found: {len(rankings)}\n')

# Count how many sections each AD appears in
ad_section_count = defaultdict(int)
for section, ads in rankings.items():
    for ad in ads:
        ad_section_count[ad['name']] += 1

# Find ADs missing sections
print('ADs MISSING SECTIONS:')
print('='*50)
missing = False
for ad_name in sorted(ad_section_count.keys()):
    count = ad_section_count[ad_name]
    if count < 8:
        print(f'{ad_name}: Only in {count}/8 sections (MISSING {8-count})')
        missing = True

if not missing:
    print('✅ All ADs have complete reviews in all 8 sections!')
        
print('\n✅ Complete (all 8 sections):')
for ad_name in sorted(ad_section_count.keys()):
    if ad_section_count[ad_name] == 8:
        print(f'  {ad_name}')