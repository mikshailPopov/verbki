import os.path
from os.path import isdir

from kivy.graphics import Color, Rectangle
from kivy.properties import ReferenceListProperty, colormap
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserLayout, FileChooserListView
from kivy.uix.layout import Layout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.metrics import dp
from kivy.uix.textinput import TextInput

from backend.utilities import add_new_deck_path


class MainScreen(Screen):
    def __init__(self, screen_manager, database_manager, **kwargs):
        self.sm = screen_manager
        self.database_manager = database_manager
        self.register_event_type('on_database_update')
        self.register_event_type('on_remove_database')
        super().__init__(**kwargs)

    def on_database_update(self):
        self.load_dict_db(self.ids['dict_stack'])

    def on_remove_database(self):
        self.remove_database()
        self.update_database()

    def update_database(self):
        self.dispatch("on_database_update")

    def remove_database(self):
        self.database_manager.remove_db()

    def load_dict_db(self, widget):
        widget.clear_widgets()
        deck_list = self.database_manager.get_all_db_files()
        for i in range(0, len(deck_list)):
            new_btn = DeckButton(deck_title=deck_list[i][:-3], root=widget)
            new_btn.deck_button.bind(on_press=self.on_deck_press)

            widget.add_widget(new_btn)

        widget.height = widget.minimum_height

    def on_deck_press(self, widget):
        if self.database_manager.connected: self.database_manager.change_connection(widget.text)
        else: self.database_manager.connect_to_db(widget.text)
        self.sm.screens_dict['deck_screen'].connect_to_deck()
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['deck_screen'])

    def switch_to_new_deck(self):
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['new_deck_creator_screen'])

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
        return isdir(os.path.join(directory, filename))

    def add_existing_deck(self):
        self.open_filechooser_popup()
    # def switch_to_settings_screen(self):
    #     self.sm.transition = SlideTransition(direction='down')
    #     self.sm.switch_to(self.sm.screens_dict['settings_screen'])


class DeckButton(BoxLayout):
    def __init__(self, deck_title, root, **kwargs):
        super().__init__(**kwargs)
        self.orientation='horizontal'
        self.size_hint = (1, None)
        self.height = dp(47)
        self.deck_button = Button(
            text=deck_title,
            color=(1,1,1,1),
            halign='left',
            valign='middle',
            size_hint=(1, None),
            height=dp(47),
            width=dp(518)
        )
        self.deck_button.padding = (dp(20), 0)
        self.deck_button.bind(size=lambda instance, value: setattr(instance, 'text_size', self.deck_button.size))

        self.add_widget(self.deck_button)

