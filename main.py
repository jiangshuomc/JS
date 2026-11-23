"""
JS Studio — Memo / Diary / Vault
Kivy app for Android.  Pure-English UI, local-JSON storage.
"""
import os
import json
import hashlib
import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.storage.jsonstore import JsonStore

# ─────────────────────────── constants ───────────────────────────
STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(STORAGE_DIR, exist_ok=True)

BG        = get_color_from_hex("#0a0a1a")
CARD_BG   = get_color_from_hex("#111827")
ACCENT    = get_color_from_hex("#4fc3f7")
ACCENT2   = get_color_from_hex("#7c4dff")
DIM       = get_color_from_hex("#546e7a")
DIMMER    = get_color_from_hex("#37474f")
WHITE     = (1, 1, 1, 1)
RED       = get_color_from_hex("#ff5252")
GREEN     = get_color_from_hex("#69f0ae")
YELLOW    = get_color_from_hex("#ffd740")
BORDER    = get_color_from_hex("#1e293b")

Window.clearcolor = BG

# ─────────────────────────── helpers ─────────────────────────────

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _today() -> str:
    return datetime.date.today().isoformat()


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M")


class Card(BoxLayout):
    """Rounded-card container."""
    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", dp(8))
        kwargs.setdefault("padding", dp(14))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*CARD_BG)
            self._rect = RoundedRectangle(radius=[dp(12)])
            Color(*BORDER)
            self._line = Line(rounded_rectangle=(0, 0, 1, 1, dp(12)), width=1)
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._line.rounded_rectangle = (*self.pos, *self.size, dp(12))


class GlowLabel(Label):
    """Label with optional accent colour & size helpers."""
    pass


class GradientButton(Button):
    """Flat minimal button with rounded rect."""
    def __init__(self, bg_color=ACCENT, txt_color=BG, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(46))
        kwargs.setdefault("font_size", sp(15))
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        self.color = txt_color
        self._bg = bg_color
        with self.canvas.before:
            Color(*self._bg)
            self._rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size


class NavBar(BoxLayout):
    """Bottom nav bar (icon-free, simple text)."""
    def __init__(self, screen_manager, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(52))
        kwargs.setdefault("spacing", 0)
        super().__init__(**kwargs)
        self.sm = screen_manager
        items = [("MEMO", "memo"), ("DIARY", "diary"), ("VAULT", "vault")]
        for label, name in items:
            btn = Button(
                text=label,
                background_normal="", background_down="",
                background_color=(0, 0, 0, 0),
                color=DIM,
                font_size=sp(12),
                bold=True,
            )
            btn.bind(on_release=lambda b, n=name: self._go(n))
            self.add_widget(btn)
        # top divider line
        with self.canvas.after:
            Color(*BORDER)
            self._div = Line(points=[0, self.height, self.width, self.height], width=1)
        self.bind(size=self._upd)

    def _upd(self, *a):
        self._div.points = [0, self.height, self.width, self.height]

    def _go(self, name):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = name


