from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime, timedelta

from database.db import get_goals, add_goal, update_goal_saved, delete_goal, get_monthly_summary
from components.navbar import BottomNavBar


class GoalsScreen(Screen):

    def on_enter(self, *_):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.user = app.current_user
        goals = get_goals(self.user["id"])

        gc = self.ids.goals_container
        gc.clear_widgets()

        if goals:
            for goal in goals:
                gc.add_widget(self._goal_card(goal))
        else:
            gc.add_widget(Label(
                text="No goals yet.\nTap '+ New' to create one!",
                font_size=dp(15), color=(0.55, 0.55, 0.55, 1),
                halign="center", size_hint_y=None, height=dp(80)
            ))

        nav = self.ids.bottom_nav
        nav.clear_widgets()
        nav.add_widget(BottomNavBar(self.manager))

    def _goal_card(self, goal):
        pct = min(goal["saved_amount"] / goal["target_amount"], 1.0) \
              if goal["target_amount"] > 0 else 0

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None, height=dp(140),
            padding=dp(14), spacing=dp(8)
        )
        with card.canvas.before:
            Color(0.95, 0.97, 0.95, 1)
            rect = RoundedRectangle(radius=[dp(12)], size=card.size, pos=card.pos)
        card.bind(size=lambda *_: setattr(rect, 'size', card.size),
                  pos=lambda *_: setattr(rect, 'pos', card.pos))

        # Name + amounts row
        name_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
        name_row.add_widget(Label(
            text=goal["name"], font_size=dp(15), bold=True,
            color=(0.1, 0.1, 0.1, 1), halign="left", text_size=(None, None)
        ))
        name_row.add_widget(Label(
            text=f"${goal['saved_amount']:,.2f} / ${goal['target_amount']:,.2f}",
            font_size=dp(12), color=(0.55, 0.55, 0.55, 1),
            halign="right", text_size=(None, None)
        ))
        card.add_widget(name_row)

        # Progress bar
        bar = Widget(size_hint_y=None, height=dp(28))
        def draw_bar(w, *_):
            w.canvas.clear()
            with w.canvas:
                pad = dp(3)
                Color(0.098, 0.235, 0.204, 1)
                RoundedRectangle(radius=[dp(6)], size=w.size, pos=w.pos)
                Color(1, 1, 1, 1)
                RoundedRectangle(
                    radius=[dp(4)],
                    size=(w.width - pad*2, w.height - pad*2),
                    pos=(w.x + pad, w.y + pad)
                )
                fill_w = max((w.width - pad*4) * pct, 0)
                Color(0.298, 0.686, 0.522, 1)
                RoundedRectangle(
                    radius=[dp(4)],
                    size=(fill_w, w.height - pad*4),
                    pos=(w.x + pad*2, w.y + pad*2)
                )
        bar.bind(size=draw_bar, pos=draw_bar)
        card.add_widget(bar)

        # Buttons row
        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(34), spacing=dp(8))
        btn_row.add_widget(Label(
            text=f"{pct*100:.0f}%",
            font_size=dp(12), color=(0.55, 0.55, 0.55, 1),
            halign="left", text_size=(None, None)
        ))
        details_btn = Button(
            text="Details", font_size=dp(12), background_normal="",
            background_color=(0.298, 0.686, 0.522, 1), color=(1, 1, 1, 1),
            size_hint_x=None, width=dp(68)
        )
        add_btn = Button(
            text="+ Save", font_size=dp(12), background_normal="",
            background_color=(0.098, 0.235, 0.204, 1), color=(1, 1, 1, 1),
            size_hint_x=None, width=dp(68)
        )
        del_btn = Button(
            text="Delete", font_size=dp(12), background_normal="",
            background_color=(0.85, 0.15, 0.15, 1), color=(1, 1, 1, 1),
            size_hint_x=None, width=dp(60)
        )
        details_btn.bind(on_press=lambda *_: self.show_goal_detail(goal))
        add_btn.bind(on_press=lambda *_: self.show_add_savings(goal))
        del_btn.bind(on_press=lambda *_: self._delete_goal(goal["id"]))
        btn_row.add_widget(details_btn)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(del_btn)
        card.add_widget(btn_row)

        return card

    def show_goal_detail(self, goal):
        pct = (goal["saved_amount"] / goal["target_amount"] * 100) \
            if goal["target_amount"] > 0 else 0

        summary = get_monthly_summary(self.user["id"])
        monthly_net = summary["income"] - summary["expense"]
        remaining = goal["target_amount"] - goal["saved_amount"]

        if remaining <= 0:
            eta_str = "Goal Reached!"
        elif monthly_net > 0:
            days = int((remaining / monthly_net) * 30)
            eta_str = (datetime.now() + timedelta(days=days)).strftime("%m / %d / %y")
        else:
            eta_str = "-- / -- / --"

        content = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(16)],
            spacing=dp(14)
        )

        with content.canvas.before:
            Color(1, 1, 1, 1)
            bg = RoundedRectangle(radius=[dp(12)], size=content.size, pos=content.pos)

        content.bind(
            size=lambda *_: setattr(bg, "size", content.size),
            pos=lambda *_: setattr(bg, "pos", content.pos)
        )

        top_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40)
        )

        close_btn = Button(
            text="X",
            font_size=dp(15),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            background_normal="",
            background_color=(0.9, 0.9, 0.9, 1),
            size_hint=(None, None),
            size=(dp(36), dp(36))
        )

        top_row.add_widget(close_btn)

        top_row.add_widget(Label(
            text=goal["name"],
            font_size=dp(18),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign="center",
            valign="middle",
            text_size=(dp(220), dp(40))
        ))

        content.add_widget(top_row)

        content.add_widget(Label(
            text=f"Goal:   ${goal['target_amount']:,.2f}",
            font_size=dp(16),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(Label(
            text=f"Saved: ${goal['saved_amount']:,.2f}   ({pct:.2f}%)",
            font_size=dp(16),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(Label(
            text="Expected Date of Completion:",
            font_size=dp(15),
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        content.add_widget(Label(
            text=eta_str,
            font_size=dp(22),
            bold=True,
            color=(0.098, 0.235, 0.204, 1),
            size_hint_y=None,
            height=dp(40)
        ))

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.82, None),
            height=dp(300),
            separator_height=0,
            background="",
            background_color=(1, 1, 1, 1),
            overlay_color=(0, 0, 0, 0.45)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_add_savings(self, goal):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        content.add_widget(Label(
            text=f"Add savings to: {goal['name']}",
            font_size=dp(15), bold=True, color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None, height=dp(28)
        ))
        amount_input = TextInput(
            hint_text="Amount", multiline=False, input_filter="float",
            size_hint_y=None, height=dp(44), font_size=dp(14),
            padding=[dp(12), dp(10)], background_normal="",
            background_color=(0.91, 0.91, 0.91, 1)
        )
        error_lbl = Label(
            text="", font_size=dp(12), color=(0.85, 0.15, 0.15, 1),
            size_hint_y=None, height=dp(18)
        )
        content.add_widget(amount_input)
        content.add_widget(error_lbl)

        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(
            text="Cancel", background_normal="",
            background_color=(0.91, 0.91, 0.91, 1), color=(0.55, 0.55, 0.55, 1)
        )
        save_btn = Button(
            text="Add", background_normal="",
            background_color=(0.298, 0.686, 0.522, 1), color=(1, 1, 1, 1)
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title="", content=content,
            size_hint=(0.85, None), height=dp(240),
            separator_height=0
        )

        def save(*_):
            try:
                amt = float(amount_input.text.strip())
                if amt <= 0: raise ValueError
            except ValueError:
                error_lbl.text = "Enter a valid amount."
                return
            update_goal_saved(goal["id"], amt)
            popup.dismiss()
            self.refresh()

        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=save)
        popup.open()

    def show_add_popup(self):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        content.add_widget(Label(
            text="New Goal", font_size=dp(17), bold=True,
            color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=dp(30)
        ))
        name_input = TextInput(
            hint_text="Goal name (e.g. Emergency Fund)", multiline=False,
            size_hint_y=None, height=dp(44), font_size=dp(14),
            padding=[dp(12), dp(10)], background_normal="",
            background_color=(0.91, 0.91, 0.91, 1)
        )
        target_input = TextInput(
            hint_text="Target amount (e.g. 1000)", multiline=False, input_filter="float",
            size_hint_y=None, height=dp(44), font_size=dp(14),
            padding=[dp(12), dp(10)], background_normal="",
            background_color=(0.91, 0.91, 0.91, 1)
        )
        error_lbl = Label(
            text="", font_size=dp(12), color=(0.85, 0.15, 0.15, 1),
            size_hint_y=None, height=dp(18)
        )
        content.add_widget(name_input)
        content.add_widget(target_input)
        content.add_widget(error_lbl)

        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel_btn = Button(
            text="Cancel", background_normal="",
            background_color=(0.91, 0.91, 0.91, 1), color=(0.55, 0.55, 0.55, 1)
        )
        save_btn = Button(
            text="Create", background_normal="",
            background_color=(0.298, 0.686, 0.522, 1), color=(1, 1, 1, 1)
        )
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title="", content=content,
            size_hint=(0.88, None), height=dp(300),
            separator_height=0
        )

        def save(*_):
            name   = name_input.text.strip()
            target = target_input.text.strip()
            if not name or not target:
                error_lbl.text = "All fields required."
                return
            try:
                t = float(target)
                if t <= 0: raise ValueError
            except ValueError:
                error_lbl.text = "Enter a valid target amount."
                return
            add_goal(self.user["id"], name, t)
            popup.dismiss()
            self.refresh()

        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=save)
        popup.open()

    def _delete_goal(self, goal_id):
        delete_goal(goal_id)
        self.refresh()
