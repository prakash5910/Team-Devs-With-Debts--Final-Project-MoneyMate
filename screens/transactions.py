from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.clock import Clock
from database.db import get_transactions, add_transaction


class TransactionRow(BoxLayout):
    income_detail = StringProperty("")
    income_amount = StringProperty("")
    expense_detail = StringProperty("")
    expense_amount = StringProperty("")


class TransactionsScreen(Screen):
    selected_type = "expense"

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.refresh(), 0)

    def refresh(self):
        app = App.get_running_app()
        self.user = app.current_user
        if not self.user:
            self.manager.current = "login"
            return

        transactions = get_transactions(self.user["id"], limit=50)
        income_list = [t for t in transactions if t["type"] == "income"]
        expense_list = [t for t in transactions if t["type"] == "expense"]

        self.ids.table_body.clear_widgets()
        max_rows = max(len(income_list), len(expense_list), 6)
        for i in range(max_rows):
            inc = income_list[i] if i < len(income_list) else None
            exp = expense_list[i] if i < len(expense_list) else None
            self.ids.table_body.add_widget(TransactionRow(
                income_detail=inc["category"] if inc else "",
                income_amount=f"${inc['amount']:,.2f}" if inc else "",
                expense_detail=exp["category"] if exp else "",
                expense_amount=f"${exp['amount']:,.2f}" if exp else "",
            ))

    def show_add_popup(self):
        self.selected_type = "expense"
        self.ids.amount_input.text = ""
        self.ids.category_input.text = ""
        self.ids.note_input.text = ""
        self.ids.popup_error.text = ""
        self._set_type("expense")
        self.popup = Popup(title="", content=self.ids.popup_content, size_hint=(0.9, None), height="360dp", separator_height=0)
        self.ids.popup_holder.remove_widget(self.ids.popup_content)
        self.popup.bind(on_dismiss=lambda *a: self.ids.popup_holder.add_widget(self.ids.popup_content))
        self.popup.open()

    def _set_type(self, t_type):
        self.selected_type = t_type
        self.ids.inc_btn.state = "down" if t_type == "income" else "normal"
        self.ids.exp_btn.state = "down" if t_type == "expense" else "normal"

    def save_transaction(self):
        try:
            amount = float(self.ids.amount_input.text.strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.ids.popup_error.text = "Enter a valid amount."
            return

        category = self.ids.category_input.text.strip()
        note = self.ids.note_input.text.strip()
        if not category:
            self.ids.popup_error.text = "Enter a category."
            return

        add_transaction(self.user["id"], self.selected_type, amount, category, note)
        self.popup.dismiss()
        self.refresh()
