# Webinar Attendee Conversion Funnel - Desktop App in Python
# Purpose:
# Help marketing/sales teams segment webinar contacts, assign tags,
# and prioritize 24-72 hour follow-up offers to improve paid conversions.

import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter


def parse_contacts(raw_text: str):
    """
    Expected CSV per line:
    contact_name, email, registered_yes_no, attendance(live/replay/no), engagement_0_100, hours_since_webinar, consultation_interest_yes_no
    """
    contacts = []
    errors = []

    for line_no, line in enumerate(raw_text.strip().splitlines(), start=1):
        if not line.strip():
            continue

        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 7:
            errors.append(f"Line {line_no}: expected 7 comma-separated values")
            continue

        name, email, registered, attendance, engagement, hours_since, consult_interest = parts

        if not name or not email or '@' not in email:
            errors.append(f"Line {line_no}: invalid name/email")
            continue

        registered = registered.lower()
        if registered not in {"yes", "no"}:
            errors.append(f"Line {line_no}: registered must be yes/no")
            continue

        attendance = attendance.lower()
        if attendance not in {"live", "replay", "no"}:
            errors.append(f"Line {line_no}: attendance must be live/replay/no")
            continue

        try:
            engagement = float(engagement)
            if not (0 <= engagement <= 100):
                raise ValueError
        except ValueError:
            errors.append(f"Line {line_no}: engagement must be 0-100")
            continue

        try:
            hours_since = float(hours_since)
            if hours_since < 0:
                raise ValueError
        except ValueError:
            errors.append(f"Line {line_no}: hours_since_webinar must be >= 0")
            continue

        consult_interest = consult_interest.lower()
        if consult_interest not in {"yes", "no"}:
            errors.append(f"Line {line_no}: consultation_interest must be yes/no")
            continue

        contacts.append(
            {
                "name": name,
                "email": email,
                "registered": registered == "yes",
                "attendance": attendance,
                "engagement": engagement,
                "hours_since": hours_since,
                "consult_interest": consult_interest == "yes",
            }
        )

    return contacts, errors


def assign_tag(contact):
    if not contact["registered"]:
        return "No Webinar Tag"
    if contact["attendance"] == "live":
        return "Webinar Attendee - Live"
    if contact["attendance"] == "replay":
        return "Webinar Attendee - Replay"
    return "Webinar Registered - No Show"


def estimate_conversion_probability(contact):
    if not contact["registered"]:
        return 0.02

    base = 0.08
    if contact["attendance"] == "live":
        base += 0.14
    elif contact["attendance"] == "replay":
        base += 0.08

    base += (contact["engagement"] / 100) * 0.12

    if contact["consult_interest"]:
        base += 0.1

    if 24 <= contact["hours_since"] <= 72:
        base += 0.05
    elif contact["hours_since"] > 72:
        base -= 0.03

    return max(0.01, min(base, 0.9))


def follow_up_action(contact):
    h = contact["hours_since"]
    if not contact["registered"]:
        return "Nurture list only"
    if h < 24:
        return "Send slides + replay + FAQ"
    if h <= 72:
        return "Send limited-time consultation offer"
    if h <= 96:
        return "Send offer expiration reminder"
    return "Move to long-term nurture"


