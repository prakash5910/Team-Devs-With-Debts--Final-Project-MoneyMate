from datetime import datetime, timedelta
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.clock import Clock
from database.db import get_goals, add_goal, update_goal_saved, delete_goal, get_monthly_summary
from kivy.lang import Builder

def show_add_goal(self):
    content = Builder.template("AddGoalContent")

    popup = Popup(
        title="New Goal",
        content=content,
        size_hint=(0.9, None),
        height="260dp"
    )
    popup.open()


class GoalCard(BoxLayout):
    goal_id = NumericProperty(0)
    name = StringProperty("")
    amount_text = StringProperty("")
    progress = NumericProperty(0)


class GoalsScreen(Screen):
    active_goal = None

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.refresh(), 0)

    def refresh(self):
        app = App.get_running_app()
        self.user = app.current_user
        if not self.user:
            self.manager.current = "login"
            return

        self.goals = get_goals(self.user["id"])
        self.ids.goal_list.clear_widgets()
        if not self.goals:
            self.ids.empty_label.text = "No goals yet. Tap '+ New' to create one!"
            return
        self.ids.empty_label.text = ""
        for goal in self.goals:
            pct = min(goal["saved_amount"] / goal["target_amount"], 1.0) if goal["target_amount"] else 0
            card = GoalCard(
                goal_id=goal["id"],
                name=goal["name"],
                amount_text=f"${goal['saved_amount']:,.2f} / ${goal['target_amount']:,.2f}",
                progress=pct * 100,
            )
            self.ids.goal_list.add_widget(card)

    def find_goal(self, goal_id):
        return next((g for g in self.goals if g["id"] == goal_id), None)

    def show_goal_detail(self, goal_id):
        goal = self.find_goal(goal_id)
        if not goal:
            return
        pct = (goal["saved_amount"] / goal["target_amount"] * 100) if goal["target_amount"] else 0
        summary = get_monthly_summary(self.user["id"])
        monthly_net = summary["income"] - summary["expense"]
        remaining = goal["target_amount"] - goal["saved_amount"]
        if remaining <= 0:
            eta = "Goal Reached!"
        elif monthly_net > 0:
            eta = (datetime.now() + timedelta(days=int((remaining / monthly_net) * 30))).strftime("%m / %d / %y")
        else:
            eta = "-- / -- / --"
        self.ids.detail_text.text = f"Goal: ${goal['target_amount']:,.2f}\nSaved: ${goal['saved_amount']:,.2f} ({pct:.2f}%)\nExpected Date: {eta}"
        self.detail_popup = Popup(title=goal["name"], content=self.ids.detail_content, size_hint=(0.85, None), height="280dp")
        self.ids.detail_holder.remove_widget(self.ids.detail_content)
        self.detail_popup.bind(on_dismiss=lambda *a: self.ids.detail_holder.add_widget(self.ids.detail_content))
        self.detail_popup.open()

    def show_add_savings(self, goal_id):
        self.active_goal = self.find_goal(goal_id)
        if not self.active_goal:
            return
        self.ids.savings_amount.text = ""
        self.ids.savings_error.text = ""
        self.savings_popup = Popup(title=f"Add to {self.active_goal['name']}", content=self.ids.savings_content, size_hint=(0.85, None), height="230dp")
        self.ids.savings_holder.remove_widget(self.ids.savings_content)
        self.savings_popup.bind(on_dismiss=lambda *a: self.ids.savings_holder.add_widget(self.ids.savings_content))
        self.savings_popup.open()

    def save_savings(self):
        try:
            amount = float(self.ids.savings_amount.text.strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.ids.savings_error.text = "Enter a valid amount."
            return
        update_goal_saved(self.active_goal["id"], amount)
        self.savings_popup.dismiss()
        self.refresh()

    def show_add_goal(self):
        self.ids.goal_name_input.text = ""
        self.ids.goal_target_input.text = ""
        self.ids.goal_error.text = ""
        self.add_popup = Popup(title="New Goal", content=self.ids.add_goal_content, size_hint=(0.9, None), height="260dp")
        self.ids.add_goal_holder.remove_widget(self.ids.add_goal_content)
        self.add_popup.bind(on_dismiss=lambda *a: self.ids.add_goal_holder.add_widget(self.ids.add_goal_content))
        self.add_popup.open()

    def save_goal(self):
        name = self.ids.goal_name_input.text.strip()
        try:
            target = float(self.ids.goal_target_input.text.strip())
            if target <= 0:
                raise ValueError
        except ValueError:
            self.ids.goal_error.text = "Enter a valid target amount."
            return
        if not name:
            self.ids.goal_error.text = "Enter a goal name."
            return
        add_goal(self.user["id"], name, target)
        self.add_popup.dismiss()
        self.refresh()

    def delete_goal_confirmed(self, goal_id):
        delete_goal(goal_id)
        self.refresh()
