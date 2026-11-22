from kivy.app import App
from kivy.uix.label import Label

class JSApp(App):
    def build(self):
        return Label(text='JS's STUDIO\nWELCOME', font_size='32sp')

if __name__ == '__main__':
    JSApp().run()