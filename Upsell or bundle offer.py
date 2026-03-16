import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


def parse_bool(value: str) -> bool:
    norm = value.strip().lower()
    if norm in {"yes", "y", "true", "1"}:
        return True
    if norm in {"no", "n", "false", "0"}:
        return False
    raise ValueError("renewal flag must be yes/no")


def parse_purchase_rows(raw_text: str):
    """
    Expected CSV rows:
    customer_id,purchase_date(YYYY-MM-DD),amount,renewal_yes_no
    """
    rows = []
    errors = []

    for line_no, line in enumerate(raw_text.strip().splitlines(), start=1):
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            errors.append(f"Line {line_no}: expected 4 comma-separated values")
            continue

        customer_id, date_text, amount_text, renewal_text = parts
        if not customer_id:
            errors.append(f"Line {line_no}: customer_id cannot be empty")
            continue

        try:
            purchase_date = datetime.strptime(date_text, DATE_FORMAT).date()
        except ValueError:
            errors.append(f"Line {line_no}: invalid date '{date_text}' (use YYYY-MM-DD)")
            continue

        try:
            amount = float(amount_text)
            if amount < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Line {line_no}: invalid amount '{amount_text}'")
            continue

        try:
            renewal = parse_bool(renewal_text)
        except ValueError:
            errors.append(f"Line {line_no}: renewal flag must be yes/no")
            continue

        rows.append(
            {
                "customer": customer_id,
                "date": purchase_date,
                "amount": amount,
                "renewal": renewal,
            }
        )

    return rows, errors


def within_window(sorted_dates, days):
    if len(sorted_dates) < 2:
        return False

    left = 0
    for right in range(len(sorted_dates)):
        while left < right and (sorted_dates[right] - sorted_dates[left]).days > days:
            left += 1
        if right - left + 1 >= 2:
            return True
    return False


def classify_tier(purchase_count: int, total_spend: float):
    if purchase_count >= 8 or total_spend >= 3000:
        return "Elite"
    if purchase_count >= 4 or total_spend >= 1200:
        return "Level 2"
    return "Level 1"


def campaign_for_tier(tier: str):
    return {
        "Level 1": "Loyalty welcome + curated upsell bundle",
        "Level 2": "Exclusive preview access + bundle certification offer",
        "Elite": "Early access launch + premium concierge bundle",
    }[tier]


def analyze_repeat_buyers(rows, min_purchases: int, window_days: int):
    customers = defaultdict(lambda: {"dates": [], "total": 0.0, "renewals": 0, "events": 0})

    for row in rows:
        c = customers[row["customer"]]
        c["dates"].append(row["date"])
        c["total"] += row["amount"]
        c["events"] += 1
        if row["renewal"]:
            c["renewals"] += 1

    tagged = []
    untagged = []

    for customer_id, agg in customers.items():
        dates = sorted(agg["dates"])
        purchases_in_window = within_window(dates, window_days)
        renewal_hit = agg["renewals"] > 0
        meets_count = agg["events"] >= min_purchases

        qualifies = (meets_count and purchases_in_window) or renewal_hit
        if qualifies:
            tier = classify_tier(agg["events"], agg["total"])
            tagged.append(
                {
                    "customer": customer_id,
                    "purchases": agg["events"],
                    "spend": agg["total"],
                    "renewals": agg["renewals"],
                    "tier": tier,
                    "campaign": campaign_for_tier(tier),
                }
            )
        else:
            untagged.append(customer_id)

    tagged.sort(key=lambda x: (x["tier"], x["spend"]), reverse=True)

    total_revenue = sum(r["amount"] for r in rows)
    repeat_revenue = sum(c["spend"] for c in tagged)
    repeat_rate = (len(tagged) / len(customers) * 100) if customers else 0
    revenue_stability = (repeat_revenue / total_revenue * 100) if total_revenue else 0
    projected_profit_lift = revenue_stability * 0.10

    metrics = {
        "customers": len(customers),
        "tagged": len(tagged),
        "repeat_rate": repeat_rate,
        "total_revenue": total_revenue,
        "repeat_revenue": repeat_revenue,
        "revenue_stability": revenue_stability,
        "profit_lift": projected_profit_lift,
    }

    return tagged, untagged, metrics


def load_sample_data():
    sample = """CUST-1001,2026-01-03,129.0,no
CUST-1001,2026-01-22,159.0,no
CUST-1001,2026-02-10,249.0,yes
CUST-1002,2026-01-04,79.0,no
CUST-1002,2026-05-14,99.0,no
CUST-1003,2026-01-08,299.0,no
CUST-1003,2026-01-16,399.0,no
CUST-1003,2026-02-01,699.0,no
CUST-1004,2026-03-01,89.0,yes
CUST-1005,2026-01-12,1200.0,no
CUST-1005,2026-02-17,1400.0,no
CUST-1005,2026-03-09,900.0,yes
"""
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, sample)


