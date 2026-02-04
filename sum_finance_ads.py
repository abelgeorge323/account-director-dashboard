print("=" * 80)
print("FINANCE REVENUE - SELECTED ADs")
print("=" * 80)
print()

# The 6 ADs and their revenue
ads = {
    "Colleen Doles": 2058,
    "Tiffany Purifoy": 1192,
    "Julie Bianchi": 501,
    "Corey Wallace": 461,
    "Peggy Shum": 428,
    "Berenday Escamilla": 419
}

total = 0
for ad, revenue in sorted(ads.items(), key=lambda x: x[1], reverse=True):
    total += revenue
    print(f"  {ad:30} ${revenue:>10,}K (${revenue/1000:>5.2f}M)")

print()
print("=" * 80)
print(f"TOTAL FOR 6 ADs:             ${total:>10,}K (${total/1000:>5.2f}M)")
print("=" * 80)
print()

# Compare to total Finance
total_finance = 5418
pct = (total / total_finance) * 100
print(f"Total Finance Revenue:       ${total_finance:>10,}K (${total_finance/1000:>5.2f}M)")
print(f"Percentage of Total:         {pct:>10.1f}%")
print()
print("=" * 80)
