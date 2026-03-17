import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ticket:
    ticket_id: str
    customer: str
    issue: str
    sla_minutes: int
    elapsed_minutes: int
    severity: str
    churn_risk: float
    channel: str
    created_at: str


SEVERITY_WEIGHT = {
    "Low": 0.1,
    "Medium": 0.2,
    "High": 0.35,
    "Critical": 0.5,
}


class SupportSLARiskApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Support SLA Risk Monitoring Model")
        self.root.geometry("1200x760")

        self.tickets: list[Ticket] = []

        self._build_ui()

    def _build_ui(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main,
            text="Support SLA Risk Monitoring Model",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            text=(
                "Objective: prevent churn caused by delayed support through SLA countdowns, "
                "automatic risk tagging, and supervisor intervention."
            ),
            foreground="#1f4f7a",
        ).pack(anchor="w", pady=(0, 8))

        form = ttk.LabelFrame(main, text="Ticket Intake", padding=10)
        form.pack(fill=tk.X, pady=(0, 8))

        self.ticket_id_var = tk.StringVar()
        self.customer_var = tk.StringVar()
        self.issue_var = tk.StringVar()
        self.sla_var = tk.StringVar(value="120")
        self.elapsed_var = tk.StringVar(value="0")
        self.severity_var = tk.StringVar(value="High")
        self.churn_var = tk.StringVar(value="0.40")
        self.channel_var = tk.StringVar(value="Gallabox")
        self.threshold_var = tk.StringVar(value="80")

        row1 = ttk.Frame(form)
        row1.pack(fill=tk.X, pady=2)
        self._labeled_entry(row1, "Ticket ID", self.ticket_id_var, 14)
        self._labeled_entry(row1, "Customer", self.customer_var, 24)
        self._labeled_entry(row1, "Issue", self.issue_var, 40)

        row2 = ttk.Frame(form)
        row2.pack(fill=tk.X, pady=2)
        self._labeled_entry(row2, "SLA (minutes)", self.sla_var, 10)
        self._labeled_entry(row2, "Elapsed (minutes)", self.elapsed_var, 12)
        self._labeled_combo(row2, "Severity", self.severity_var, ["Low", "Medium", "High", "Critical"], 10)
        self._labeled_entry(row2, "Churn Risk (0-1)", self.churn_var, 10)
        self._labeled_entry(row2, "Channel", self.channel_var, 12)
        self._labeled_entry(row2, "Risk Threshold %", self.threshold_var, 10)

        actions = ttk.Frame(form)
        actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(actions, text="Log Ticket", command=self.log_ticket).pack(side=tk.LEFT)
        ttk.Button(actions, text="Load SaaS Billing Example", command=self.load_example).pack(side=tk.LEFT, padx=6)
        ttk.Button(actions, text="Run Risk Scan", command=self.refresh_monitor).pack(side=tk.LEFT)
        ttk.Button(actions, text="+1 Minute Tick", command=self.increment_all_elapsed).pack(side=tk.LEFT, padx=6)

        workflow_frame = ttk.LabelFrame(main, text="Operational Workflow", padding=10)
        workflow_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            workflow_frame,
            text=(
                "1) Ticket logged   →   2) SLA countdown initiated   →   3) Risk threshold triggered   "
                "→   4) Support SLA Risk tag assignment   →   5) Immediate intervention"
            ),
            font=("Segoe UI", 10, "italic"),
        ).pack(anchor="w")

        columns = (
            "ticket_id",
            "customer",
            "issue",
            "elapsed",
            "sla",
            "utilization",
            "risk_score",
            "tag",
            "action",
        )
        self.tree = ttk.Treeview(main, columns=columns, show="headings", height=16)
        self.tree.pack(fill=tk.BOTH, expand=True)

        for col, w in [
            ("ticket_id", 100),
            ("customer", 150),
            ("issue", 220),
            ("elapsed", 90),
            ("sla", 90),
            ("utilization", 110),
            ("risk_score", 110),
            ("tag", 170),
            ("action", 210),
        ]:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=w, anchor=tk.W)

        self.summary_var = tk.StringVar(value="No tickets yet.")
        ttk.Label(main, textvariable=self.summary_var, foreground="#0b5394").pack(anchor="w", pady=(8, 0))

    def _labeled_entry(self, parent, label, var, width):
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=4)
        ttk.Label(frame, text=label).pack(anchor="w")
        ttk.Entry(frame, textvariable=var, width=width).pack(anchor="w")

    def _labeled_combo(self, parent, label, var, values, width):
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=4)
        ttk.Label(frame, text=label).pack(anchor="w")
        ttk.Combobox(frame, textvariable=var, values=values, width=width, state="readonly").pack(anchor="w")

    def log_ticket(self):
        try:
            sla = int(self.sla_var.get())
            elapsed = int(self.elapsed_var.get())
            churn = float(self.churn_var.get())
            if sla <= 0 or elapsed < 0 or not (0 <= churn <= 1):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Use valid values: SLA>0, elapsed>=0, churn risk between 0 and 1.")
            return

        if not self.ticket_id_var.get().strip() or not self.customer_var.get().strip() or not self.issue_var.get().strip():
            messagebox.showerror("Missing Fields", "Ticket ID, Customer, and Issue are required.")
            return

        ticket = Ticket(
            ticket_id=self.ticket_id_var.get().strip(),
            customer=self.customer_var.get().strip(),
            issue=self.issue_var.get().strip(),
            sla_minutes=sla,
            elapsed_minutes=elapsed,
            severity=self.severity_var.get(),
            churn_risk=churn,
            channel=self.channel_var.get().strip() or "Gallabox",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.tickets.append(ticket)
        self.refresh_monitor()

    def compute_predictive_risk_score(self, ticket: Ticket):
        utilization = ticket.elapsed_minutes / ticket.sla_minutes
        severity_component = SEVERITY_WEIGHT.get(ticket.severity, 0.2)
        channel_component = 0.08 if ticket.channel.lower() == "gallabox" else 0.03

        score = (
            utilization * 0.55
            + ticket.churn_risk * 0.30
            + severity_component
            + channel_component
        )
        normalized = min(max(score, 0), 1)
        return normalized, utilization

    def get_tag_and_action(self, utilization: float, risk_score: float):
        threshold = float(self.threshold_var.get()) / 100
        if utilization >= 1:
            return "SLA Breach", "Escalate to retention + incident room"
        if utilization >= threshold or risk_score >= 0.75:
            return "Support SLA Risk", "Alert supervisor for immediate intervention"
        if utilization >= threshold * 0.75:
            return "Watchlist", "Reprioritize queue and monitor closely"
        return "Healthy", "Standard handling"

    def refresh_monitor(self):
        self.tree.delete(*self.tree.get_children())

        total = len(self.tickets)
        high_risk_count = 0
        breached = 0

        for t in self.tickets:
            risk_score, utilization = self.compute_predictive_risk_score(t)
            tag, action = self.get_tag_and_action(utilization, risk_score)

            if tag == "Support SLA Risk":
                high_risk_count += 1
            if tag == "SLA Breach":
                breached += 1

            self.tree.insert(
                "",
                tk.END,
                values=(
                    t.ticket_id,
                    t.customer,
                    t.issue,
                    t.elapsed_minutes,
                    t.sla_minutes,
                    f"{utilization * 100:.1f}%",
                    f"{risk_score * 100:.1f}%",
                    tag,
                    action,
                ),
            )

        self.summary_var.set(
            f"Tickets: {total} | Support SLA Risk tagged: {high_risk_count} | Breached: {breached} | "
            "Revenue logic: faster resolution lowers cancellation risk and strengthens brand trust."
        )

    def increment_all_elapsed(self):
        if not self.tickets:
            messagebox.showinfo("No Tickets", "Log at least one ticket first.")
            return

        for t in self.tickets:
            t.elapsed_minutes += 1
        self.refresh_monitor()

    def load_example(self):
        self.ticket_id_var.set("GBX-2048")
        self.customer_var.set("Nimbus SaaS")
        self.issue_var.set("Billing error affecting renewal")
        self.sla_var.set("120")
        self.elapsed_var.set("97")
        self.severity_var.set("Critical")
        self.churn_var.set("0.78")
        self.channel_var.set("Gallabox")
        self.threshold_var.set("80")


if __name__ == "__main__":
    root = tk.Tk()
    app = SupportSLARiskApp(root)
    root.mainloop()