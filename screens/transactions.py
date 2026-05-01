from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime

from database.db import get_transactions, add_transaction
from components.navbar import BottomNavBar


class TransactionsScreen(Screen):

    def on_enter(self, *_):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.user = app.current_user

        transactions = get_transactions(self.user["id"], limit=50)

        if hasattr(self, "start_date") and hasattr(self, "end_date"):
            transactions = [
                t for t in transactions
                if self.start_date <= t["date"] <= self.end_date
            ]

        income_list = [t for t in transactions if t["type"] == "income"]
        expense_list = [t for t in transactions if t["type"] == "expense"]

        tb = self.ids.table_body
        tb.clear_widgets()

        max_rows = max(len(income_list), len(expense_list), 6)

        for i in range(max_rows):
            inc = income_list[i] if i < len(income_list) else None
            exp = expense_list[i] if i < len(expense_list) else None

            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44))
            bg = (1, 1, 1, 1) if i % 2 == 0 else (0.96, 0.96, 0.96, 1)

            with row.canvas.before:
                Color(*bg)
                rect = Rectangle(size=row.size, pos=row.pos)

            row.bind(
                size=lambda w, v, r=rect: setattr(r, "size", v),
                pos=lambda w, v, r=rect: setattr(r, "pos", v)
            )

            row.add_widget(Label(
                text=inc["category"] if inc else "",
                font_size=dp(12),
                color=(0.1, 0.1, 0.1, 1),
                halign="center"
            ))

            row.add_widget(Label(
                text=f"${inc['amount']:,.2f}" if inc else "",
                font_size=dp(12),
                bold=True,
                color=(0.18, 0.60, 0.40, 1),
                halign="center"
            ))

            vd = Widget(size_hint_x=None, width=dp(1))
            with vd.canvas.before:
                Color(0.82, 0.82, 0.82, 1)
                vd_rect = Rectangle(size=vd.size, pos=vd.pos)

            vd.bind(
                size=lambda w, v, r=vd_rect: setattr(r, "size", v),
                pos=lambda w, v, r=vd_rect: setattr(r, "pos", v)
            )

            row.add_widget(vd)

            row.add_widget(Label(
                text=exp["category"] if exp else "",
                font_size=dp(12),
                color=(0.1, 0.1, 0.1, 1),
                halign="center"
            ))

            row.add_widget(Label(
                text=f"${exp['amount']:,.2f}" if exp else "",
                font_size=dp(12),
                bold=True,
                color=(0.85, 0.15, 0.15, 1),
                halign="center"
            ))

            tb.add_widget(row)

            hdiv = Widget(size_hint_y=None, height=dp(1))
            with hdiv.canvas.before:
                Color(0.88, 0.88, 0.88, 1)
                hd_rect = Rectangle(size=hdiv.size, pos=hdiv.pos)

            hdiv.bind(
                size=lambda w, v, r=hd_rect: setattr(r, "size", v),
                pos=lambda w, v, r=hd_rect: setattr(r, "pos", v)
            )

            tb.add_widget(hdiv)

        nav = self.ids.bottom_nav
        nav.clear_widgets()
        nav.add_widget(BottomNavBar(self.manager))

    def show_add_popup(self):
        self.selected_type = "expense"

        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))

        content.add_widget(Label(
            text="Add Transaction",
            font_size=dp(17),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        type_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )

        self.inc_btn = Button(
            text="Income",
            font_size=dp(14),
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1),
            color=(0.55, 0.55, 0.55, 1)
        )

        self.exp_btn = Button(
            text="Expense",
            font_size=dp(14),
            background_normal="",
            background_color=(0.098, 0.235, 0.204, 1),
            color=(1, 1, 1, 1)
        )

        self.inc_btn.bind(on_press=lambda *_: self._set_type("income"))
        self.exp_btn.bind(on_press=lambda *_: self._set_type("expense"))

        type_row.add_widget(self.inc_btn)
        type_row.add_widget(self.exp_btn)
        content.add_widget(type_row)

        ti_style = dict(
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14),
            padding=[dp(12), dp(10)],
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.55, 0.55, 0.55, 1)
        )

        self.amount_input = TextInput(
            hint_text="Amount (e.g. 50.00)",
            input_filter="float",
            **ti_style
        )

        self.category_input = TextInput(
            hint_text="Category (e.g. Food, Rent)",
            **ti_style
        )

        self.note_input = TextInput(
            hint_text="Note (optional)",
            **ti_style
        )

        content.add_widget(self.amount_input)
        content.add_widget(self.category_input)
        content.add_widget(self.note_input)

        self.popup_error = Label(
            text="",
            font_size=dp(12),
            color=(0.85, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(18)
        )

        content.add_widget(self.popup_error)

        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10)
        )

        cancel_btn = Button(
            text="Cancel",
            font_size=dp(14),
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1),
            color=(0.55, 0.55, 0.55, 1)
        )

        save_btn = Button(
            text="Save",
            font_size=dp(14),
            background_normal="",
            background_color=(0.298, 0.686, 0.522, 1),
            color=(1, 1, 1, 1)
        )

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        self.popup = Popup(
            title="",
            content=content,
            size_hint=(0.92, None),
            height=dp(440),
            separator_height=0,
            background="",
            background_color=(1, 1, 1, 1),
            overlay_color=(0, 0, 0, 0.45)
        )

        cancel_btn.bind(on_press=self.popup.dismiss)
        save_btn.bind(on_press=self._save_transaction)

        self.popup.open()

    def _set_type(self, t):
        self.selected_type = t

        active = (0.098, 0.235, 0.204, 1)
        inactive = (0.91, 0.91, 0.91, 1)

        if t == "income":
            self.inc_btn.background_color = active
            self.inc_btn.color = (1, 1, 1, 1)
            self.exp_btn.background_color = inactive
            self.exp_btn.color = (0.55, 0.55, 0.55, 1)
        else:
            self.exp_btn.background_color = active
            self.exp_btn.color = (1, 1, 1, 1)
            self.inc_btn.background_color = inactive
            self.inc_btn.color = (0.55, 0.55, 0.55, 1)

    def _save_transaction(self, *_):
        amount_text = self.amount_input.text.strip()
        category = self.category_input.text.strip()
        note = self.note_input.text.strip()

        if not amount_text or not category:
            self.popup_error.text = "Amount and category are required."
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.popup_error.text = "Enter a valid positive amount."
            return

        add_transaction(
            self.user["id"],
            self.selected_type,
            amount,
            category,
            note
        )

        self.popup.dismiss()
        self.refresh()

    def show_date_filter_popup(self):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        content.add_widget(Label(
            text="Select Date Range",
            font_size=dp(17),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        start_input = TextInput(
            hint_text="From date: YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14),
            padding=[dp(12), dp(10)],
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1)
        )

        end_input = TextInput(
            hint_text="To date: YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14),
            padding=[dp(12), dp(10)],
            background_normal="",
            background_color=(0.91, 0.91, 0.91, 1)
        )

        error_lbl = Label(
            text="",
            font_size=dp(12),
            color=(0.85, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(18)
        )

        content.add_widget(start_input)
        content.add_widget(end_input)
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
            size_hint=(0.88, None),
            height=dp(280),
            separator_height=0,
            background="",
            background_color=(1, 1, 1, 1),
            overlay_color=(0, 0, 0, 0.45)
        )

        def apply_filter(*_):
            start = start_input.text.strip()
            end = end_input.text.strip()

            try:
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                error_lbl.text = "Use YYYY-MM-DD format."
                return

            if start > end:
                error_lbl.text = "Start date must be before end date."
                return

            self.start_date = start
            self.end_date = end
            self.ids.date_label.text = f"From: {start}  to  {end}"

            popup.dismiss()
            self.refresh()

        cancel_btn.bind(on_press=popup.dismiss)
        apply_btn.bind(on_press=apply_filter)

        popup.open()