def analyze_funnel():
    raw = input_text.get("1.0", tk.END)
    contacts, errors = parse_contacts(raw)

    output_text.delete("1.0", tk.END)
    result_tree.delete(*result_tree.get_children())

    if errors:
        messagebox.showwarning(
            "Input Warnings",
            "Some rows were skipped due to errors:\n\n" + "\n".join(errors[:12])
            + ("\n..." if len(errors) > 12 else ""),
        )

    if not contacts:
        messagebox.showerror("No Valid Data", "Please provide at least one valid contact row.")
        return

    stage_counts = Counter(
        {
            "registration_confirmed": sum(1 for c in contacts if c["registered"]),
            "attendance_verified": sum(1 for c in contacts if c["attendance"] in {"live", "replay"}),
            "tag_assigned": sum(1 for c in contacts if assign_tag(c).startswith("Webinar Attendee")),
            "follow_up_window_24_72h": sum(1 for c in contacts if 24 <= c["hours_since"] <= 72),
            "offer_expiration_reminder": sum(1 for c in contacts if 72 < c["hours_since"] <= 96),
        }
    )

    conversions_expected = 0.0
    segment_counter = Counter()

    for c in sorted(contacts, key=lambda x: x["engagement"], reverse=True):
        tag = assign_tag(c)
        probability = estimate_conversion_probability(c)
        action = follow_up_action(c)
        conversions_expected += probability

        segment = "Live Attendee" if c["attendance"] == "live" else (
            "Replay Viewer" if c["attendance"] == "replay" else "No Show"
        )
        segment_counter[segment] += 1

        result_tree.insert(
            "",
            tk.END,
            values=(
                c["name"],
                tag,
                f"{c['engagement']:.0f}",
                action,
                f"{probability * 100:.1f}%",
            ),
        )

    total_contacts = len(contacts)
    expected_rate = (conversions_expected / total_contacts) * 100

    summary = [
        "Webinar Attendee Conversion Funnel",
        "=" * 34,
        f"Total Contacts: {total_contacts}",
        f"Registration Confirmed: {stage_counts['registration_confirmed']}",
        f"Attendance Verified: {stage_counts['attendance_verified']}",
        f"Webinar Attendee Tag Assigned: {stage_counts['tag_assigned']}",
        f"In Follow-up Window (24-72h): {stage_counts['follow_up_window_24_72h']}",
        f"Offer Expiration Reminder Pool: {stage_counts['offer_expiration_reminder']}",
        "",
        "Attendee Segments:",
    ]

    for seg, count in segment_counter.items():
        summary.append(f"  - {seg}: {count}")

    summary += [
        "",
        f"Expected Conversions (model estimate): {conversions_expected:.2f}",
        f"Estimated Funnel Conversion Rate: {expected_rate:.1f}%",
        "",
        "Recommended Automation Sequence:",
        "  1) Registration confirmed",
        "  2) Attendance verified (live vs replay)",
        "  3) Tag assignment",
        "  4) Follow-up sequence in 24-72 hours",
        "  5) Offer expiration reminder",
    ]

    output_text.insert(tk.END, "\n".join(summary))


def load_sample_data():
    sample = """Ava Brooks,ava@logiflow.ai,yes,live,92,18,yes
Mason Lee,mason@fleetedge.com,yes,live,76,36,yes
Sophia Diaz,sophia@routevision.io,yes,replay,68,54,no
Noah Patel,noah@cargozen.com,yes,replay,58,80,yes
Ethan Ross,ethan@supplypilot.com,yes,no,40,30,no
Liam Chen,liam@urbanfreight.co,no,no,25,10,no
Emma Stone,emma@tracelogix.ai,yes,live,88,74,yes
Olivia Green,olivia@shipmind.io,yes,replay,73,26,yes
"""
    input_text.delete("1.0", tk.END)
    input_text.insert(tk.END, sample)


root = tk.Tk()
root.title("Webinar Attendee Conversion Funnel")
root.geometry("1080x760")

style = ttk.Style(root)
style.theme_use("clam")

main = ttk.Frame(root, padding=12)
main.pack(fill=tk.BOTH, expand=True)

header = ttk.Label(main, text="Webinar Attendee Conversion Funnel", font=("Segoe UI", 16, "bold"))
header.pack(anchor="w", pady=(0, 8))

instructions = ttk.Label(
    main,
    text=(
        "Enter one contact per line: "
        "name, email, registered_yes_no, attendance(live/replay/no), "
        "engagement_0_100, hours_since_webinar, consultation_interest_yes_no"
    ),
)
instructions.pack(anchor="w")

input_text = tk.Text(main, height=11, width=130)
input_text.pack(fill=tk.X, pady=8)

buttons = ttk.Frame(main)
buttons.pack(fill=tk.X, pady=(0, 8))

ttk.Button(buttons, text="Load Sample Data", command=load_sample_data).pack(side=tk.LEFT)
ttk.Button(buttons, text="Analyze Funnel", command=analyze_funnel).pack(side=tk.LEFT, padx=8)

summary_label = ttk.Label(main, text="Funnel Summary")
summary_label.pack(anchor="w")

output_text = tk.Text(main, height=14, width=130)
output_text.pack(fill=tk.BOTH, expand=False, pady=6)

columns = ("name", "tag", "engagement", "next_action", "conversion_probability")
result_tree = ttk.Treeview(main, columns=columns, show="headings", height=12)
for col, width in [
    ("name", 170),
    ("tag", 260),
    ("engagement", 100),
    ("next_action", 280),
    ("conversion_probability", 170),
]:
    result_tree.heading(col, text=col.replace("_", " ").title())
    result_tree.column(col, width=width, anchor=tk.CENTER)

result_tree.pack(fill=tk.BOTH, expand=True)

load_sample_data()
root.mainloop()