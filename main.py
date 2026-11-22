from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.core.window import Window

import json
import os

# 窗口背景色（深色主题）
Window.clearcolor = get_color_from_hex("#0a0a1a")

# 数据文件夹
DATA_DIR = "data"
TODO_FILE = os.path.join(DATA_DIR, "todos.json")
PASS_FILE = os.path.join(DATA_DIR, "passwords.json")

# 如果data文件夹不存在就创建
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ========== 读取和保存待办 ==========
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

# ========== 读取和保存密码 ==========
def load_passwords():
    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, "r") as f:
            return json.load(f)
    return []

def save_passwords(passwords):
    with open(PASS_FILE, "w") as f:
        json.dump(passwords, f, indent=2)

# ========== 闪屏页面 ==========
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        self.opacity = 0

        layout = BoxLayout(orientation="vertical", spacing=dp(10))

        self.logo = Label(
            text="JS",
            font_size=dp(42),
            color=get_color_from_hex("#4fc3f7"),
            size_hint=(1, 0.55),
            halign="center",
            valign="middle"
        )

        self.en = Label(
            text="JS's STUDIO",
            font_size=dp(14),
            color=get_color_from_hex("#546e7a"),
            size_hint=(1, 0.15),
            halign="center"
        )

        self.foot = Label(
            text="Your world, your rules",
            font_size=dp(12),
            color=get_color_from_hex("#37474f"),
            size_hint=(1, 0.15),
            halign="center",
            opacity=0
        )

        layout.add_widget(self.logo)
        layout.add_widget(self.en)
        layout.add_widget(self.foot)
        self.add_widget(layout)

        Clock.schedule_once(self.step1, 0.2)

    def step1(self, dt):
        Animation(opacity=1, duration=0.7).start(self)
        Animation(font_size=dp(42), duration=0.8, t="out_bounce").start(self.logo)
        Clock.schedule_once(self.step2, 1.0)

    def step2(self, dt):
        Animation(opacity=1, duration=0.6).start(self.foot)
        Clock.schedule_once(self.step3, 2.0)

    def step3(self, dt):
        anim = Animation(opacity=0, duration=0.6)
        anim.bind(on_complete=lambda *a: self.go_main())
        anim.start(self)

    def go_main(self):
        if self.manager:
            self.manager.current = 'main'

# ========== 主菜单页面 ==========
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"

        layout = BoxLayout(orientation="vertical", spacing=dp(18), padding=(dp(30), dp(60), dp(30), dp(30)))

        # 标题
        layout.add_widget(Label(
            text="[b]JS's STUDIO[/b]",
            font_size=dp(28),
            color=get_color_from_hex("#4fc3f7"),
            size_hint=(1, 0.2),
            markup=True,
            halign="center"
        ))

        # 待办按钮
        todo_btn = Button(
            text="待办清单",
            font_size=dp(20),
            background_color=get_color_from_hex("#1a3a5c"),
            size_hint=(1, 0.15)
        )
        todo_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'todo'))
        layout.add_widget(todo_btn)

        # 密码本按钮
        pass_btn = Button(
            text="密码本",
            font_size=dp(20),
            background_color=get_color_from_hex("#1a3a5c"),
            size_hint=(1, 0.15)
        )
        pass_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'password'))
        layout.add_widget(pass_btn)

        # 退出按钮
        exit_btn = Button(
            text="退出",
            font_size=dp(16),
            background_color=get_color_from_hex("#37474f"),
            size_hint=(1, 0.1)
        )
        exit_btn.bind(on_press=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)

        self.add_widget(layout)

# ========== 待办清单页面 ==========
class TodoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "todo"
        self.todos = load_todos()

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))

        # 标题
        layout.add_widget(Label(
            text="[b]待办清单[/b]",
            font_size=dp(24),
            color=get_color_from_hex("#4fc3f7"),
            size_hint=(1, 0.08),
            markup=True,
            halign="center"
        ))

        # 输入栏
        input_row = BoxLayout(size_hint=(1, 0.08), spacing=dp(8))
        self.todo_input = TextInput(
            hint_text="输入新任务...",
            multiline=False,
            background_color=get_color_from_hex("#1a1a2e"),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        add_btn = Button(
            text="添加",
            size_hint=(0.25, 1),
            background_color=get_color_from_hex("#4fc3f7")
        )
        add_btn.bind(on_press=self.add_todo)
        input_row.add_widget(self.todo_input)
        input_row.add_widget(add_btn)
        layout.add_widget(input_row)

        # 滚动列表
        scroll = ScrollView(size_hint=(1, 0.74))
        self.todo_list = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.todo_list.bind(minimum_height=self.todo_list.setter('height'))
        scroll.add_widget(self.todo_list)
        layout.add_widget(scroll)

        # 返回按钮
        back_btn = Button(
            text="返回主菜单",
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#37474f")
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        self.add_widget(layout)
        self.refresh_list()

    def add_todo(self, instance):
        text = self.todo_input.text.strip()
        if text:
            self.todos.append({"text": text, "done": False})
            self.todo_input.text = ""
            save_todos(self.todos)
            self.refresh_list()

    def toggle_todo(self, index):
        self.todos[index]["done"] = not self.todos[index]["done"]
        save_todos(self.todos)
        self.refresh_list()

    def delete_todo(self, index):
        self.todos.pop(index)
        save_todos(self.todos)
        self.refresh_list()

    def refresh_list(self):
        self.todo_list.clear_widgets()
        for i, todo in enumerate(self.todos):
            row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))

            # 任务按钮（点击切换完成状态）
            btn = Button(
                text=f"{'[s]' if todo['done'] else ''}{todo['text']}{'[/s]' if todo['done'] else ''}",
                background_color=get_color_from_hex("#1a1a2e"),
                markup=True
            )
            btn.bind(on_press=lambda x, i=i: self.toggle_todo(i))

            # 删除按钮
            del_btn = Button(
                text="删除",
                size_hint=(0.2, 1),
                background_color=get_color_from_hex("#e53935")
            )
            del_btn.bind(on_press=lambda x, i=i: self.delete_todo(i))

            row.add_widget(btn)
            row.add_widget(del_btn)
            self.todo_list.add_widget(row)

