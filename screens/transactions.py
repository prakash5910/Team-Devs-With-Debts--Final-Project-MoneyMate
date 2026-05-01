from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime

from database.db import get_transactions, add_transaction
from components.navbar import BottomNavBar

class TransactionsScreen(Screen):
    def on_enter(self, *_):
        self.refresh()

    def refresh(self, clear_filters=False):
        app = App.get_running_app()
        self.user = getattr(app, 'current_user', None)
        if not self.user: return

        if clear_filters:
            if hasattr(self, "start_date"): del self.start_date
            if hasattr(self, "end_date"): del self.end_date
            self.ids.date_label.text = "Showing: All History"

        transactions = get_transactions(self.user["id"], limit=50)
        transactions.sort(key=lambda x: str(x['date']), reverse=True)

        if hasattr(self, "start_date") and hasattr(self, "end_date"):
            transactions = [
                t for t in transactions
                if self.start_date <= str(t["date"]) <= self.end_date
            ]

        tb = self.ids.table_body
        tb.clear_widgets()

        for t in transactions:
            tb.add_widget(self._create_transaction_item(t))

        nav = self.ids.bottom_nav
        nav.clear_widgets()
        nav.add_widget(BottomNavBar(self.manager))

    def _create_transaction_item(self, t):
        is_inc = t["type"] == "income"
        color = (0.18, 0.60, 0.40, 1) if is_inc else (0.85, 0.15, 0.15, 1)
        
        # Increased horizontal padding to dp(20) to move text away from edges
        item = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(75), 
                         padding=[dp(20), dp(12)], spacing=dp(15))
        
        with item.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(14)])
            Color(0, 0, 0, 0.05)
            Line(rounded_rectangle=[item.x, item.y, item.width, item.height, dp(14)], width=1.2)
        
        # Link card background to movement
        item.bind(pos=self._update_item_graphics, size=self._update_item_graphics)

        details = BoxLayout(orientation="vertical", spacing=dp(2))
        
        # text_size adjusted to match width for proper halign="left"
        details.add_widget(Label(
            text=t["category"], 
            bold=True, 
            color=(0.1, 0.1, 0.1, 1), 
            font_size=dp(15),
            halign="left", 
            valign="middle",
            text_size=(dp(200), None)
        ))
        
        details.add_widget(Label(
            text=str(t["date"]), 
            font_size=dp(12), 
            color=(0.5, 0.5, 0.5, 1), 
            halign="left", 
            valign="middle",
            text_size=(dp(200), None)
        ))
        item.add_widget(details)

        amt = Label(
            text=f"{'+' if is_inc else '-'}${t['amount']:,.2f}", 
            bold=True, 
            color=color, 
            font_size=dp(16),
            halign="right", 
            valign="middle",
            size_hint_x=None, 
            width=dp(110),
            text_size=(dp(110), None)
        )
        item.add_widget(amt)
        return item

    def _update_item_graphics(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(14)])
            Color(0, 0, 0, 0.05)
            Line(rounded_rectangle=[instance.x, instance.y, instance.width, instance.height, dp(14)], width=1.2)

    def show_add_popup(self):
        self.selected_type = "expense"
        content = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15))
        
        content.add_widget(Label(text="New Entry", font_size=dp(20), bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=dp(30)))

        type_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        self.inc_btn = Button(text="Income", background_color=(0,0,0,0), color=(0.5, 0.5, 0.5, 1))
        self.exp_btn = Button(text="Expense", background_color=(0,0,0,0), color=(1, 1, 1, 1))
        
        with self.inc_btn.canvas.before:
            self.inc_bg = Color(0.9, 0.9, 0.9, 1)
            self.inc_rect = RoundedRectangle(pos=self.inc_btn.pos, size=self.inc_btn.size, radius=[dp(10)])
        with self.exp_btn.canvas.before:
            self.exp_bg = Color(0.098, 0.235, 0.204, 1)
            self.exp_rect = RoundedRectangle(pos=self.exp_btn.pos, size=self.exp_btn.size, radius=[dp(10)])

        def update_toggle(*_):
            self.inc_rect.pos = self.inc_btn.pos
            self.inc_rect.size = self.inc_btn.size
            self.exp_rect.pos = self.exp_btn.pos
            self.exp_rect.size = self.exp_btn.size

        self.inc_btn.bind(pos=update_toggle, size=update_toggle, on_release=lambda *_: self._set_type("income"))
        self.exp_btn.bind(pos=update_toggle, size=update_toggle, on_release=lambda *_: self._set_type("expense"))
        
        type_row.add_widget(self.inc_btn)
        type_row.add_widget(self.exp_btn)
        content.add_widget(type_row)

        self.amount_input = TextInput(hint_text="0.00", input_filter="float", multiline=False, size_hint_y=None, height=dp(48), padding=[dp(12), dp(12)], background_color=(0.96, 0.97, 0.98, 1), background_normal="")
        self.category_input = TextInput(hint_text="Category", multiline=False, size_hint_y=None, height=dp(48), padding=[dp(12), dp(12)], background_color=(0.96, 0.97, 0.98, 1), background_normal="")
        
        content.add_widget(self.amount_input)
        content.add_widget(self.category_input)

        save_btn = Button(text="SAVE TRANSACTION", bold=True, size_hint_y=None, height=dp(55), background_color=(0,0,0,0))
        with save_btn.canvas.before:
            Color(0.298, 0.686, 0.522, 1)
            self.save_rect = RoundedRectangle(pos=save_btn.pos, size=save_btn.size, radius=[dp(15)])
        
        save_btn.bind(on_release=self._save_transaction, pos=lambda inst, pos: setattr(self.save_rect, 'pos', pos), size=lambda inst, size: setattr(self.save_rect, 'size', size))
        
        content.add_widget(save_btn)

        self.popup = Popup(title="", content=content, size_hint=(0.9, None), height=dp(440), background_color=(1,1,1,1), separator_height=0)
        self.popup.open()

    def _set_type(self, t):
        self.selected_type = t
        if t == "income":
            self.inc_bg.rgba = (0.098, 0.235, 0.204, 1); self.inc_btn.color = (1,1,1,1)
            self.exp_bg.rgba = (0.9, 0.9, 0.9, 1); self.exp_btn.color = (0.5, 0.5, 0.5, 1)
        else:
            self.exp_bg.rgba = (0.098, 0.235, 0.204, 1); self.exp_btn.color = (1,1,1,1)
            self.inc_bg.rgba = (0.9, 0.9, 0.9, 1); self.inc_btn.color = (0.5, 0.5, 0.5, 1)

    def _save_transaction(self, *_):
        try:
            amt_val = self.amount_input.text.strip()
            cat_val = self.category_input.text.strip()
            if amt_val and cat_val:
                add_transaction(self.user["id"], self.selected_type, float(amt_val), cat_val, "")
                self.popup.dismiss()
                self.refresh(clear_filters=True)
        except ValueError: pass

    def show_date_filter_popup(self):
        content = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15))
        content.add_widget(Label(text="Filter Activity", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=dp(30)))
        start = TextInput(hint_text="YYYY-MM-DD", multiline=False, size_hint_y=None, height=dp(44), padding=[dp(10), dp(10)])
        end = TextInput(hint_text="YYYY-MM-DD", multiline=False, size_hint_y=None, height=dp(44), padding=[dp(10), dp(10)])
        content.add_widget(start); content.add_widget(end)
        apply_btn = Button(text="APPLY FILTER", bold=True, size_hint_y=None, height=dp(50), background_color=(0,0,0,0))
        with apply_btn.canvas.before:
            Color(0.298, 0.686, 0.522, 1); RoundedRectangle(pos=apply_btn.pos, size=apply_btn.size, radius=[dp(12)])
        def apply(*_):
            if start.text and end.text:
                self.start_date, self.end_date = start.text, end.text
                self.ids.date_label.text = f"From: {start.text} to {end.text}"
                popup.dismiss(); self.refresh()
        apply_btn.bind(on_release=apply)
        content.add_widget(apply_btn)
        popup = Popup(title="", content=content, size_hint=(0.85, None), height=dp(340), background_color=(1,1,1,1), separator_height=0)
        popup.open()