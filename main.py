from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.core.window import Window

# 背景色
Window.clearcolor = get_color_from_hex("#0a0a1a")


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        self.opacity = 0

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
        )

        self.logo = Label(
            text="JS",
            font_size=dp(42),
            color=get_color_from_hex("#4fc3f7"),
            size_hint=(1, 0.55),
            halign="center",
            valign="middle",
        )

        self.en = Label(
            text="JS's STUDIO",
            font_size=dp(14),
            color=get_color_from_hex("#546e7a"),
            size_hint=(1, 0.15),
            halign="center",
        )

        self.foot = Label(
            text="Your world, your rules",
            font_size=dp(12),
            color=get_color_from_hex("#37474f"),
            size_hint=(1, 0.15),
            halign="center",
            opacity=0,
        )

        layout.add_widget(self.logo)
        layout.add_widget(self.en)
        layout.add_widget(self.foot)
        self.add_widget(layout)

        Clock.schedule_once(self.step1, 0.2)

    def step1(self, dt):
        Animation(opacity=1, duration=0.7).start(self)
        self.logo.font_size = dp(55)
        Animation(font_size=dp(42), duration=0.8, t="out_bounce").start(self.logo)
        Clock.schedule_once(self.step2, 1.0)

    def step2(self, dt):
        Animation(opacity=1, duration=0.6).start(self.foot)
        Clock.schedule_once(self.step3, 2.0)

    def step3(self, dt):
        anim = Animation(opacity=0, duration=0.6)
        anim.bind(on_complete=lambda *a: self._switch_to_main())
        anim.start(self)

    def _switch_to_main(self):
        if self.manager:
            self.manager.current = 'main'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(18),
            padding=(0, dp(40), 0, 0),
        )

        row1 = Label(
            text="WELCOME TO NEW WORLD",
            font_size=dp(22),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15),
            halign="center",
            valign="middle",
        )

        row2 = Label(
            text="Register or Log in",
            font_size=dp(22),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15),
            halign="center",
            valign="middle",
        )

        layout.add_widget(row1)
        layout.add_widget(row2)
        self.add_widget(layout)


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(MainScreen())
        sm.current = "splash"
        return sm


if __name__ == "__main__":
    MyApp().run()