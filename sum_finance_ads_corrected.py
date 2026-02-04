print("=" * 80)
print("FINANCE REVENUE - SELECTED ADs (CORRECTED)")
print("=" * 80)
print()

# The 6 ADs and their revenue
ads = {
    "Colleen Doles": {"accounts": ["Wells Fargo"], "revenue": 2058},
    "Tiffany Purifoy": {"accounts": ["Charles Schwab", "Citibank", "Fidelity", "T Rowe Price", "State Farm Ins"], "revenue": 1192},
    "Julie Bianchi": {"accounts": ["CIGNA", "Elevance Health"], "revenue": 501},
    "Corey Wallace": {"accounts": ["Geico"], "revenue": 461},
    "Peggy": {"accounts": ["Deutsche Bank", "Chubb Insurance"], "revenue": 428 + 119},  # Combined!
    "Berenday Escamilla": {"accounts": ["USAA"], "revenue": 419}
}

total = 0
for ad, data in sorted(ads.items(), key=lambda x: x[1]["revenue"], reverse=True):
    revenue = data["revenue"]
    accounts = data["accounts"]
    total += revenue
    print(f"  {ad:30} ${revenue:>10,}K (${revenue/1000:>5.2f}M)")
    for account in accounts:
        print(f"    - {account}")

print()
print("=" * 80)
print(f"TOTAL FOR 6 ADs:             ${total:>10,}K (${total/1000:>5.2f}M)")
print("=" * 80)
print()

# Compare to total Finance
total_finance = 5418
pct = (total / total_finance) * 100
remaining = total_finance - total
print(f"Total Finance Revenue:       ${total_finance:>10,}K (${total_finance/1000:>5.2f}M)")
print(f"Your 6 ADs:                  ${total:>10,}K (${total/1000:>5.2f}M) - {pct:.1f}%")
print(f"Remaining (Other ADs + TBH): ${remaining:>10,}K (${remaining/1000:>5.2f}M) - {(remaining/total_finance)*100:.1f}%")
print()
print("=" * 80)
