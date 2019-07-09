from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class Root(BoxLayout):
    pass


class ExampleApp(App):
    def build(self):
        return Root()


ExampleApp().run()