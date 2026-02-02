from os.path import isdir, join

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from GUI.global_screen import GlobalScreenManager
from backend.data_manager import DatabaseManager
from backend.utilities import add_new_deck_path, get_all_deck_paths, remove_deck_path


class SettingsScreen(Screen):
    def __init__(self, screen_manager : GlobalScreenManager, database_manager:DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.db_manager = database_manager

    def on_pre_enter(self, *args):
        self.load_paths()

    def load_paths(self):
        self.ids['path_stack_layout'].clear_widgets()
        for path in get_all_deck_paths():

            path = PathButtonWidget(path=path, root=self)
            self.ids['path_stack_layout'].add_widget(path)
        self.ids['path_stack_layout'].height = self.ids['path_stack_layout'].minimum_height

    def open_filechooser_popup(self):
        def update_path_text(*args):
            text_input.text = str(args[1][0])

        def add_new_path(path):
            if len(path) == 0:
                text_input.hint_text = "Choose directory"
                return
            add_new_deck_path(path)
            on_close_popup()

        def on_close_popup(*args):
            pathchooser_popup.dismiss()
            self.load_paths()

        main_layout = BoxLayout(orientation="vertical")

        pathchooser_popup = Popup(title='Path Selection', content=main_layout, size_hint=(None, None),
                                   size=(dp(400), dp(400)))

        text_input = TextInput(hint_text="Path...", write_tab=False, multiline=False, font_size=dp(12),size_hint=(1, .1))
        filechooser = FileChooserListView(dirselect=True, filters=[self.is_dir])
        filechooser.bind(selection=update_path_text)

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(30))
        select_button = Button(text='Select', size_hint=(1, 1))
        close_button = Button(text='Close', size_hint=(1, 1))

        button_layout.add_widget(select_button)
        button_layout.add_widget(close_button)

        select_button.bind(on_press=lambda value: add_new_path(text_input.text))
        close_button.bind(on_press=on_close_popup)

        main_layout.add_widget(filechooser)
        main_layout.add_widget(text_input)
        main_layout.add_widget(button_layout)

        pathchooser_popup.open()

    def is_dir(self, directory, filename):
        return isdir(join(directory, filename))

    def on_add_new_path(self):
        self.open_filechooser_popup()

    def delete_path(self, path):
        remove_deck_path(path)
        self.load_paths()

    def on_exit(self):
        self.screen_manager.transition = SlideTransition(direction='up')
        self.screen_manager.switch_to(self.screen_manager.screens_dict['main_screen'])


class PathButtonWidget(BoxLayout):
    def __init__(self, path:str, root, **kwargs):
        super().__init__(**kwargs)
        self.root = root
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = dp(37)
        self.path = path
        self.spacing = dp(1)
        self.path_button = Button(
            text=self.path,
            color=(1,1,1,1),
            halign='left',
            valign='middle',
            size_hint=(.8, 1),
        )
        self.path_button.padding = (dp(10), 0)
        self.path_button.bind(size=lambda instance, value: setattr(instance, 'text_size', self.path_button.size))

        self.delete_button = Button(
            text="delete",
            size_hint=(.1, 1),
        )
        self.delete_button.bind(on_release=lambda value: self.root.delete_path(self.path))

        self.edit_button = Button(
            text="edit",
            size_hint=(.1, 1),
        )

        self.add_widget(self.path_button)
        self.add_widget(self.delete_button)
        self.add_widget(self.edit_button)
