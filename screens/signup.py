from kivy.uix.screenmanager import Screen
from kivy.app import App
from database.db import register_user

class SignupScreen(Screen):
    """
    Handles user registration UI and logic.
    Linked IDs: name_input, username_input, email_input, password_input, error_label
    """

    def do_signup(self):
        # 1. Extract and clean data from the UI
        name     = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        email    = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        # 2. UI-side Validation
        if not all([name, username, email, password]):
            self.ids.error_label.text = "All fields are required."
            return
            
        if len(password) < 6:
            self.ids.error_label.text = "Password is too short (min 6)."
            return

        # 3. Database Attempt
        # register_user should return (bool, result_data_or_error_msg)
        success, result = register_user(name, username, email, password)
        
        if success:
            self.ids.error_label.text = ""
            # Store session data in the main App class
            app = App.get_running_app()
            app.current_user = {
                "id": result, 
                "name": name, 
                "username": username,
                "email": email, 
                "currency": "USD", 
                "theme": "light", 
                "notifications": 1
            }
            # Success! Move to the next screen
            self.manager.current = "dashboard"
        else:
            # Show database error (e.g., 'Username already exists')
            self.ids.error_label.text = str(result)