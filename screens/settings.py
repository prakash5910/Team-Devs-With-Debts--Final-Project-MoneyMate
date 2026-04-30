from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock
from database.db import update_user_info, update_user_settings, get_user


class SettingsScreen(Screen):
    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.load_user(), 0)

    def load_user(self):
        app = App.get_running_app()
        self.user = app.current_user
        if not self.user:
            self.manager.current = "login"
            return
        self.user = get_user(self.user["id"])
        app.current_user = self.user
        self.ids.name_input.text = self.user.get("name", "")
        self.ids.username_input.text = self.user.get("username", "")
        self.ids.email_input.text = self.user.get("email", "")
        self.ids.password_input.text = ""
        self.ids.currency_spinner.text = self.user.get("currency", "USD")
        self.ids.theme_switch.active = self.user.get("theme", "light") == "dark"
        self.ids.notif_switch.active = bool(self.user.get("notifications", 1))
        self.ids.info_status.text = ""

    def save_user_info(self):
        name = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not name or not username or not email:
            self.ids.info_status.text = "Name, username and email cannot be empty."
            return

        update_user_info(
            self.user["id"],
            name=name,
            username=username,
            email=email,
            password=password if password else None,
        )
        App.get_running_app().current_user = get_user(self.user["id"])
        self.ids.info_status.text = "Saved successfully."

    def on_currency(self, value):
        if hasattr(self, "user") and self.user:
            update_user_settings(self.user["id"], currency=value)

    def on_theme(self, active):
        if hasattr(self, "user") and self.user:
            update_user_settings(self.user["id"], theme="dark" if active else "light")

    def on_notif(self, active):
        if hasattr(self, "user") and self.user:
            update_user_settings(self.user["id"], notifications=1 if active else 0)