# ═══════════════════════════ Splash ══════════════════════════════

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "splash"
        self.opacity = 0
        layout = BoxLayout(orientation="vertical", spacing=dp(10))
        self.logo = Label(
            text="JS", font_size=dp(42),
            color=ACCENT, size_hint=(1, 0.55),
            halign="center", valign="middle",
        )
        self.en = Label(
            text="JS STUDIO", font_size=dp(14),
            color=DIM, size_hint=(1, 0.15), halign="center",
        )
        self.foot = Label(
            text="Your world, your rules", font_size=dp(12),
            color=DIMMER, size_hint=(1, 0.15), halign="center", opacity=0,
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
        anim.bind(on_complete=lambda *a: self._switch())
        anim.start(self)

    def _switch(self):
        if self.manager:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "home"


# ═══════════════════════════ Home ════════════════════════════════

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        root = BoxLayout(orientation="vertical", spacing=dp(16), padding=(dp(20), dp(50), dp(20), dp(20)))

        # header
        hdr = Label(
            text="JS STUDIO", font_size=sp(26), color=WHITE,
            size_hint=(1, 0.12), halign="center", valign="middle",
            bold=True,
        )
        sub = Label(
            text="Personal Suite", font_size=sp(13), color=DIM,
            size_hint=(1, 0.06), halign="center",
        )
        root.add_widget(hdr)
        root.add_widget(sub)

        # spacer
        root.add_widget(Label(size_hint=(1, 0.05)))

        # menu cards
        for icon, title, desc, target, col in [
            ("✦", "MEMO",  "Quick notes & reminders", "memo",   ACCENT),
            ("✦", "DIARY", "Daily journal",           "diary",  GREEN),
            ("✦", "VAULT", "Encrypted passwords",      "vault",  ACCENT2),
        ]:
            card = Card(size_hint=(1, 0.2))
            row = BoxLayout(orientation="horizontal", spacing=dp(12))
            icon_lbl = Label(text=icon, font_size=sp(24), color=col,
                             size_hint=(0.2, 1), halign="center", valign="middle")
            txt_box = BoxLayout(orientation="vertical", spacing=dp(2))
            txt_box.add_widget(Label(text=title, font_size=sp(18), color=WHITE,
                                     halign="left", valign="middle", bold=True))
            txt_box.add_widget(Label(text=desc, font_size=sp(11), color=DIM,
                                     halign="left", valign="middle"))
            row.add_widget(icon_lbl)
            row.add_widget(txt_box)
            card.add_widget(row)
            card.bind(on_touch_down=lambda inst, touch, t=target: self._go(inst, touch, t))
            root.add_widget(card)

        root.add_widget(Label(size_hint=(1, 0.08)))
        foot = Label(text="v1.0  ·  Local Storage", font_size=sp(10), color=DIMMER,
                     size_hint=(1, 0.04), halign="center")
        root.add_widget(foot)

        self.add_widget(root)

    def _go(self, inst, touch, target):
        if inst.collide_point(*touch.pos):
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = target


# ═══════════════════════════ Memo ════════════════════════════════

MEMO_FILE = os.path.join(STORAGE_DIR, "memos.json")


class MemoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "memo"
        self._store = JsonStore(MEMO_FILE)
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(10), padding=(dp(16), dp(16), dp(16), dp(8)))

        # header
        hdr = BoxLayout(orientation="horizontal", size_hint=(1, 0.07))
        hdr.add_widget(Label(text="MEMO", font_size=sp(22), color=WHITE, bold=True,
                             halign="left", valign="middle"))
        add_btn = GradientButton(text="+", size_hint=(None, 1), width=dp(44),
                                 font_size=sp(22))
        add_btn.bind(on_release=lambda b: self._add_dialog())
        hdr.add_widget(add_btn)
        root.add_widget(hdr)

        # list
        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        root.add_widget(scroll)

        # nav
        root.add_widget(NavBar(self.manager))
        self.add_widget(root)
        self._refresh()

    def _refresh(self):
        self.list_box.clear_widgets()
        memos = self._load()
        if not memos:
            self.list_box.add_widget(Label(
                text="No memos yet. Tap + to add.", font_size=sp(13), color=DIMMER,
                size_hint=(1, None), height=dp(50), halign="center", valign="middle"))
            return
        for m in memos:
            self.list_box.add_widget(self._item(m))

    def _item(self, m):
        card = Card(size_hint=(1, None), height=dp(64))
        row = BoxLayout(orientation="horizontal", spacing=dp(10))
        # checkbox
        chk = Label(
            text="✓" if m["done"] else "○",
            font_size=sp(20),
            color=GREEN if m["done"] else DIM,
            size_hint=(None, 1), width=dp(36),
            halign="center", valign="middle",
        )
        chk.bind(on_touch_down=lambda inst, touch, mid=m["id"]: self._toggle(inst, touch, mid))
        row.add_widget(chk)
        # text
        txt_box = BoxLayout(orientation="vertical", spacing=dp(2))
        t = m["text"]
        if m["done"]:
            t = "[s]" + t + "[/s]"
        txt_box.add_widget(Label(text=t, font_size=sp(14),
                                 color=DIM if m["done"] else WHITE,
                                 markup=True, halign="left", valign="middle"))
        txt_box.add_widget(Label(text=m.get("date", ""), font_size=sp(10), color=DIMMER,
                                 halign="left"))
        row.add_widget(txt_box)
        # delete
        del_btn = Label(text="✕", font_size=sp(16), color=RED,
                        size_hint=(None, 1), width=dp(36),
                        halign="center", valign="middle")
        del_btn.bind(on_touch_down=lambda inst, touch, mid=m["id"]: self._del(inst, touch, mid))
        row.add_widget(del_btn)
        card.add_widget(row)
        return card

    def _toggle(self, inst, touch, mid):
        if not inst.collide_point(*touch.pos):
            return
        memos = self._load()
        for m in memos:
            if m["id"] == mid:
                m["done"] = not m["done"]
                break
        self._save(memos)
        self._refresh()

    def _del(self, inst, touch, mid):
        if not inst.collide_point(*touch.pos):
            return
        memos = [m for m in self._load() if m["id"] != mid]
        self._save(memos)
        self._refresh()

    def _add_dialog(self):
        ti = TextInput(
            hint_text="Type your memo...", multiline=True,
            font_size=sp(14), foreground_color=WHITE,
            background_color=CARD_BG, cursor_color=ACCENT,
            size_hint=(1, None), height=dp(100),
            padding=(dp(10), dp(10)),
        )
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        content.add_widget(ti)
        btn_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=dp(42))
        ok = GradientButton(text="SAVE", size_hint=(1, 1))
        cancel = GradientButton(text="CANCEL", bg_color=BORDER, txt_color=WHITE, size_hint=(1, 1))
        content.add_widget(btn_row)
        btn_row.add_widget(cancel)
        btn_row.add_widget(ok)
        popup = Popup(title="New Memo", content=content, size_hint=(0.85, 0.4),
                      background_color=get_color_from_hex("#0d1117"),
                      title_color=WHITE, separator_color=ACCENT)
        ok.bind(on_release=lambda b: self._save_memo(ti.text, popup))
        cancel.bind(on_release=popup.dismiss)
        popup.open()

    def _save_memo(self, text, popup):
        text = text.strip()
        if not text:
            return
        memos = self._load()
        memos.insert(0, {
            "id": int(datetime.datetime.now().timestamp() * 1000),
            "text": text,
            "done": False,
            "date": f"{_today()} {_now()}",
        })
        self._save(memos)
        self._refresh()
        popup.dismiss()

    def _load(self):
        try:
            with open(MEMO_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self, memos):
        with open(MEMO_FILE, "w") as f:
            json.dump(memos, f, ensure_ascii=False, indent=2)


