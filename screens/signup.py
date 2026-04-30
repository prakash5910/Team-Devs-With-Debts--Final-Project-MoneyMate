from kivy.uix.screenmanager import Screen
from kivy.app import App
from database.db import register_user


class SignupScreen(Screen):
    def do_signup(self):
        name = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not all([name, username, email, password]):
            self.ids.error_label.text = "Please fill in all fields."
            return
        if len(password) < 6:
            self.ids.error_label.text = "Password must be at least 6 characters."
            return

        success, result = register_user(name, username, email, password)
        if success:
            App.get_running_app().current_user = {
                "id": result,
                "name": name,
                "username": username,
                "email": email,
                "currency": "USD",
                "theme": "light",
                "notifications": 1,
            }
            self.ids.error_label.text = ""
            self.manager.current = "dashboard"
        else:
            self.ids.error_label.text = str(result)
