import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.config import Config
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "720")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from database.db import init_db
from screens.login import LoginScreen
from screens.signup import SignupScreen
from screens.dashboard import DashboardScreen
from screens.transactions import TransactionsScreen
from screens.goals import GoalsScreen
from screens.settings import SettingsScreen

KV_FILES = [
    "components/navbar.kv",
    "screens/login.kv",
    "screens/signup.kv",
    "screens/dashboard.kv",
    "screens/transactions.kv",
    "screens/goals.kv",
    "screens/settings.kv",
]


class MoneyMateApp(App):
    title = "MoneyMate"
    current_user = None

    def build(self):
        init_db()
        base = os.path.dirname(__file__)
        for kv in KV_FILES:
            Builder.load_file(os.path.join(base, kv))

        sm = ScreenManager(transition=FadeTransition(duration=0.12))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TransactionsScreen(name="transactions"))
        sm.add_widget(GoalsScreen(name="goals"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == "__main__":
    MoneyMateApp().run()
