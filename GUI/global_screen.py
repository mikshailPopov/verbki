from kivy.uix.screenmanager import ScreenManager, Screen


class GlobalScreenManager(ScreenManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        else:
            print(f"Instance {cls._instance} already exists.")
        return cls._instance

    def __init__(self, **kwargs):
        self.screens_dict = {}
        super().__init__(**kwargs)

    def add_new_screen(self, screen_name : str, new_screen : Screen):
        self.screens_dict.update({screen_name: new_screen})
        self.add_widget(self.screens_dict[screen_name])