# ═══════════════════════════ Diary ═══════════════════════════════

DIARY_FILE = os.path.join(STORAGE_DIR, "diary.json")


class DiaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "diary"
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(10), padding=(dp(16), dp(16), dp(16), dp(8)))

        hdr = BoxLayout(orientation="horizontal", size_hint=(1, 0.07))
        hdr.add_widget(Label(text="DIARY", font_size=sp(22), color=WHITE, bold=True,
                             halign="left", valign="middle"))
        date_lbl = Label(text=_today(), font_size=sp(12), color=ACCENT,
                         halign="right", valign="middle")
        hdr.add_widget(date_lbl)
        root.add_widget(hdr)

        # today's entry or prompt
        entry = self._today_entry()
        if entry:
            card = Card(size_hint=(1, 0.65))
            card.add_widget(Label(text=entry["text"], font_size=sp(14), color=WHITE,
                                  halign="left", valign="top", markup=True))
            root.add_widget(card)
            edit_btn = GradientButton(text="EDIT TODAY", size_hint=(1, None), height=dp(42))
            edit_btn.bind(on_release=lambda b: self._edit_dialog(entry))
            root.add_widget(edit_btn)
        else:
            empty = BoxLayout(orientation="vertical", spacing=dp(10), size_hint=(1, 0.65))
            empty.add_widget(Label(text="No entry today.", font_size=sp(16), color=DIM))
            empty.add_widget(Label(text="Write something ✎", font_size=sp(13), color=DIMMER))
            root.add_widget(empty)
            write_btn = GradientButton(text="WRITE", bg_color=GREEN, size_hint=(1, None), height=dp(42))
            write_btn.bind(on_release=lambda b: self._edit_dialog(None))
            root.add_widget(write_btn)

        # history
        hist_btn = GradientButton(text="HISTORY", bg_color=BORDER, txt_color=WHITE,
                                  size_hint=(1, None), height=dp(38))
        hist_btn.bind(on_release=lambda b: self._history())
        root.add_widget(hist_btn)

        root.add_widget(NavBar(self.manager))
        self.add_widget(root)

    def _edit_dialog(self, existing):
        ti = TextInput(
            text=existing["text"] if existing else "",
            hint_text="Dear diary...", multiline=True,
            font_size=sp(14), foreground_color=WHITE,
            background_color=CARD_BG, cursor_color=GREEN,
            size_hint=(1, None), height=dp(180),
            padding=(dp(10), dp(10)),
        )
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        content.add_widget(ti)
        btn_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=dp(42))
        ok = GradientButton(text="SAVE", bg_color=GREEN)
        cancel = GradientButton(text="CANCEL", bg_color=BORDER, txt_color=WHITE)
        btn_row.add_widget(cancel)
        btn_row.add_widget(ok)
        content.add_widget(btn_row)
        popup = Popup(title=_today(), content=content, size_hint=(0.9, 0.55),
                      background_color=get_color_from_hex("#0d1117"),
                      title_color=WHITE, separator_color=GREEN)
        ok.bind(on_release=lambda b: self._save_entry(ti.text, popup))
        cancel.bind(on_release=popup.dismiss)
        popup.open()

    def _save_entry(self, text, popup):
        text = text.strip()
        if not text:
            return
        entries = self._load()
        today = _today()
        found = False
        for e in entries:
            if e["date"] == today:
                e["text"] = text
                e["time"] = _now()
                found = True
                break
        if not found:
            entries.insert(0, {"date": today, "text": text, "time": _now()})
        self._save(entries)
        self._build()
        popup.dismiss()

    def _history(self):
        entries = self._load()
        if not entries:
            return
        scroll = ScrollView()
        box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))
        for e in entries:
            card = Card(size_hint=(1, None), height=dp(80))
            col = BoxLayout(orientation="vertical", spacing=dp(4))
            col.add_widget(Label(text=f"{e['date']}  {e.get('time', '')}",
                                 font_size=sp(11), color=ACCENT, halign="left"))
            preview = e["text"][:80] + ("..." if len(e["text"]) > 80 else "")
            col.add_widget(Label(text=preview, font_size=sp(13), color=WHITE,
                                 halign="left", valign="top"))
            card.add_widget(col)
            box.add_widget(card)
        scroll.add_widget(box)
        popup = Popup(title="History", content=scroll, size_hint=(0.9, 0.7),
                      background_color=get_color_from_hex("#0d1117"),
                      title_color=WHITE, separator_color=GREEN)
        popup.open()

    def _today_entry(self):
        entries = self._load()
        today = _today()
        for e in entries:
            if e["date"] == today:
                return e
        return None

    def _load(self):
        try:
            with open(DIARY_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self, entries):
        with open(DIARY_FILE, "w") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)


