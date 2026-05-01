import os
import sys
from kivy.core.text import LabelBase


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LabelBase.register(
    name="MaterialIcons",
    fn_regular=os.path.join(BASE_DIR, "fonts", "MaterialIcons-Regular.ttf")
)

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.config import Config
Config.set("graphics", "width",     "360")
Config.set("graphics", "height",    "720")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from database.db import init_db
from screens.login        import LoginScreen
from screens.signup       import SignupScreen
from screens.dashboard    import DashboardScreen
from screens.transactions import TransactionsScreen
from screens.goals        import GoalsScreen
from screens.settings     import SettingsScreen
from screens.statements import StatementsScreen
# Load all KV files
KV_DIR = os.path.join(os.path.dirname(__file__), "kv")
for kv_file in ["login", "signup", "dashboard", "transactions", "goals", "settings", "statements"]:
    Builder.load_file(os.path.join(KV_DIR, f"{kv_file}.kv"))


class MoneyMateApp(App):
    title        = "MoneyMate"
    current_user = None

    def build(self):
        init_db()
        sm = ScreenManager(transition=FadeTransition(duration=0.12))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TransactionsScreen(name="transactions"))
        sm.add_widget(GoalsScreen(name="goals"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(StatementsScreen(name="statements"))
        return sm


if __name__ == "__main__":
    MoneyMateApp().run()
