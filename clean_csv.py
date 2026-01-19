"""Clean the performance review CSV with all normalizations."""
import csv

# Read the input CSV
with open('data/Year-End Review_ Account Director Leadership Evaluation(Sheet1) (2).csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Apply all fixes
for i, row in enumerate(rows):
    if i == 0:  # Skip header
        continue
    
    if len(row) < 7:  # Skip empty or incomplete rows
        continue
    
    # Fix Account Director names
    if row[6]:  # Account Director Name column
        ad_name = row[6].strip()
        
        # Fix Benjamin Ehrenberger
        if ad_name == "Benjamin Ehrenberger":
            row[6] = "Benjamin Ehrenberg"
        
        # Fix Stu Kelloff
        if ad_name == "Stu Kelloff ":
            row[6] = "Stuart Kelloff"
        
        # Fix Maravilla names
        if ad_name == "Maravilla Evelyn Jacqueline":
            row[6] = "Jacqueline Maravilla"
        if ad_name == "Jaqueline Maravilla ":
            row[6] = "Jacqueline Maravilla"
        
        # Fix Jack Thorton
        if ad_name == "Jack Thorton" or ad_name == "Jack Thorton ":
            row[6] = "Jack Thornton"
        
        # Fix isaac calderon
        if ad_name == "isaac calderon":
            row[6] = "Isaac Calderon"
    
    # Fix reviewer names for rows 7-9 (Ben's reviews)
    if i == 7:  # Row 7 (ID=2)
        row[4] = "Shane Follmann"
        row[3] = "sfollmann@sbmcorp.com"
    elif i == 8:  # Row 8 (ID=3)
        row[4] = "Ryan Blackwood"
        row[3] = "rblackwood@sbmcorp.com"
    elif i == 9:  # Row 9 (ID=4)
        row[4] = "Valarie Barnett"
        row[3] = "vbarnett@sbmcorp.com"
    
    # Fix anonymous reviewer names using "Enter Your Name" column (index 7)
    if row[3] == "anonymous" and len(row) > 7 and row[7]:
        reviewer_name = row[7].strip()
        if reviewer_name:
            # Map names to emails
            email_map = {
                "Valarie Barnett": "vbarnett@sbmcorp.com",
                "Luna Duarte": "lduarte@sbmcorp.com",
                "Shane Follmann": "sfollmann@sbmcorp.com",
                "Shane Follmann ": "sfollmann@sbmcorp.com",
                "Melissa Hampton": "mhampton@sbmcorp.com",
                "Yousef Abbasi": "yabbasi@sbmcorp.com",
                "Kyle Wallace": "kwallace@sbmcorp.com",
                "Dan Hartman": "dhartman@sbmcorp.com",
                "NIck Viskovich": "nviskovich@sbmcorp.com",
                "Nick Viskovich": "nviskovich@sbmcorp.com",
                "Mike Jedan": "mjedan@sbmcorp.com",
                "mike jedan": "mjedan@sbmcorp.com",
                "Marvin Owens": "mowens@sbmcorp.com",
                "Zach Shock": "zshock@sbmcorp.com"
            }
            row[4] = reviewer_name.strip()
            row[3] = email_map.get(reviewer_name.strip(), "unknown@sbmcorp.com")
    
    # Normalize account names
    if row[5]:  # Account Name column
        account = row[5].strip()
        
        # Normalize Mark Schlerf accounts
        if account in ["HP LAM Xerox and others ", "LAM / HP", "HP/Lam/Xerox", "HP / LAM / Xerox"]:
            row[5] = "HP/LAM/Xerox"
        
        # Normalize Grant Frazier accounts
        if account in ["Meta ", "META", "Meta"]:
            row[5] = "Meta"
        
        # Normalize Merck
        if account in ["Merck ", "Merck"]:
            row[5] = "Merck"
        if account == "CBRE Merck ":
            row[5] = "CBRE Merck"
        
        # Normalize Google
        if account in ["Google ", "Google JLL"]:
            row[5] = "Google"
        
        # Normalize Nestle/GE
        if account in ["Nestle/GE Health", "Nestle and GE", "GE Healthcare / Nestle "]:
            row[5] = "Nestle/GE Healthcare"
        
        # Normalize LinkedIn/Uber
        if account in ["LinkedIn Uber", "LinkedIn and Uber ", "LinkedIn & Uber"]:
            row[5] = "LinkedIn/Uber"
        
        # Normalize Microsoft
        if account in ["MSFT PS", "Microsoft "]:
            row[5] = "Microsoft"
        
        # Normalize Nike
        if account in ["Nike", "Nike Distribution "]:
            row[5] = "Nike Distribution"
        
        # Normalize Lonza
        if account in ["Lonza ", "Lonza"]:
            row[5] = "Lonza"
        
        # Normalize Nvidia
        if account in ["Nvidia ", "Nvidia"]:
            row[5] = "Nvidia"
        
        # Normalize Deutsche Bank
        if account == "Deutsche Bank ":
            row[5] = "Deutsche Bank"
        
        # Normalize Isaac's accounts
        if account in ["Bayer, J&J, Kenvue, Millipore Sigma", "Bayer, Millipore, Johnson & Johnson, Bluerock, Kenvue", "Bayer / J&J / Kenvue / Millipore"]:
            row[5] = "Bayer/J&J/Kenvue/Millipore Sigma"
        
        # Normalize Patrick's accounts
        if account in ["Cardinal, IQVIA, McKesson", "McKesson, IQVIA, Cardinal Health", "McKesson, CAH, IQVIA"]:
            row[5] = "Cardinal/IQVIA/McKesson"
        
        # Normalize Aaron's accounts
        if account == "Mars, 3M":
            row[5] = "Mars/3M"
        
        # Normalize Lockheed
        if account == "Lockheed":
            row[5] = "Lockheed Martin"

# Write cleaned CSV
with open('data/performance_reviews.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("✅ CSV cleaned and saved to data/performance_reviews.csv")
print(f"   - {len(rows) - 1} data rows processed")

