import os

from kivy.app import App
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.text import LabelBase


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "..", "fonts", "MaterialIcons-Regular.ttf")

LabelBase.register(
    name="MaterialIcons",
    fn_regular=FONT_PATH
)


class CircleIcon(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(44), dp(44))
        self.font_name = "MaterialIcons"
        self.font_size = dp(30)
        self.color = (0, 0, 0, 1)
        self.halign = "center"
        self.valign = "middle"

        with self.canvas.before:
            Color(0.94, 0.94, 0.94, 1)
            self.circle = Ellipse(size=self.size, pos=self.pos)

        self.bind(size=self._update, pos=self._update)

    def _update(self, *_):
        self.circle.size = self.size
        self.circle.pos = self.pos
        self.text_size = self.size


class NavItem(ButtonBehavior, BoxLayout):
    def __init__(self, icon_code, label_text, callback, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.size_hint = (1, 1)
        self.padding = [0, dp(6), 0, dp(4)]
        self.spacing = dp(2)
        self.callback = callback

        icon = CircleIcon(text=icon_code)
        icon_box = BoxLayout(size_hint_y=None, height=dp(46))
        icon_box.add_widget(BoxLayout())
        icon_box.add_widget(icon)
        icon_box.add_widget(BoxLayout())

        label = Label(
            text=label_text,
            font_size=dp(11),
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(18),
        )
        label.bind(size=lambda w, v: setattr(w, "text_size", w.size))

        self.add_widget(icon_box)
        self.add_widget(label)

    def on_press(self):
        self.callback()


class BottomNavBar(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(82)
        self.sm = screen_manager

        with self.canvas.before:
            Color(0.38, 0.74, 0.56, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        self.add_widget(NavItem("\ue853", "Account", self._go_account))
        self.add_widget(NavItem("\ue0cb", "Contact Us", self._go_contact))
        self.add_widget(NavItem("\ue879", "Log Out", self._do_logout))

    def _go_account(self):
        self.sm.current = "settings"

    def _go_contact(self):
        pass

    def _do_logout(self):
        App.get_running_app().current_user = None
        self.sm.current = "login"

    def _update_bg(self, *_):
        self.bg.size = self.size
        self.bg.pos = self.pos