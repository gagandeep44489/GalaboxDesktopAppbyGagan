"""
High Cart Value Customer Maximization Strategy - Desktop App in Python

Purpose:
Identify customers whose cart value exceeds a configurable threshold,
assign a "High Cart Value" tag, and generate premium engagement actions.
"""

import tkinter as tk
from tkinter import ttk, messagebox


def parse_orders(raw_text: str):
    """
    Expected format per line:
    customer_id, customer_name, cart_value
    """
    orders = []
    errors = []

    for line_no, line in enumerate(raw_text.strip().splitlines(), start=1):
        if not line.strip():
            continue

        parts = [item.strip() for item in line.split(",")]
        if len(parts) != 3:
            errors.append(f"Line {line_no}: expected 3 comma-separated fields")
            continue

        customer_id, customer_name, cart_value_text = parts

        if not customer_id or not customer_name:
            errors.append(f"Line {line_no}: customer_id and customer_name are required")
            continue

        try:
            cart_value = float(cart_value_text)
            if cart_value < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Line {line_no}: cart_value must be a non-negative number")
            continue

        orders.append(
            {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "cart_value": cart_value,
            }
        )

    return orders, errors


def recommendation_for(cart_value: float, threshold: float):
    ratio = cart_value / threshold if threshold > 0 else 0
    if ratio >= 2.0:
        return "VIP thank-you + priority shipping + loyalty bonus"
    if ratio >= 1.3:
        return "Thank-you note + premium cross-sell offer"
    return "Thank-you note + early-access campaign invite"


def run_strategy():
    raw_data = orders_input.get("1.0", tk.END)
    orders, errors = parse_orders(raw_data)

    output_box.delete("1.0", tk.END)
    results_table.delete(*results_table.get_children())

    if errors:
        messagebox.showwarning(
            "Input warnings",
            "Some lines were skipped due to formatting issues:\n\n"
            + "\n".join(errors[:12])
            + ("\n..." if len(errors) > 12 else ""),
        )

    if not orders:
        messagebox.showerror("No valid rows", "Please provide at least one valid customer row.")
        return

    try:
        threshold = float(threshold_var.get().strip())
        if threshold <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid threshold", "Threshold must be a number greater than 0.")
        return

    total_customers = len(orders)
    total_revenue = sum(order["cart_value"] for order in orders)
    average_cart = total_revenue / total_customers

    high_value_orders = [order for order in orders if order["cart_value"] >= threshold]
    high_value_revenue = sum(order["cart_value"] for order in high_value_orders)
    high_value_share = (high_value_revenue / total_revenue * 100) if total_revenue else 0.0

    summary_lines = [
        "High Cart Value Customer Maximization Strategy",
        "=" * 46,
        "Operational workflow:",
        "1) Cart value calculation",
        "2) Threshold exceeded",
        "3) Tag assignment",
        "4) Premium engagement",
        "5) Future high-value targeting",
        "",
        f"Configured high-cart threshold: ${threshold:,.2f}",
        f"Average transaction size: ${average_cart:,.2f}",
        f"Total customers analyzed: {total_customers}",
        f"High Cart Value tagged customers: {len(high_value_orders)}",
        f"Revenue from tagged customers: ${high_value_revenue:,.2f}",
        f"Revenue concentration from tagged group: {high_value_share:.1f}%",
    ]

    if threshold < average_cart:
        summary_lines.append(
            "\nNote: Your threshold is below average cart value; consider raising it for stronger premium targeting."
        )

    output_box.insert(tk.END, "\n".join(summary_lines))

    for order in sorted(orders, key=lambda x: x["cart_value"], reverse=True):
        is_high = order["cart_value"] >= threshold
        tag = "High Cart Value" if is_high else "Standard"
        engagement = recommendation_for(order["cart_value"], threshold) if is_high else "Standard nurture sequence"
        results_table.insert(
            "",
            tk.END,
            values=(
                order["customer_id"],
                order["customer_name"],
                f"${order['cart_value']:,.2f}",
                tag,
                engagement,
            ),
        )


def load_sample_data():
    sample = """C101,Avery Thomas,1299.00
C102,Riya Patel,245.00
C103,Noah Chen,780.00
C104,Mia Johnson,1899.00
C105,Ethan Green,315.00
C106,Sophia Lewis,1125.00
"""
    orders_input.delete("1.0", tk.END)
    orders_input.insert(tk.END, sample)


root = tk.Tk()
root.title("High Cart Value Customer Maximization Strategy")
root.geometry("1100x760")

style = ttk.Style(root)
style.theme_use("clam")

main = ttk.Frame(root, padding=12)
main.pack(fill=tk.BOTH, expand=True)

header = ttk.Label(
    main,
    text="High Cart Value Customer Maximization Strategy",
    font=("Segoe UI", 16, "bold"),
)
header.pack(anchor="w", pady=(0, 6))

subtitle = ttk.Label(
    main,
    text=(
        'Assign the "High Cart Value" tag when cart value exceeds threshold, '
        "then trigger premium engagement actions."
    ),
)
subtitle.pack(anchor="w", pady=(0, 8))

instructions = ttk.Label(
    main,
    text="Enter one row per customer: customer_id, customer_name, cart_value",
)
instructions.pack(anchor="w")

orders_input = tk.Text(main, height=11, width=130)
orders_input.pack(fill=tk.X, pady=8)

controls = ttk.Frame(main)
controls.pack(fill=tk.X, pady=(0, 8))

threshold_label = ttk.Label(controls, text="High-cart threshold ($):")
threshold_label.pack(side=tk.LEFT)

threshold_var = tk.StringVar(value="1000")
threshold_entry = ttk.Entry(controls, textvariable=threshold_var, width=12)
threshold_entry.pack(side=tk.LEFT, padx=(6, 14))

ttk.Button(controls, text="Load Sample Data", command=load_sample_data).pack(side=tk.LEFT)
ttk.Button(controls, text="Run Strategy", command=run_strategy).pack(side=tk.LEFT, padx=8)

summary_label = ttk.Label(main, text="Strategy Summary")
summary_label.pack(anchor="w")

output_box = tk.Text(main, height=14, width=130)
output_box.pack(fill=tk.BOTH, expand=False, pady=6)

results_label = ttk.Label(main, text="Customer Tagging & Premium Engagement Actions")
results_label.pack(anchor="w", pady=(6, 2))

columns = ("customer_id", "name", "cart", "tag", "engagement")
results_table = ttk.Treeview(main, columns=columns, show="headings", height=11)

for col, width in [
    ("customer_id", 120),
    ("name", 180),
    ("cart", 130),
    ("tag", 150),
    ("engagement", 470),
]:
    results_table.heading(col, text=col.replace("_", " ").title())
    results_table.column(col, width=width, anchor=tk.CENTER)

results_table.pack(fill=tk.BOTH, expand=True)

load_sample_data()
run_strategy()

root.mainloop()