accounts = {
    "3M Corp": 4457,
    "ABB Supply": 0,
    "Aerospace District Lodge": 0,
    "Alfa Laval": 0,
    "American Medical Systems": 0,
    "Anheuser Busch": 59997,
    "Applied Materials": 0,
    "ASML Holding": 0,
    "Ball Corporation": 245912,
    "Boeing Company": 1001952,
    "Bombardier Learjet": 0,
    "Brown Forman": 0,
    "Caterpillar": 0,
    "Chemours Company": 28606,
    "Cinram": 0,
    "Clorox Company": 127070,
    "Coca-Cola": 195106,
    "Covestro": 46692,
    "Danfoss Power Solutions": 155881,
    "Duke Energy": 0,
    "DuPont": 42051,
    "Duracell": 0,
    "Encore Aerojet Rocketdyne": 0,
    "Exxon Mobile": 0,
    "Fanatics": 20387,
    "Flextronics": 0,
    "Gallo Wine": 159470,
    "GE Healthcare": 358847,
    "General Dynamics": 283466,
    "General Electric": 708291,
    "GE Power": 109325,
    "Hasbro": 47850,
    "Henkel": 0,
    "Honeywell International": 0,
    "Hughes Christensen": 0,
    "Hyliion": 13741,
    "JDS Uniphase Corporation": 0,
    "Jireh Semiconductor": 0,
    "John Deere": 0,
    "Johnson Controls": 0,
    "JSR Micro": 5475,
    "Lockheed Martin": 967738,
    "Mars": 738762,
    "Micro Motion": 0,
    "Molson Coors": 156052,
    "Mondi Jackson": 0,
    "Nestle": 645657,
    "Newell Brands": 31761,
    "Nilfisk": 0,
    "Northrop Grumman": 211679,
    "Omnivision": 0,
    "Otis Elevator Company": 0,
    "Parsons Corporation": 4197,
    "Philips": 0,
    "Piper Aircraft": 0,
    "Procter & Gamble Company": 733293,
    "Rolls Royce": 0,
    "S.C. Johnson": 86888,
    "Schneider Electric": 0,
    "Shell": 0,
    "Sikorsky": 0,
    "Solidigm": 0,
    "Spirit Aerosystems": 405520,
    "Stanley Black & Decker": 0,
    "Taiwan Semiconductor": 0,
    "Texas Instruments": 0,
    "Textron Aviation": 1504446,
    "Trane": 0,
    "UCAR": 75757,
    "United Technologies": 317579,
    "W.L. Gore": 39224,
    "Wabash National Corporation": 0,
    "Westinghouse": 326747,
    "Wieland Group": 54526,
    "Workspace Properties": 38940
}

total = sum(accounts.values())
total_with_revenue = sum(1 for v in accounts.values() if v > 0)

print(f"Total Accounts: {len(accounts)}")
print(f"Accounts with Revenue: {total_with_revenue}")
print(f"Accounts with No Revenue: {len(accounts) - total_with_revenue}")
print(f"\nTotal Revenue (if in dollars): ${total:,}")
print(f"Total Revenue (if in dollars): ${total/1_000_000:.2f}M")
print(f"\nTotal Revenue (if in thousands): ${total:,}K")
print(f"Total Revenue (if in thousands): ${total/1000:.2f}M")

# Show top 10
print("\nTop 10 Accounts by Revenue:")
sorted_accounts = sorted(accounts.items(), key=lambda x: x[1], reverse=True)
for i, (account, revenue) in enumerate(sorted_accounts[:10], 1):
    if revenue > 0:
        print(f"{i:2}. {account:35} ${revenue:,}")
