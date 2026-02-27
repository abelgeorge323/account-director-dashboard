"""
Verify all metrics used in EOY_Quick_Read_Financial_Report.html against source CSVs.
"""
import csv

def parse_val(s):
    """Parse numeric value from CSV cell."""
    if not s or s.strip() in ('', '-', 'N/A'):
        return None
    s = str(s).strip().replace(',', '').replace('(', '-').replace(')', '')
    try:
        return float(s)
    except ValueError:
        return None

def load_csv(path):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        r = csv.reader(f)
        headers = next(r)
        for row in r:
            if len(row) >= 15:
                rows.append(row)
    return headers, rows

def get_kpi(rows, kpi_name, col_idx=15):  # Dec-25 is col 15 (0-indexed)
    for row in rows:
        if row[2] and kpi_name in row[2]:
            return parse_val(row[col_idx]) if col_idx < len(row) else None
    return None

def main():
    print("=" * 60)
    print("EOY QUICK READ - METRIC VERIFICATION")
    print("=" * 60)

    # Colleen Doles - Wells Fargo
    print("\n--- COLLEEN DOLES (Wells Fargo) ---")
    _, wf = load_csv("data/ad_csvs/colleen-doles.csv")
    wf_rev = get_kpi(wf, "Revenue")
    wf_growth = get_kpi(wf, "Growth")
    wf_gap = get_kpi(wf, "Gap")
    wf_red_dollars = get_kpi(wf, "Red Sites ($)")
    wf_red_n = get_kpi(wf, "Red Sites (#)")
    wf_hc = get_kpi(wf, "Headcount")
    wf_turn = get_kpi(wf, "Turnover")
    wf_csat = get_kpi(wf, "CSAT")

    print(f"  Revenue (Dec 25):   {wf_rev} K -> ${wf_rev/1000:.2f}M" if wf_rev else "  Revenue: N/A")
    print(f"  YoY Growth:         {wf_growth}%" if wf_growth is not None else "  Growth: N/A")
    print(f"  Gap ($):            {wf_gap} K -> (${abs(wf_gap)}K)" if wf_gap is not None else "  Gap: N/A")
    print(f"  Red Sites ($):      {wf_red_dollars} K -> ${abs(wf_red_dollars)}K" if wf_red_dollars is not None else "  Red Sites $: N/A")
    print(f"  Red Sites (#):      {wf_red_n}" if wf_red_n is not None else "  Red Sites #: N/A")
    print(f"  Headcount:          {wf_hc}" if wf_hc is not None else "  Headcount: N/A")
    print(f"  Turnover:           {wf_turn}%" if wf_turn is not None else "  Turnover: N/A")
    print(f"  CSAT:              {wf_csat}" if wf_csat is not None else "  CSAT: N/A")

    # Joshua Grady - Gilead + Avid
    print("\n--- JOSHUA GRADY (Gilead + Avid) ---")
    _, jg = load_csv("data/ad_csvs/joshua-grady.csv")

    gilead_rows = [r for r in jg if r[0] == "Gilead Sciences"]
    avid_rows = [r for r in jg if r[0] == "Avid Biodevices"]

    for name, rows in [("Gilead", gilead_rows), ("Avid", avid_rows)]:
        if not rows:
            continue
        rev = get_kpi(rows, "Revenue")
        growth = get_kpi(rows, "Growth")
        gap = get_kpi(rows, "Gap")
        hc = get_kpi(rows, "Headcount")
        turn = get_kpi(rows, "Turnover")
        csat = get_kpi(rows, "CSAT")
        print(f"  {name}: Rev={rev}K, Growth={growth}%, Gap={gap}K, HC={hc}, Turn={turn}%, CSAT={csat}")

    g_rev = get_kpi(gilead_rows, "Revenue")
    a_rev = get_kpi(avid_rows, "Revenue")
    total = (g_rev or 0) + (a_rev or 0)
    print(f"  Combined Revenue:   {total} K -> ${total/1000:.2f}M")

    g_hc = get_kpi(gilead_rows, "Headcount")
    a_hc = get_kpi(avid_rows, "Headcount")
    print(f"  Combined Headcount: {(g_hc or 0) + (a_hc or 0)}")

    # Quarterly averages
    print("\n--- QUARTERLY AVERAGES ---")
    def q_avg(rows, kpi, cols):  # cols = list of 0-indexed col numbers
        vals = []
        for row in rows:
            if row[2] and kpi in row[2]:
                for c in cols:
                    v = parse_val(row[c]) if c < len(row) else None
                    if v is not None:
                        vals.append(v)
                break
        return sum(vals) / len(vals) if vals else None

    months = {'Q1': [4,5,6], 'Q2': [7,8,9], 'Q3': [10,11,12], 'Q4': [13,14,15]}  # Jan-Dec cols
    for q, cols in months.items():
        wf_q = q_avg(wf, "Revenue", cols)
        g_q = q_avg(gilead_rows, "Revenue", cols)
        a_q = q_avg(avid_rows, "Revenue", cols)
        j_q = (g_q or 0) + (a_q or 0)
        print(f"  Colleen {q}: ${wf_q:.0f}K" if wf_q else f"  Colleen {q}: N/A")
        print(f"  Joshua {q}: ${j_q:.0f}K (Gilead ${g_q:.0f}K + Avid ${a_q:.0f}K)" if (g_q or a_q) else f"  Joshua {q}: N/A")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