# ═══════════════════════════ Vault ═══════════════════════════════

VAULT_FILE = os.path.join(STORAGE_DIR, "vault.json")
CONFIG_FILE = os.path.join(STORAGE_DIR, "config.json")


class VaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "vault"
        self._unlocked = False
        self._build()

    def on_enter(self):
        if not self._unlocked:
            self._lock_screen()

    # ─── lock UI ───
    def _lock_screen(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(16), padding=(dp(30), dp(60), dp(30), dp(30)))

        root.add_widget(Label(text="🔒", font_size=sp(48), size_hint=(1, 0.25), halign="center"))
        root.add_widget(Label(text="VAULT LOCKED", font_size=sp(20), color=WHITE,
                              size_hint=(1, 0.08), halign="center", bold=True))

        has_pw = self._get_hash() is not None
        hint = "Enter password" if has_pw else "Set a new password"
        self.pw_input = TextInput(
            hint_text=hint, password=True, multiline=False,
            font_size=sp(14), foreground_color=WHITE,
            background_color=CARD_BG, cursor_color=ACCENT2,
            size_hint=(1, None), height=dp(44),
            padding=(dp(12), dp(10)),
        )
        root.add_widget(self.pw_input)

        self.confirm_input = TextInput(
            hint_text="Confirm password", password=True, multiline=False,
            font_size=sp(14), foreground_color=WHITE,
            background_color=CARD_BG, cursor_color=ACCENT2,
            size_hint=(1, None), height=dp(44),
            padding=(dp(12), dp(10)),
        )
        if not has_pw:
            root.add_widget(self.confirm_input)

        self.err_label = Label(text="", font_size=sp(12), color=RED,
                               size_hint=(1, 0.05), halign="center")
        root.add_widget(self.err_label)

        unlock_btn = GradientButton(text="UNLOCK" if has_pw else "SET PASSWORD",
                                    bg_color=ACCENT2)
        unlock_btn.bind(on_release=lambda b: self._try_unlock())
        root.add_widget(unlock_btn)

        root.add_widget(NavBar(self.manager))
        self.add_widget(root)

    def _try_unlock(self):
        pw = self.pw_input.text
        stored = self._get_hash()
        if stored is None:
            # setting new password
            if len(pw) < 4:
                self.err_label.text = "Password too short (min 4)"
                return
            if pw != self.confirm_input.text:
                self.err_label.text = "Passwords do not match"
                return
            self._set_hash(pw)
            self._unlocked = True
            self._build_main()
        else:
            if _hash(pw) == stored:
                self._unlocked = True
                self._build_main()
            else:
                self.err_label.text = "Wrong password"
                self.pw_input.text = ""

    # ─── main vault UI ───
    def _build_main(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", spacing=dp(10), padding=(dp(16), dp(16), dp(16), dp(8)))

        hdr = BoxLayout(orientation="horizontal", size_hint=(1, 0.07))
        hdr.add_widget(Label(text="VAULT", font_size=sp(22), color=WHITE, bold=True,
                             halign="left", valign="middle"))
        add_btn = GradientButton(text="+", size_hint=(None, 1), width=dp(44),
                                 bg_color=ACCENT2)
        add_btn.bind(on_release=lambda b: self._add_dialog())
        hdr.add_widget(add_btn)
        # lock btn
        lock_btn = GradientButton(text="LOCK", size_hint=(None, 1), width=dp(60),
                                  bg_color=BORDER, txt_color=WHITE, font_size=sp(11))
        lock_btn.bind(on_release=lambda b: self._lock())
        hdr.add_widget(lock_btn)
        root.add_widget(hdr)

        scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        root.add_widget(scroll)

        root.add_widget(NavBar(self.manager))
        self.add_widget(root)
        self._refresh()

    def _lock(self):
        self._unlocked = False
        self._lock_screen()

    def _refresh(self):
        self.list_box.clear_widgets()
        items = self._load()
        if not items:
            self.list_box.add_widget(Label(
                text="No entries. Tap + to add.", font_size=sp(13), color=DIMMER,
                size_hint=(1, None), height=dp(50), halign="center", valign="middle"))
            return
        for item in items:
            self.list_box.add_widget(self._item(item))

    def _item(self, item):
        card = Card(size_hint=(1, None), height=dp(68))
        row = BoxLayout(orientation="horizontal", spacing=dp(10))
        col = BoxLayout(orientation="vertical", spacing=dp(3))
        col.add_widget(Label(text=item.get("title", ""), font_size=sp(15), color=WHITE,
                             halign="left", valign="middle", bold=True))
        # masked password
        masked = "•" * len(item.get("password", ""))
        col.add_widget(Label(text=f"{item.get('username', '')}  |  {masked}",
                             font_size=sp(12), color=DIM, halign="left"))
        row.add_widget(col)
        # reveal btn
        eye = Label(text="👁", font_size=sp(18), color=ACCENT2,
                    size_hint=(None, 1), width=dp(36),
                    halign="center", valign="middle")
        eye.bind(on_touch_down=lambda inst, touch, i=item: self._reveal(inst, touch, i))
        row.add_widget(eye)
        # delete
        del_btn = Label(text="✕", font_size=sp(16), color=RED,
                        size_hint=(None, 1), width=dp(36),
                        halign="center", valign="middle")
        del_btn.bind(on_touch_down=lambda inst, touch, iid=item["id"]: self._del(inst, touch, iid))
        row.add_widget(del_btn)
        card.add_widget(row)
        return card

    def _reveal(self, inst, touch, item):
        if not inst.collide_point(*touch.pos):
            return
        content = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(16))
        content.add_widget(Label(text=f"[b]{item.get('title', '')}[/b]", font_size=sp(16),
                                 color=WHITE, markup=True, halign="center"))
        content.add_widget(Label(text=f"User: {item.get('username', '')}", font_size=sp(14),
                                 color=ACCENT, halign="left"))
        pw_box = BoxLayout(orientation="horizontal", spacing=dp(8))
        pw_label = Label(text=item.get("password", ""), font_size=sp(16), color=GREEN,
                         halign="left", valign="middle")
        pw_box.add_widget(pw_label)
        content.add_widget(pw_box)
        if item.get("note"):
            content.add_widget(Label(text=f"Note: {item['note']}", font_size=sp(12),
                                     color=DIM, halign="left"))
        close = GradientButton(text="CLOSE", bg_color=BORDER, txt_color=WHITE)
        content.add_widget(close)
        popup = Popup(title="Details", content=content, size_hint=(0.8, 0.45),
                      background_color=get_color_from_hex("#0d1117"),
                      title_color=WHITE, separator_color=ACCENT2)
        close.bind(on_release=popup.dismiss)
        popup.open()

    def _del(self, inst, touch, iid):
        if not inst.collide_point(*touch.pos):
            return
        items = [i for i in self._load() if i["id"] != iid]
        self._save(items)
        self._refresh()

    def _add_dialog(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        ti_title = TextInput(hint_text="Title (e.g. Google)", multiline=False,
                             font_size=sp(14), foreground_color=WHITE,
                             background_color=CARD_BG, cursor_color=ACCENT2,
                             size_hint=(1, None), height=dp(40), padding=(dp(10), dp(8)))
        ti_user = TextInput(hint_text="Username / Email", multiline=False,
                            font_size=sp(14), foreground_color=WHITE,
                            background_color=CARD_BG, cursor_color=ACCENT2,
                            size_hint=(1, None), height=dp(40), padding=(dp(10), dp(8)))
        ti_pw = TextInput(hint_text="Password", password=True, multiline=False,
                          font_size=sp(14), foreground_color=WHITE,
                          background_color=CARD_BG, cursor_color=ACCENT2,
                          size_hint=(1, None), height=dp(40), padding=(dp(10), dp(8)))
        ti_note = TextInput(hint_text="Note (optional)", multiline=True,
                            font_size=sp(14), foreground_color=WHITE,
                            background_color=CARD_BG, cursor_color=ACCENT2,
                            size_hint=(1, None), height=dp(60), padding=(dp(10), dp(8)))
        content.add_widget(ti_title)
        content.add_widget(ti_user)
        content.add_widget(ti_pw)
        content.add_widget(ti_note)
        btn_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=dp(40))
        ok = GradientButton(text="SAVE", bg_color=ACCENT2)
        cancel = GradientButton(text="CANCEL", bg_color=BORDER, txt_color=WHITE)
        btn_row.add_widget(cancel)
        btn_row.add_widget(ok)
        content.add_widget(btn_row)
        popup = Popup(title="New Entry", content=content, size_hint=(0.85, 0.6),
                      background_color=get_color_from_hex("#0d1117"),
                      title_color=WHITE, separator_color=ACCENT2)
        ok.bind(on_release=lambda b: self._save_entry(
            ti_title.text, ti_user.text, ti_pw.text, ti_note.text, popup))
        cancel.bind(on_release=popup.dismiss)
        popup.open()

    def _save_entry(self, title, user, pw, note, popup):
        title = title.strip()
        pw = pw.strip()
        if not title or not pw:
            return
        items = self._load()
        items.insert(0, {
            "id": int(datetime.datetime.now().timestamp() * 1000),
            "title": title,
            "username": user.strip(),
            "password": pw,
            "note": note.strip(),
        })
        self._save(items)
        self._refresh()
        popup.dismiss()

    # ─── storage ───
    def _load(self):
        try:
            with open(VAULT_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self, items):
        with open(VAULT_FILE, "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def _get_hash(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
            return cfg.get("pw_hash")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _set_hash(self, pw):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"pw_hash": _hash(pw)}, f)


# ═══════════════════════════ App ═════════════════════════════════

class JSStudioApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(MemoScreen())
        sm.add_widget(DiaryScreen())
        sm.add_widget(VaultScreen())
        sm.current = "splash"

        # Android back button
        Window.bind(on_keyboard=self._on_key)
        return sm

    def _on_key(self, window, key, *args):
        if key == 27:  # ESC / Android back
            sm = self.root
            if sm.current == "home":
                return False  # let system exit
            elif sm.current in ("memo", "diary", "vault"):
                sm.transition = SlideTransition(direction="right")
                sm.current = "home"
                return True
        return False


if __name__ == "__main__":
    JSStudioApp().run()
