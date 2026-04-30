from kivy.uix.boxlayout import BoxLayout
from kivy.app import App


class BottomNavBar(BoxLayout):
    def go_account(self):
        self.screen_manager.current = "settings"

    def go_contact(self):
        # Placeholder until a Contact screen is added.
        pass

    def do_logout(self):
        App.get_running_app().current_user = None
        self.screen_manager.current = "login"
