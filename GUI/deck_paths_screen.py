from contextlib import suppress
from os.path import isdir, join
from kivy.compat import text_type
from kivy.graphics import Rectangle, Color
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from GUI.global_screen import GlobalScreenManager
from backend.data_manager import DatabaseManager
from backend.utilities import add_new_deck_path, get_all_deck_paths, remove_deck_path, is_dir


class DeckPathsScreen(Screen):
    def __init__(self, screen_manager : GlobalScreenManager, database_manager : DatabaseManager, **kwargs):
        self.sm = screen_manager
        self.database_manager = database_manager
        super().__init__(**kwargs)

    def load_deck_paths(self):
        self.ids['path_stack'].clear_widgets()
        paths_list = get_all_deck_paths()
        for path in paths_list:
            path_button = DeckPathWidget(str(path))
            path_button.remove_button.bind(on_press=lambda value: self.on_remove_path_pressed(path_button.path_text.text))
            self.ids['path_stack'].add_widget(path_button)
        self.ids['path_stack'].height = self.ids['path_stack'].minimum_height

    def open_filechooser_popup(self):
        def update_path_text(*args):
            text_input.text = str(args[1][0])

        def on_select_path_pressed(path):
            if len(path) == 0:
                text_input.hint_text = "Choose directory"
                return
            add_new_deck_path(path)
            self.load_deck_paths()
            on_close_popup_pressed()

        def on_close_popup_pressed(*args):
            path_chooser_popup.dismiss()

        popup_layout = BoxLayout(orientation="vertical")
        path_chooser_popup = Popup(title='Path Selection', content=popup_layout, size_hint=(None, None),
                                   size=(dp(400), dp(400)))

        text_input = TextInput(hint_text="Path...", write_tab=False, multiline=False, font_size=dp(12),size_hint=(1, .1))

        filechooser = FileChooserListView(dirselect=True, filters=[is_dir])
        filechooser.bind(selection=update_path_text)

        select_button = Button(text='Select', size_hint=(1, 1))
        close_button = Button(text='Close', size_hint=(1, 1))

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(30))
        button_layout.add_widget(select_button)
        button_layout.add_widget(close_button)

        select_button.bind(on_press=lambda value: on_select_path_pressed(text_input.text))
        close_button.bind(on_press=on_close_popup_pressed)

        popup_layout.add_widget(filechooser)
        popup_layout.add_widget(text_input)
        popup_layout.add_widget(button_layout)

        path_chooser_popup.open()

    def on_add_path_pressed(self):
        self.open_filechooser_popup()

    def on_back_pressed(self):
        self.sm.transition = SlideTransition(direction='right')
        self.sm.switch_to(self.sm.screens_dict['main_screen'])

    def on_remove_path_pressed(self, path):
        remove_deck_path(path)
        self.load_deck_paths()


class DeckPathWidget(BoxLayout):
    def __init__(self, path_text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height=dp(47)
        self.width=dp(518)
        self.path_text = Label(
            text=path_text,
            size_hint=(.9, None),
            color=(0,0,0,1),
            halign='left',
            valign='middle',
            height=dp(47),
            width=dp(518),
            padding=(dp(21), dp(0)))
        self.path_text.bind(size=self.path_text.setter('text_size'))

        self.remove_button = Button(text="X", size_hint=(.1, 1), background_color=(1,0,0,1))
        self.add_widget(self.path_text)
        self.add_widget(self.remove_button)