def run_model():
    raw = input_text.get("1.0", tk.END)
    rows, errors = parse_purchase_rows(raw)

    summary_text.delete("1.0", tk.END)
    result_tree.delete(*result_tree.get_children())

    if errors:
        messagebox.showwarning(
            "Input Warnings",
            "Some lines were skipped:\n\n" + "\n".join(errors[:10]) + ("\n..." if len(errors) > 10 else ""),
        )

    if not rows:
        messagebox.showerror("No Data", "Please provide at least one valid purchase row.")
        return

    try:
        min_purchases = int(min_purchases_var.get())
        window_days = int(window_days_var.get())
        if min_purchases < 2 or window_days < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Thresholds", "Use integer thresholds: min purchases >= 2 and window days >= 1.")
        return

    tagged, untagged, metrics = analyze_repeat_buyers(rows, min_purchases, window_days)

    summary_lines = [
        "Repeat Buyer Revenue Stabilization Model",
        "=" * 42,
        "Workflow: Purchase Event -> Threshold -> Tag -> Exclusive Campaign -> Upsell",
        "",
        f"Total Customers: {metrics['customers']}",
        f"Tagged Repeat Buyers: {metrics['tagged']} ({metrics['repeat_rate']:.1f}%)",
        f"Total Revenue: ${metrics['total_revenue']:.2f}",
        f"Repeat Buyer Revenue: ${metrics['repeat_revenue']:.2f}",
        f"Revenue Stability Index: {metrics['revenue_stability']:.1f}%",
        f"Projected Profit Margin Lift (10% repeat gain model): {metrics['profit_lift']:.2f}%",
        "",
        f"Not Yet Tagged: {', '.join(untagged) if untagged else 'None'}",
    ]
    summary_text.insert(tk.END, "\n".join(summary_lines))

    for c in tagged:
        result_tree.insert(
            "",
            tk.END,
            values=(
                c["customer"],
                c["purchases"],
                f"${c['spend']:.2f}",
                c["renewals"],
                c["tier"],
                c["campaign"],
            ),
        )


root = tk.Tk()
root.title("Repeat Buyer Revenue Stabilization Model")
root.geometry("1120x760")

style = ttk.Style(root)
style.theme_use("clam")

main = ttk.Frame(root, padding=12)
main.pack(fill=tk.BOTH, expand=True)

header = ttk.Label(main, text="Repeat Buyer Revenue Stabilization Model", font=("Segoe UI", 16, "bold"))
header.pack(anchor="w", pady=(0, 8))

instructions = ttk.Label(
    main,
    text="Enter: customer_id,purchase_date(YYYY-MM-DD),amount,renewal_yes_no",
)
instructions.pack(anchor="w")

input_text = tk.Text(main, height=11)
input_text.pack(fill=tk.X, pady=8)

controls = ttk.Frame(main)
controls.pack(fill=tk.X, pady=(0, 8))

min_purchases_var = tk.StringVar(value="2")
window_days_var = tk.StringVar(value="90")


ttk.Label(controls, text="Minimum Purchases:").pack(side=tk.LEFT)
ttk.Entry(controls, textvariable=min_purchases_var, width=6).pack(side=tk.LEFT, padx=(4, 12))

ttk.Label(controls, text="Window (days):").pack(side=tk.LEFT)
ttk.Entry(controls, textvariable=window_days_var, width=6).pack(side=tk.LEFT, padx=(4, 12))

ttk.Button(controls, text="Load Sample", command=load_sample_data).pack(side=tk.LEFT)
ttk.Button(controls, text="Run Model", command=run_model).pack(side=tk.LEFT, padx=8)

summary_label = ttk.Label(main, text="Revenue Summary")
summary_label.pack(anchor="w")

summary_text = tk.Text(main, height=12)
summary_text.pack(fill=tk.X, pady=6)

result_label = ttk.Label(main, text="Tagged Repeat Buyers")
result_label.pack(anchor="w", pady=(6, 2))

columns = ("customer", "purchases", "spend", "renewals", "tier", "campaign")
result_tree = ttk.Treeview(main, columns=columns, show="headings", height=12)
for col, width in [
    ("customer", 130),
    ("purchases", 90),
    ("spend", 110),
    ("renewals", 90),
    ("tier", 90),
    ("campaign", 480),
]:
    result_tree.heading(col, text=col.title())
    result_tree.column(col, width=width, anchor=tk.W)

result_tree.pack(fill=tk.BOTH, expand=True)

load_sample_data()
root.mainloop()