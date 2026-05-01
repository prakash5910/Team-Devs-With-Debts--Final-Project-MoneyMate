from kivy.uix.screenmanager import Screen
from kivy.app import App

from database.db import update_user_info, update_user_settings
from components.navbar import BottomNavBar


class SettingsScreen(Screen):

    def on_enter(self, *_):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        self.user = app.current_user

        # Populate fields from saved user data
        self.ids.name_input.text     = self.user.get("name", "")
        self.ids.username_input.text = self.user.get("username", "")
        self.ids.email_input.text    = self.user.get("email", "")
        self.ids.password_input.text = ""

        self.ids.currency_spin.text  = self.user.get("currency", "USD")
        self.ids.theme_switch.active = self.user.get("theme", "light") == "dark"
        self.ids.notif_switch.active = bool(self.user.get("notifications", 1))
        self.ids.info_status.text    = ""

        # Bottom nav
        nav = self.ids.bottom_nav
        nav.clear_widgets()
        nav.add_widget(BottomNavBar(self.manager))

    def save_user_info(self):
        name     = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        email    = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not name or not username or not email:
            self.ids.info_status.text  = "Name, username and email cannot be empty."
            self.ids.info_status.color = (0.85, 0.15, 0.15, 1)
            return

        update_user_info(
            self.user["id"],
            name=name, username=username, email=email,
            password=password if password else None
        )
        app = App.get_running_app()
        app.current_user["name"]     = name
        app.current_user["username"] = username
        app.current_user["email"]    = email
        self.user = app.current_user

        self.ids.info_status.text  = "Changes saved!"
        self.ids.info_status.color = (0.298, 0.686, 0.522, 1)

    def on_currency(self, value):
        update_user_settings(self.user["id"], currency=value)
        App.get_running_app().current_user["currency"] = value

    def on_theme(self, active):
        theme = "dark" if active else "light"
        update_user_settings(self.user["id"], theme=theme)
        App.get_running_app().current_user["theme"] = theme

    def on_notif(self, active):
        update_user_settings(self.user["id"], notifications=int(active))
        App.get_running_app().current_user["notifications"] = int(active)
