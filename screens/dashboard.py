from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from datetime import datetime

from database.db import get_monthly_summary, get_goals
from components.navbar import BottomNavBar


class ClickableBox(ButtonBehavior, BoxLayout):
    pass


class DonutChart(Widget):
    def __init__(self, amount, total, arc_color, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount
        self.total = total
        self.arc_color = arc_color
        self.bind(size=self._draw, pos=self._draw)

    def _draw(self, *_):
        self.canvas.clear()

        if self.width <= 0 or self.height <= 0:
            return

        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        radius = min(self.width, self.height) / 2 - dp(6)
        thickness = radius * 0.35

        pct = 0
        if self.total > 0 and self.amount > 0:
            pct = min(self.amount / self.total, 1.0)

        with self.canvas:
            Color(0.85, 0.85, 0.85, 1)
            Line(circle=(cx, cy, radius - thickness / 2), width=thickness)

            if pct > 0:
                Color(*self.arc_color)
                Line(
                    circle=(cx, cy, radius - thickness / 2, 90, 90 + 360 * pct),
                    width=thickness,
                    cap="none"
                )


class DashboardScreen(Screen):

    def on_enter(self, *_):
        Clock.schedule_once(lambda dt: self.refresh(), 0)

    def refresh(self):
        app = App.get_running_app()
        user = app.current_user

        if not user:
            return

        summary = get_monthly_summary(user["id"])
        goals = get_goals(user["id"])

        income = summary["income"]
        expense = summary["expense"]
        month = datetime.now().strftime("%B")

        first_name = user["name"].split()[0] if user.get("name") else "User"

        self.ids.greeting_label.text = f"Hello, {first_name}!"
        self.ids.month_label.text = f"Month: {month}"
        self.ids.income_label.text = f"${income:,.2f}"
        self.ids.expense_label.text = f"${expense:,.2f}"

        max_val = max(income, expense, 1)

        income_box = self.ids.income_chart
        income_box.clear_widgets()
        income_box.add_widget(DonutChart(
            amount=income,
            total=max_val,
            arc_color=(0.18, 0.60, 0.40, 1),
            size_hint=(None, None),
            size=(dp(110), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        ))

        expense_box = self.ids.expense_chart
        expense_box.clear_widgets()
        expense_box.add_widget(DonutChart(
            amount=expense,
            total=max_val,
            arc_color=(0.85, 0.15, 0.15, 1),
            size_hint=(None, None),
            size=(dp(110), dp(110)),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        ))

        gc = self.ids.goals_container
        gc.clear_widgets()

        if goals:
            gc.add_widget(self._goal_bar(goals[0]))

            if len(goals) > 1:
                btn = Button(
                    text=f"+ {len(goals) - 1} more goals >",
                    font_size=dp(13),
                    color=(0.298, 0.686, 0.522, 1),
                    background_color=(0, 0, 0, 0),
                    background_normal="",
                    size_hint_y=None,
                    height=dp(32)
                )
                btn.bind(on_press=lambda *_: setattr(self.manager, "current", "goals"))
                gc.add_widget(btn)
        else:
            btn = Button(
                text="Set your first goal >",
                font_size=dp(13),
                color=(0.298, 0.686, 0.522, 1),
                background_color=(0, 0, 0, 0),
                background_normal="",
                size_hint_y=None,
                height=dp(36)
            )
            btn.bind(on_press=lambda *_: setattr(self.manager, "current", "goals"))
            gc.add_widget(btn)

        nav_box = self.ids.bottom_nav
        nav_box.clear_widgets()
        nav_box.add_widget(BottomNavBar(self.manager))

    def _goal_bar(self, goal):
        pct = min(goal["saved_amount"] / goal["target_amount"], 1.0) if goal["target_amount"] > 0 else 0

        container = ClickableBox(
            orientation="vertical",
            size_hint_y=None,
            height=dp(88),
            spacing=dp(6)
        )
        container.bind(on_press=lambda *_: setattr(self.manager, "current", "goals"))

        name_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(22)
        )

        name_row.add_widget(Label(
            text=goal["name"],
            font_size=dp(13),
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign="center",
            valign="middle"
        ))

        name_row.add_widget(Label(
            text=f"${goal['saved_amount']:,.0f} / ${goal['target_amount']:,.0f}",
            font_size=dp(12),
            color=(0.55, 0.55, 0.55, 1),
            halign="center",
            valign="middle"
        ))

        container.add_widget(name_row)

        bar = Widget(size_hint_y=None, height=dp(26))

        def draw_bar(w, *_):
            w.canvas.clear()
            with w.canvas:
                pad = dp(4)

                Color(0.098, 0.235, 0.204, 1)
                RoundedRectangle(radius=[dp(7)], size=w.size, pos=w.pos)

                Color(1, 1, 1, 1)
                RoundedRectangle(
                    radius=[dp(5)],
                    size=(w.width - pad * 2, w.height - pad * 2),
                    pos=(w.x + pad, w.y + pad)
                )

                fill_w = max((w.width - pad * 4) * pct, 0)

                Color(0.298, 0.686, 0.522, 1)
                RoundedRectangle(
                    radius=[dp(5)],
                    size=(fill_w, w.height - pad * 4),
                    pos=(w.x + pad * 2, w.y + pad * 2)
                )

        bar.bind(size=draw_bar, pos=draw_bar)
        container.add_widget(bar)

        container.add_widget(Label(
            text=f"{pct * 100:.0f}% complete",
            font_size=dp(11),
            color=(0.55, 0.55, 0.55, 1),
            size_hint_y=None,
            height=dp(18),
            halign="center",
            valign="middle"
        ))

        return container