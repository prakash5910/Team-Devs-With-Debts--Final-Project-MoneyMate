from kivy.uix.screenmanager import Screen
from kivy.app import App
from database.db import login_user


class LoginScreen(Screen):
    # ids bound automatically by KV: username_input, password_input, error_label

    def do_login(self):
        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not username or not password:
            self.ids.error_label.text = "Please fill in all fields."
            return

        user = login_user(username, password)
        if user:
            self.ids.error_label.text = ""
            App.get_running_app().current_user = user
            self.manager.current = "dashboard"
        else:
            self.ids.error_label.text = "Invalid username or password."
