from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout

from database.db import get_monthly_summary, get_goals, get_transactions


class GoalPreview(BoxLayout):
    goal_name = StringProperty("")
    goal_amount = StringProperty("")
    progress = NumericProperty(0)


class TransactionPreview(BoxLayout):
    text = StringProperty("")


class DashboardScreen(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.refresh(), 0)

    def refresh(self):
        app = App.get_running_app()
        user = app.current_user
        if not user:
            self.manager.current = "login"
            return

        summary = get_monthly_summary(user["id"])
        goals = get_goals(user["id"])
        transactions = get_transactions(user["id"], limit=5)

        income = summary["income"] or 0
        expense = summary["expense"] or 0
        balance = income - expense

        self.ids.greeting.text = f"Hello {user['name'].split()[0]}!"
        self.ids.month_label.text = f"Month: {datetime.now().strftime('%B')}"
        self.ids.income_label.text = f"${income:,.2f}"
        self.ids.expense_label.text = f"${expense:,.2f}"
        self.ids.balance_label.text = f"Balance: ${balance:,.2f}"

        self.ids.goal_box.clear_widgets()
        if goals:
            goal = goals[0]
            pct = min(goal["saved_amount"] / goal["target_amount"], 1.0) if goal["target_amount"] else 0
            self.ids.goal_box.add_widget(GoalPreview(
                goal_name=goal["name"],
                goal_amount=f"${goal['saved_amount']:,.0f} / ${goal['target_amount']:,.0f}",
                progress=pct * 100,
            ))
        else:
            self.ids.goal_box.add_widget(TransactionPreview(text="No goals yet. Tap Goals to create one."))

        self.ids.transaction_box.clear_widgets()
        if transactions:
            for t in transactions:
                sign = "+" if t["type"] == "income" else "-"
                self.ids.transaction_box.add_widget(TransactionPreview(
                    text=f"{t['category']}   {sign}${t['amount']:,.2f}"
                ))
        else:
            self.ids.transaction_box.add_widget(TransactionPreview(text="No transactions yet."))
