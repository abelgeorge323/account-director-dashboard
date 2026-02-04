print("=" * 80)
print("MANUFACTURING REVENUE BY REPORTING GROUPS")
print("=" * 80)
print()

# Group 1: Nicholas Trenkamp + Logan Newman + Jennifer Segovia + Kimberly Wittekind
print("GROUP 1: Nicholas Trenkamp, Logan Newman, Jennifer Segovia, Kimberly Wittekind")
print("-" * 80)
group1 = [
    ("Nicholas Trenkamp", [733293]),
    ("Logan Newman", [708291, 109325, 13741]),
    ("Jennifer Segovia", [283466, 211679]),
    ("Kimberly Wittekind", [645657, 358847])
]
group1_total = 0
for ad, revenues in group1:
    ad_total = sum(revenues)
    group1_total += ad_total
    print(f"  {ad:30} ${ad_total:>12,} (${ad_total/1_000_000:>5.2f}M)")
print(f"\n  GROUP 1 TOTAL:                 ${group1_total:>12,} (${group1_total/1_000_000:>5.2f}M)")

# Group 2: Kyle Wallace + Justin Dallavis
print()
print("GROUP 2: Kyle Wallace, Justin Dallavis")
print("-" * 80)
group2 = [
    ("Kyle Wallace", [1504446, 405520]),
    ("Justin Dallavis", [1001952])
]
group2_total = 0
for ad, revenues in group2:
    ad_total = sum(revenues)
    group2_total += ad_total
    print(f"  {ad:30} ${ad_total:>12,} (${ad_total/1_000_000:>5.2f}M)")
print(f"\n  GROUP 2 TOTAL:                 ${group2_total:>12,} (${group2_total/1_000_000:>5.2f}M)")

# Group 3: Aaron Simpson
print()
print("GROUP 3: Aaron Simpson")
print("-" * 80)
group3 = [
    ("Aaron Simpson", [738762, 245912, 4457])
]
group3_total = 0
for ad, revenues in group3:
    ad_total = sum(revenues)
    group3_total += ad_total
    print(f"  {ad:30} ${ad_total:>12,} (${ad_total/1_000_000:>5.2f}M)")
print(f"\n  GROUP 3 TOTAL:                 ${group3_total:>12,} (${group3_total/1_000_000:>5.2f}M)")

# Group 4: Benjamin Ehrenberg
print()
print("GROUP 4: Benjamin Ehrenberg")
print("-" * 80)
group4 = [
    ("Benjamin Ehrenberg", [967738, 4197])
]
group4_total = 0
for ad, revenues in group4:
    ad_total = sum(revenues)
    group4_total += ad_total
    print(f"  {ad:30} ${ad_total:>12,} (${ad_total/1_000_000:>5.2f}M)")
print(f"\n  GROUP 4 TOTAL:                 ${group4_total:>12,} (${group4_total/1_000_000:>5.2f}M)")

# Group 5: Ayesha Nasir
print()
print("GROUP 5: Ayesha Nasir")
print("-" * 80)
group5 = [
    ("Ayesha Nasir", [326747, 42051])
]
group5_total = 0
for ad, revenues in group5:
    ad_total = sum(revenues)
    group5_total += ad_total
    print(f"  {ad:30} ${ad_total:>12,} (${ad_total/1_000_000:>5.2f}M)")
print(f"\n  GROUP 5 TOTAL:                 ${group5_total:>12,} (${group5_total/1_000_000:>5.2f}M)")

# Grand total
print()
print("=" * 80)
print("SUMMARY BY REPORTING GROUP")
print("=" * 80)
grand_total = group1_total + group2_total + group3_total + group4_total + group5_total

print(f"\nGroup 1 (4 ADs):                 ${group1_total:>12,} (${group1_total/1_000_000:>5.2f}M) - {group1_total/grand_total*100:>5.1f}%")
print(f"Group 2 (2 ADs):                 ${group2_total:>12,} (${group2_total/1_000_000:>5.2f}M) - {group2_total/grand_total*100:>5.1f}%")
print(f"Group 3 (1 AD):                  ${group3_total:>12,} (${group3_total/1_000_000:>5.2f}M) - {group3_total/grand_total*100:>5.1f}%")
print(f"Group 4 (1 AD):                  ${group4_total:>12,} (${group4_total/1_000_000:>5.2f}M) - {group4_total/grand_total*100:>5.1f}%")
print(f"Group 5 (1 AD):                  ${group5_total:>12,} (${group5_total/1_000_000:>5.2f}M) - {group5_total/grand_total*100:>5.1f}%")
print(f"\nTOTAL (9 ADs):                   ${grand_total:>12,} (${grand_total/1_000_000:>5.2f}M)")
print("=" * 80)
