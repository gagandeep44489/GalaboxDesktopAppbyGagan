import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from datetime import datetime


TRIAL_LENGTH_DAYS = 7


@dataclass
class TrialUser:
    name: str
    email: str
    activated_day: int
    tag: str = "Free Trial User"
    engagement_score: int = 0
    converted: bool = False
    expired: bool = False
    messages_sent: list[str] = field(default_factory=list)

    @property
    def trial_day(self) -> int:
        return self.current_day - self.activated_day + 1

    @property
    def current_day(self) -> int:
        return AppState.current_day

    @property
    def segment(self) -> str:
        return "Active" if self.engagement_score >= 3 else "Inactive"


class AppState:
    current_day = 1


class FreeTrialConversionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Free Trial User Conversion Model")
        self.geometry("1150x700")
        self.users: list[TrialUser] = []

        self._build_layout()
        self._refresh_dashboard()

    def _build_layout(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.day_label = ttk.Label(top, text="Day 1", font=("Segoe UI", 14, "bold"))
        self.day_label.pack(side="left")

        ttk.Button(top, text="Advance to Next Day", command=self.advance_day).pack(side="left", padx=10)
        ttk.Button(top, text="Run Mid-Trial Engagement Check", command=self.run_mid_trial_check).pack(side="left", padx=5)

        stats = ttk.Frame(self, padding=(10, 0))
        stats.pack(fill="x")

        self.stats_label = ttk.Label(stats, text="", font=("Segoe UI", 10))
        self.stats_label.pack(anchor="w")

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.Frame(paned, padding=8)
        right = ttk.Frame(paned, padding=8)
        paned.add(left, weight=2)
        paned.add(right, weight=3)

        # Activation form
        form = ttk.LabelFrame(left, text="1) Trial Activation + 2) Tag Assignment", padding=10)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Email").grid(row=1, column=0, sticky="w")

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()

        ttk.Entry(form, textvariable=self.name_var, width=28).grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        ttk.Entry(form, textvariable=self.email_var, width=28).grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        ttk.Button(form, text="Activate Trial", command=self.activate_trial).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # user table
        table_frame = ttk.LabelFrame(left, text="Trial Users", padding=8)
        table_frame.pack(fill="both", expand=True)

        columns = ("name", "email", "trial_day", "segment", "engagement", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col, w in zip(columns, (120, 210, 70, 80, 100, 90)):
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Log Feature Interaction (+1)", command=self.log_interaction).pack(fill="x", pady=2)
        ttk.Button(actions, text="Force Convert Selected", command=self.convert_selected).pack(fill="x", pady=2)

        # workflow + event log
        workflow = ttk.LabelFrame(right, text="Operational Workflow", padding=10)
        workflow.pack(fill="x", pady=(0, 10))

        workflow_text = (
            "1. Trial activation\n"
            "2. Free Trial User tag assignment\n"
            "3. Automated onboarding sequence\n"
            "4. Mid-trial engagement check (active vs inactive)\n"
            "5. Expiry reminder + upgrade offer"
        )
        ttk.Label(workflow, text=workflow_text, justify="left").pack(anchor="w")

        log_frame = ttk.LabelFrame(right, text="Automation & Revenue Event Log", padding=10)
        log_frame.pack(fill="both", expand=True)

        self.log_box = tk.Text(log_frame, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True)

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def activate_trial(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()

        if not name or not email:
            messagebox.showwarning("Missing data", "Please enter both name and email.")
            return

        user = TrialUser(name=name, email=email, activated_day=AppState.current_day)
        self.users.append(user)

        self.name_var.set("")
        self.email_var.set("")

        self.log(f"{name} activated trial and received tag: '{user.tag}'.")
        self._send_onboarding_messages(user)
        self._refresh_dashboard()

    def _send_onboarding_messages(self, user: TrialUser):
        steps = [
            "Welcome tutorial: complete your first dashboard setup.",
            "Feature highlight: real-time analytics and custom reports.",
            "Milestone prompt: connect your first data source.",
        ]
        for msg in steps:
            user.messages_sent.append(msg)
            self.log(f"Auto-message to {user.name}: {msg}")

    def _send_day_based_messages(self, user: TrialUser, trial_day: int):
        if trial_day == 3:
            msg = "Milestone reminder: You've reached day 3—try team sharing."
            user.messages_sent.append(msg)
            self.log(f"{user.name}: {msg}")
        elif trial_day == 6:
            msg = "Expiry reminder: 1 day left. Upgrade now for 10% off annual plan."
            user.messages_sent.append(msg)
            self.log(f"{user.name}: {msg}")

    def advance_day(self):
        AppState.current_day += 1
        for user in self.users:
            if user.converted or user.expired:
                continue
            trial_day = AppState.current_day - user.activated_day + 1
            self._send_day_based_messages(user, trial_day)
            if trial_day > TRIAL_LENGTH_DAYS:
                user.expired = True
                self.log(f"{user.name}'s trial expired. Final upgrade offer delivered.")
        self._refresh_dashboard()

    def run_mid_trial_check(self):
        for user in self.users:
            if user.converted or user.expired:
                continue
            trial_day = AppState.current_day - user.activated_day + 1
            if trial_day >= 4:
                if user.segment == "Inactive":
                    prompt = "Need help? Book a 10-min setup call to see value faster."
                    self.log(f"Mid-trial check ({user.name}, Inactive): {prompt}")
                    user.messages_sent.append(prompt)
                else:
                    upsell = "Power user tip: unlock advanced analytics with paid plan."
                    self.log(f"Mid-trial check ({user.name}, Active): {upsell}")
                    user.messages_sent.append(upsell)
        self._refresh_dashboard()

    def log_interaction(self):
        user = self._selected_user()
        if not user:
            return
        if user.converted or user.expired:
            messagebox.showinfo("Not allowed", "Cannot log activity for converted/expired users.")
            return
        user.engagement_score += 1
        self.log(f"Interaction logged for {user.name}. Engagement score: {user.engagement_score}.")
        self._refresh_dashboard()

    def convert_selected(self):
        user = self._selected_user()
        if not user:
            return
        if user.expired:
            messagebox.showinfo("Unavailable", "Cannot convert expired trial.")
            return
        if user.converted:
            messagebox.showinfo("Already converted", "User is already a paid subscriber.")
            return
        user.converted = True
        self.log(f"{user.name} upgraded to paid subscription before trial expiration.")
        self._refresh_dashboard()

    def _selected_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a user first.")
            return None
        index = int(selected[0])
        return self.users[index]

    def _refresh_dashboard(self):
        self.day_label.config(text=f"Day {AppState.current_day}")

        for row in self.tree.get_children():
            self.tree.delete(row)

        converted = 0
        active = 0
        inactive = 0

        for idx, user in enumerate(self.users):
            td = max(1, AppState.current_day - user.activated_day + 1)
            status = "Converted" if user.converted else "Expired" if user.expired else "Trial"
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(user.name, user.email, td, user.segment, user.engagement_score, status),
            )

            if user.segment == "Active":
                active += 1
            else:
                inactive += 1
            if user.converted:
                converted += 1

        total = len(self.users)
        rate = (converted / total * 100) if total else 0
        self.stats_label.config(
            text=(
                f"Total Trial Users: {total}   |   Converted: {converted}   |   "
                f"Conversion Rate: {rate:.1f}%   |   Active Segment: {active}   |   Inactive Segment: {inactive}"
            )
        )


if __name__ == "__main__":
    app = FreeTrialConversionApp()
    app.mainloop()