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
        cx, cy = self.center
        radius = min(self.width, self.height) / 2 - dp(5)
        thickness = dp(8)
        pct = min(self.amount / self.total, 1.0) if self.total > 0 else 0
        with self.canvas:
            Color(0.92, 0.92, 0.92, 1)
            Line(circle=(cx, cy, radius), width=thickness)
            if pct > 0:
                Color(*self.arc_color)
                Line(circle=(cx, cy, radius, 0, 360 * pct), width=thickness, cap="round")


class DashboardScreen(Screen):
    def on_enter(self, *_):
        Clock.schedule_once(lambda dt: self.refresh(), 0.1)

    def refresh(self):
        app = App.get_running_app()
        user = getattr(app, 'current_user', None)
        if not user:
            return

        summary = get_monthly_summary(user["id"])
        goals = get_goals(user["id"])

        # 1. Header
        first_name = user["name"].split()[0] if user.get("name") else "User"
        self.ids.greeting_label.text = f"Hi, {first_name}!"
        self.ids.month_label.text = datetime.now().strftime("%B Summary")
        self.ids.income_label.text = f"${summary['income']:,.2f}"
        self.ids.expense_label.text = f"${summary['expense']:,.2f}"

        # 2. Charts
        max_val = max(summary["income"], summary["expense"], 1)
        self._update_chart(self.ids.income_chart, summary["income"], max_val, (0.18, 0.60, 0.40, 1))
        self._update_chart(self.ids.expense_chart, summary["expense"], max_val, (0.85, 0.15, 0.15, 1))

        # 3. Goals
        gc = self.ids.goals_container
        gc.clear_widgets()

        if goals:
            for goal in goals:
                gc.add_widget(self._create_goal_item(goal))
        else:
            btn = Button(
                text="Set your first goal +",
                size_hint_y=None,
                height=dp(45),
                background_color=(0, 0, 0, 0),
                color=(0.298, 0.686, 0.522, 1)
            )
            btn.bind(on_press=lambda *_: setattr(self.manager, "current", "goals"))
            gc.add_widget(btn)

        # 4. Bottom Nav
        self.ids.bottom_nav.clear_widgets()
        self.ids.bottom_nav.add_widget(BottomNavBar(self.manager))

    def _update_chart(self, parent, amt, total, color):
        parent.clear_widgets()
        parent.add_widget(DonutChart(
            amount=amt,
            total=total,
            arc_color=color,
            size_hint=(None, None),
            size=(dp(70), dp(70))
        ))

    def _create_goal_item(self, goal):
        target = goal.get("target_amount", 1)
        saved = goal.get("saved_amount", 0)
        pct = min(saved / target, 1.0)

        card = ClickableBox(
            orientation="vertical",
            size_hint_y=None,
            height=dp(95),
            padding=dp(15),
            spacing=dp(8)
        )

        with card.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
            Color(0, 0, 0, 0.05)
            Line(rounded_rectangle=[card.x, card.y, card.width, card.height, dp(12)], width=1.1)

        card.bind(pos=self._update_card_graphics, size=self._update_card_graphics)
        card.bind(on_press=lambda *_: setattr(self.manager, "current", "goals"))

        # --- Row 1 (FIXED) ---
        row = BoxLayout(size_hint_y=None, height=dp(20))

        name_lbl = Label(
            text=goal["name"],
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.6
        )
        name_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        amount_lbl = Label(
            text=f"${saved:,.0f}/${target:,.0f}",
            font_size=dp(11),
            color=(0.4, 0.4, 0.4, 1),
            halign="right",
            valign="middle",
            size_hint_x=0.4
        )
        amount_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        row.add_widget(name_lbl)
        row.add_widget(amount_lbl)
        card.add_widget(row)

        # --- Row 2 (Progress Bar) ---
        bar = Widget(size_hint_y=None, height=dp(10))

        def draw_bar(w, *_):
            w.canvas.clear()
            with w.canvas:
                Color(0.93, 0.93, 0.93, 1)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(5)])
                Color(0.298, 0.686, 0.522, 1)
                RoundedRectangle(pos=w.pos, size=(w.width * pct, w.height), radius=[dp(5)])

        bar.bind(pos=draw_bar, size=draw_bar)
        card.add_widget(bar)

        # --- Row 3 (FIXED) ---
        pct_lbl = Label(
            text=f"{pct*100:.1f}% complete",
            font_size=dp(10),
            color=(0.5, 0.5, 0.5, 1),
            halign="left",
            valign="middle"
        )
        pct_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        card.add_widget(pct_lbl)

        return card

    def _update_card_graphics(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(12)])
            Color(0, 0, 0, 0.05)
            Line(
                rounded_rectangle=[instance.x, instance.y, instance.width, instance.height, dp(12)],
                width=1.1
            )