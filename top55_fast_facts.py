"""
Fast facts: Top 55 accounts - response count and IFM distribution comparison.
- Top 55: from month_end_by_ifm (CBRE, Direct, JLL, C&W, Amentum, EMCOR) by revenue
- Responses: accounts with SCR notes from scorecard visibility report (RAW_ENTRIES)
"""
import pandas as pd
from pathlib import Path
from collections import defaultdict

def parse_revenue(val):
    if pd.isna(val) or val == "" or str(val).strip() in ("-", " -   "):
        return 0
    s = str(val).strip().replace(",", "").replace("(", "-").replace(")", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0

def main():
    base = Path("data/month_end_by_ifm")
    ifms = ["CBRE", "Direct", "JLL", "C&W", "Amentum", "EMCOR"]
    file_map = {"EMCOR": "Emcor"}  # filename uses Emcor

    # Build account -> total revenue, account -> set of IFMs
    account_rev = defaultdict(float)
    account_ifms = defaultdict(set)

    for ifm in ifms:
        fname = file_map.get(ifm, ifm)
        path = base / f"{fname}_January_2026.csv"
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                acc = str(row.get("Account", "")).strip()
                if not acc:
                    continue
                rv = parse_revenue(row.get("Sum of RV", 0))
                account_rev[acc] += rv
                account_ifms[acc].add(ifm)
        except Exception as e:
            print(f"  Skip {path.name}: {e}")

    # Top 55 by revenue
    sorted_accounts = sorted(account_rev.items(), key=lambda x: x[1], reverse=True)
    top55 = [a for a, _ in sorted_accounts[:55]]

    # IFM distribution of top 55 (count account-IFM pairs; accounts can span multiple IFMs)
    top55_ifm = defaultdict(int)
    for acc in top55:
        for ifm in account_ifms.get(acc, set()):
            top55_ifm[ifm] += 1

    # Use RAW_ENTRIES from scorecard for response count and IFM dist
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from generate_scorecard_visibility_report import RAW_ENTRIES

    num_responses = len(RAW_ENTRIES)  # 30 accounts with SCR notes
    response_ifm = defaultdict(int)
    for _, _, ifms, _, _ in RAW_ENTRIES:
        for ifm in ifms:
            response_ifm[ifm] += 1

    # Output
    print("=" * 60)
    print("TOP 55 ACCOUNTS – FAST FACTS")
    print("=" * 60)
    print()
    print("RESPONSE COUNT")
    print("-" * 40)
    print(f"  Top 55 accounts (universe):      55")
    print(f"  Responses received (SCR notes):  {num_responses}")
    print(f"  Response rate:                   {num_responses/55*100:.1f}%")
    print()
    print("IFM DISTRIBUTION – Top 55 Accounts")
    print("-" * 40)
    total55 = sum(top55_ifm.values())
    for ifm in ["CBRE", "Direct", "JLL", "C&W", "Amentum", "EMCOR"]:
        c = top55_ifm.get(ifm, 0)
        pct = c / total55 * 100 if total55 else 0
        print(f"  {ifm:<10} {c:>3}  ({pct:>5.1f}%)")
    print(f"  {'Total':<10} {total55:>3}")
    print()
    print("IFM DISTRIBUTION – Our Responses")
    print("-" * 40)
    total_resp = sum(response_ifm.values())
    for ifm in ["CBRE", "Direct", "JLL", "C&W", "Amentum", "EMCOR"]:
        c = response_ifm.get(ifm, 0)
        pct = c / total_resp * 100 if total_resp else 0
        print(f"  {ifm:<10} {c:>3}  ({pct:>5.1f}%)")
    print(f"  {'Total':<10} {total_resp:>3}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