# ========== 密码本页面 ==========
class PasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "password"
        self.passwords = load_passwords()

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))

        # 标题
        layout.add_widget(Label(
            text="[b]密码本[/b]",
            font_size=dp(24),
            color=get_color_from_hex("#4fc3f7"),
            size_hint=(1, 0.06),
            markup=True,
            halign="center"
        ))

        # 添加表单
        form = GridLayout(cols=2, size_hint=(1, 0.22), spacing=dp(6))
        self.site_input = TextInput(
            hint_text="网站/应用名称",
            background_color=get_color_from_hex("#1a1a2e"),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.user_input = TextInput(
            hint_text="用户名/账号",
            background_color=get_color_from_hex("#1a1a2e"),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.pass_input = TextInput(
            hint_text="密码",
            password=True,
            background_color=get_color_from_hex("#1a1a2e"),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        add_btn = Button(text="保存", background_color=get_color_from_hex("#4fc3f7"))
        add_btn.bind(on_press=self.add_password)

        form.add_widget(Label(text="网站:", color=(1, 1, 1, 1)))
        form.add_widget(self.site_input)
        form.add_widget(Label(text="账号:", color=(1, 1, 1, 1)))
        form.add_widget(self.user_input)
        form.add_widget(Label(text="密码:", color=(1, 1, 1, 1)))
        form.add_widget(self.pass_input)
        form.add_widget(Label(text=""))
        form.add_widget(add_btn)
        layout.add_widget(form)

        # 密码列表
        scroll = ScrollView(size_hint=(1, 0.62))
        self.pass_list = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.pass_list.bind(minimum_height=self.pass_list.setter('height'))
        scroll.add_widget(self.pass_list)
        layout.add_widget(scroll)

        # 返回按钮
        back_btn = Button(
            text="返回主菜单",
            size_hint=(1, 0.1),
            background_color=get_color_from_hex("#37474f")
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        self.add_widget(layout)
        self.refresh_list()

    def add_password(self, instance):
        site = self.site_input.text.strip()
        user = self.user_input.text.strip()
        pwd = self.pass_input.text.strip()
        if site and pwd:
            self.passwords.append({"site": site, "user": user, "password": pwd})
            self.site_input.text = ""
            self.user_input.text = ""
            self.pass_input.text = ""
            save_passwords(self.passwords)
            self.refresh_list()

    def delete_password(self, index):
        self.passwords.pop(index)
        save_passwords(self.passwords)
        self.refresh_list()

    def show_password(self, index):
        entry = self.passwords[index]
        popup = Popup(title=entry["site"], size_hint=(0.85, 0.45))
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text=f"账号: {entry['user']}", color=(1, 1, 1, 1)))
        content.add_widget(Label(text=f"密码: {entry['password']}", color=(1, 1, 1, 1)))
        close_btn = Button(text="关闭", background_color=get_color_from_hex("#37474f"))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.content = content
        popup.open()

    def refresh_list(self):
        self.pass_list.clear_widgets()
        for i, entry in enumerate(self.passwords):
            row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
            btn = Button(
                text=f"{entry['site']} - {entry['user']}",
                background_color=get_color_from_hex("#1a1a2e")
            )
            btn.bind(on_press=lambda x, i=i: self.show_password(i))
            del_btn = Button(
                text="删除",
                size_hint=(0.2, 1),
                background_color=get_color_from_hex("#e53935")
            )
            del_btn.bind(on_press=lambda x, i=i: self.delete_password(i))
            row.add_widget(btn)
            row.add_widget(del_btn)
            self.pass_list.add_widget(row)

# ========== App主类 ==========
class MyApp(App):
    def build(self):
        self.title = "JS's STUDIO"
        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(MainScreen())
        sm.add_widget(TodoScreen())
        sm.add_widget(PasswordScreen())
        sm.current = "splash"
        return sm

if __name__ == "__main__":
    MyApp().run()