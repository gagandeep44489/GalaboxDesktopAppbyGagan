import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Contact:
    name: str
    segment: str
    average_order_value: float
    likely_to_convert: bool
    tagged: bool = False


@dataclass
class CampaignStepResult:
    step: str
    impressions: int
    conversions: int
    revenue: float


class FestivalOfferApp:
    SEGMENT_LIFT = {
        "VIP": 1.35,
        "Repeat": 1.20,
        "Price-Sensitive": 1.45,
        "Inactive": 1.10,
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Festival Offer Campaign Revenue Acceleration Model")
        self.root.geometry("1100x720")

        self.contacts: List[Contact] = []
        self.results: List[CampaignStepResult] = []

        self.discount_map = {
            "VIP": tk.DoubleVar(value=10.0),
            "Repeat": tk.DoubleVar(value=15.0),
            "Price-Sensitive": tk.DoubleVar(value=20.0),
            "Inactive": tk.DoubleVar(value=18.0),
        }

        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(
            self.root,
            text="Festival Offer Campaign - Desktop Simulator",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(pady=(12, 5))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        setup_tab = ttk.Frame(notebook)
        execution_tab = ttk.Frame(notebook)
        analysis_tab = ttk.Frame(notebook)

        notebook.add(setup_tab, text="1) Segment & Tag")
        notebook.add(execution_tab, text="2) Promotion Flow")
        notebook.add(analysis_tab, text="3) Revenue Analysis")

        self._build_setup_tab(setup_tab)
        self._build_execution_tab(execution_tab)
        self._build_analysis_tab(analysis_tab)

    def _build_setup_tab(self, parent):
        form = ttk.LabelFrame(parent, text="Add Contact")
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=22).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text="Segment").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.segment_var = tk.StringVar(value="Price-Sensitive")
        segment_combo = ttk.Combobox(
            form,
            textvariable=self.segment_var,
            values=["VIP", "Repeat", "Price-Sensitive", "Inactive"],
            state="readonly",
            width=18,
        )
        segment_combo.grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(form, text="Avg Order Value ($)").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.aov_var = tk.StringVar(value="99")
        ttk.Entry(form, textvariable=self.aov_var, width=12).grid(row=0, column=5, padx=6, pady=6)

        self.likely_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Likely to respond", variable=self.likely_var).grid(
            row=1, column=0, columnspan=2, padx=6, pady=6, sticky="w"
        )

        ttk.Button(form, text="Add Contact", command=self.add_contact).grid(row=1, column=5, padx=6, pady=6, sticky="e")

        discount_box = ttk.LabelFrame(parent, text="Segment-Based Discount Differentiation")
        discount_box.pack(fill="x", padx=8, pady=8)

        for i, segment in enumerate(["VIP", "Repeat", "Price-Sensitive", "Inactive"]):
            ttk.Label(discount_box, text=f"{segment} discount %").grid(row=0, column=i * 2, padx=6, pady=6, sticky="w")
            ttk.Entry(discount_box, textvariable=self.discount_map[segment], width=8).grid(
                row=0, column=i * 2 + 1, padx=6, pady=6
            )

        table_frame = ttk.LabelFrame(parent, text="Contacts")
        table_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.contact_table = ttk.Treeview(
            table_frame,
            columns=("name", "segment", "aov", "likely", "tagged"),
            show="headings",
            height=14,
        )
        for col, text, width in [
            ("name", "Name", 220),
            ("segment", "Segment", 150),
            ("aov", "Avg Order Value", 130),
            ("likely", "Likely", 90),
            ("tagged", "Festival Tagged", 130),
        ]:
            self.contact_table.heading(col, text=text)
            self.contact_table.column(col, width=width, anchor="center")

        self.contact_table.pack(fill="both", expand=True, padx=8, pady=8)

        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", padx=8, pady=8)

        ttk.Button(action_frame, text="Auto-Tag Target Segments", command=self.auto_tag).pack(side="left", padx=6)
        ttk.Button(action_frame, text="Load Demo Dataset", command=self.load_demo).pack(side="left", padx=6)
        ttk.Button(action_frame, text="Clear", command=self.clear_all).pack(side="left", padx=6)

    def _build_execution_tab(self, parent):
        box = ttk.LabelFrame(parent, text="Campaign Flow")
        box.pack(fill="x", padx=8, pady=8)

        self.step_vars = {
            "Countdown Message": tk.BooleanVar(value=True),
            "Early Access Offer": tk.BooleanVar(value=True),
            "Last-Day Reminder": tk.BooleanVar(value=True),
        }

        for idx, (step, var) in enumerate(self.step_vars.items()):
            ttk.Checkbutton(box, text=step, variable=var).grid(row=0, column=idx, padx=10, pady=8, sticky="w")

        ttk.Button(box, text="Run Campaign", command=self.run_campaign).grid(row=0, column=4, padx=10, pady=8)

        self.execution_text = tk.Text(parent, height=26, wrap="word", font=("Consolas", 11))
        self.execution_text.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_analysis_tab(self, parent):
        metrics = ttk.LabelFrame(parent, text="Post-Campaign Revenue Analysis")
        metrics.pack(fill="x", padx=8, pady=8)

        self.tagged_var = tk.StringVar(value="0")
        self.conv_var = tk.StringVar(value="0")
        self.rev_var = tk.StringVar(value="$0.00")
        self.velocity_var = tk.StringVar(value="$0.00/day")

        labels = [
            ("Tagged Contacts", self.tagged_var),
            ("Total Conversions", self.conv_var),
            ("Campaign Revenue", self.rev_var),
            ("Revenue Velocity (5 days)", self.velocity_var),
        ]

        for i, (title, var) in enumerate(labels):
            card = ttk.Frame(metrics)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            ttk.Label(card, text=title, font=("Segoe UI", 10, "bold")).pack()
            ttk.Label(card, textvariable=var, font=("Segoe UI", 13)).pack(pady=(4, 0))

        self.segment_table = ttk.Treeview(
            parent,
            columns=("segment", "discount", "impressions", "conversions", "revenue"),
            show="headings",
            height=20,
        )
        for col, text, width in [
            ("segment", "Segment", 180),
            ("discount", "Discount %", 120),
            ("impressions", "Impressions", 130),
            ("conversions", "Conversions", 130),
            ("revenue", "Revenue", 140),
        ]:
            self.segment_table.heading(col, text=text)
            self.segment_table.column(col, width=width, anchor="center")

        self.segment_table.pack(fill="both", expand=True, padx=8, pady=8)

    def add_contact(self):
        name = self.name_var.get().strip()
        segment = self.segment_var.get()

        if not name:
            messagebox.showerror("Missing Name", "Please provide a contact name.")
            return

        try:
            aov = float(self.aov_var.get())
            if aov <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Value", "Average order value must be a positive number.")
            return

        self.contacts.append(Contact(name=name, segment=segment, average_order_value=aov, likely_to_convert=self.likely_var.get()))
        self.name_var.set("")
        self.refresh_contacts()

    def refresh_contacts(self):
        self.contact_table.delete(*self.contact_table.get_children())
        for c in self.contacts:
            self.contact_table.insert(
                "",
                "end",
                values=(c.name, c.segment, f"${c.average_order_value:.2f}", "Yes" if c.likely_to_convert else "No", "Yes" if c.tagged else "No"),
            )

    def auto_tag(self):
        if not self.contacts:
            messagebox.showwarning("No Contacts", "Add contacts before tagging.")
            return

        target_segments = {"Price-Sensitive", "Inactive", "Repeat", "VIP"}
        for c in self.contacts:
            c.tagged = c.segment in target_segments and (c.likely_to_convert or c.segment != "Inactive")

        self.refresh_contacts()
        tagged_count = sum(1 for c in self.contacts if c.tagged)
        messagebox.showinfo("Tagging Completed", f"Festival tag assigned to {tagged_count} contacts.")

    def load_demo(self):
        demo = [
            Contact("Aria", "VIP", 210, True),
            Contact("Ben", "Repeat", 125, True),
            Contact("Carlos", "Price-Sensitive", 80, True),
            Contact("Divya", "Inactive", 95, False),
            Contact("Elena", "Price-Sensitive", 75, True),
            Contact("Farhan", "Repeat", 140, True),
            Contact("Gia", "VIP", 260, True),
            Contact("Hana", "Inactive", 105, True),
        ]
        self.contacts = demo
        self.auto_tag()

    def clear_all(self):
        self.contacts.clear()
        self.results.clear()
        self.execution_text.delete("1.0", "end")
        self.refresh_contacts()
        self._update_analysis()

    def run_campaign(self):
        tagged_contacts = [c for c in self.contacts if c.tagged]
        if not tagged_contacts:
            messagebox.showwarning("No Tagged Contacts", "Tag contacts before running the campaign.")
            return

        steps = [step for step, enabled in self.step_vars.items() if enabled.get()]
        if not steps:
            messagebox.showwarning("No Steps Enabled", "Enable at least one promotional step.")
            return

        self.execution_text.delete("1.0", "end")
        self.results.clear()

        urgency_multiplier = {
            "Countdown Message": 0.10,
            "Early Access Offer": 0.18,
            "Last-Day Reminder": 0.25,
        }

        for step in steps:
            impressions = len(tagged_contacts)
            conversions = 0
            revenue = 0.0

            for c in tagged_contacts:
                base_prob = 0.08 if not c.likely_to_convert else 0.22
                segment_boost = self.SEGMENT_LIFT.get(c.segment, 1.0)
                discount = self.discount_map[c.segment].get() / 100
                convert_prob = min(0.92, (base_prob + urgency_multiplier[step]) * segment_boost)

                converted = convert_prob >= 0.35
                if converted:
                    conversions += 1
                    final_revenue = c.average_order_value * (1 - discount)
                    revenue += final_revenue

            self.results.append(CampaignStepResult(step=step, impressions=impressions, conversions=conversions, revenue=revenue))

            self.execution_text.insert(
                "end",
                f"{step}\n"
                f"  Impressions : {impressions}\n"
                f"  Conversions : {conversions}\n"
                f"  Revenue     : ${revenue:,.2f}\n"
                "-" * 60 + "\n",
            )

        self._update_analysis()

    def _update_analysis(self):
        tagged_contacts = [c for c in self.contacts if c.tagged]
        total_conversions = sum(step.conversions for step in self.results)
        total_revenue = sum(step.revenue for step in self.results)

        self.tagged_var.set(str(len(tagged_contacts)))
        self.conv_var.set(str(total_conversions))
        self.rev_var.set(f"${total_revenue:,.2f}")
        self.velocity_var.set(f"${(total_revenue / 5) if total_revenue else 0:,.2f}/day")

        segment_data: Dict[str, Dict[str, float]] = {s: {"impressions": 0, "conversions": 0, "revenue": 0.0} for s in self.SEGMENT_LIFT}

        steps_used = max(1, len(self.results))
        for c in tagged_contacts:
            seg = segment_data[c.segment]
            seg["impressions"] += steps_used

            discount = self.discount_map[c.segment].get() / 100
            expected_prob = min(0.9, (0.22 if c.likely_to_convert else 0.08) * self.SEGMENT_LIFT[c.segment] + 0.28)
            expected_conv = 1 if expected_prob >= 0.35 else 0
            seg["conversions"] += expected_conv
            seg["revenue"] += (c.average_order_value * (1 - discount) * expected_conv)

        self.segment_table.delete(*self.segment_table.get_children())
        for segment, data in segment_data.items():
            self.segment_table.insert(
                "",
                "end",
                values=(
                    segment,
                    f"{self.discount_map[segment].get():.1f}%",
                    int(data["impressions"]),
                    int(data["conversions"]),
                    f"${data['revenue']:,.2f}",
                ),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = FestivalOfferApp(root)
    root.mainloop()