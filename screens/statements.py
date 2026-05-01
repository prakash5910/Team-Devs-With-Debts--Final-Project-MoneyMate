from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from datetime import datetime

from database.db import get_transactions
from components.navbar import BottomNavBar


class StatementsScreen(Screen):

    def on_enter(self, *_):
        if not hasattr(self, "statement_month"):
            self.statement_month = datetime.now().strftime("%Y-%m")
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.user = app.current_user

        transactions = get_transactions(self.user["id"], limit=1000)
        month_transactions = [
            t for t in transactions
            if t["date"].startswith(self.statement_month)
        ]

        income = sum(t["amount"] for t in month_transactions if t["type"] == "income")
        expense = sum(t["amount"] for t in month_transactions if t["type"] == "expense")
        balance = income - expense

        self.ids.month_label.text = f"Month: {self.statement_month}"
        self.ids.income_total.text = f"${income:,.2f}"
        self.ids.expense_total.text = f"${expense:,.2f}"
        self.ids.balance_total.text = f"${balance:,.2f}"
        self.ids.transaction_count.text = f"{len(month_transactions)} transactions"

        nav = self.ids.bottom_nav
        nav.clear_widgets()
        nav.add_widget(BottomNavBar(self.manager))

    def show_month_popup(self):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        content.add_widget(Label(
            text="Select Statement Month",
            font_size=dp(17),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(32)
        ))

        month_input = TextInput(
            hint_text="YYYY-MM",
            text=self.statement_month,
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=dp(15),
            padding=[dp(12), dp(10)],
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1)
        )

        error_lbl = Label(
            text="",
            font_size=dp(12),
            color=(0.85, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(20)
        )

        content.add_widget(month_input)
        content.add_widget(error_lbl)

        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10)
        )

        cancel_btn = Button(
            text="Cancel",
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1),
            color=(0.55, 0.55, 0.55, 1)
        )

        apply_btn = Button(
            text="Apply",
            background_normal="",
            background_color=(0.298, 0.686, 0.522, 1),
            color=(1, 1, 1, 1)
        )

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(apply_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.85, None),
            height=dp(230),
            separator_height=0,
            background="",
            background_color=(1, 1, 1, 1),
            overlay_color=(0, 0, 0, 0.45)
        )

        def apply_month(*_):
            value = month_input.text.strip()

            try:
                datetime.strptime(value, "%Y-%m")
            except ValueError:
                error_lbl.text = "Use YYYY-MM format."
                return

            self.statement_month = value
            popup.dismiss()
            self.refresh()

        cancel_btn.bind(on_press=popup.dismiss)
        apply_btn.bind(on_press=apply_month)
        popup.open()