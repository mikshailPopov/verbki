from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.metrics import dp
from GUI.global_screen import GlobalScreenManager
from backend.data_manager import DatabaseManager


class MainScreen(Screen):
    def __init__(self, screen_manager : GlobalScreenManager, database_manager : DatabaseManager, **kwargs):
        self.sm = screen_manager
        self.database_manager = database_manager
        self.register_event_type('on_database_update')
        self.register_event_type('on_remove_database')
        super().__init__(**kwargs)

    def on_database_update(self):
        self.load_decks(self.ids['deck_stack_L'])

    def on_remove_database(self):
        self.remove_database()
        self.update_database()

    def update_database(self):
        self.dispatch("on_database_update")

    def remove_database(self):
        self.database_manager.remove_db()

    def load_decks(self, widget):
        widget.clear_widgets()
        deck_list = self.database_manager.get_db_files_from_all_path()
        for i in range(0, len(deck_list)):
            new_btn = DeckButton(deck_title=deck_list[i][:-3], root=widget)
            new_btn.deck_button.bind(on_press=self.on_select_deck_pressed)

            widget.add_widget(new_btn)

        widget.height = widget.minimum_height

    def on_select_deck_pressed(self, widget):
        if self.database_manager.connected: self.database_manager.change_connection(widget.text)
        else: self.database_manager.connect_to_db(widget.text)
        self.sm.screens_dict['deck_screen'].connect_to_deck()
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['deck_screen'])

    def on_deck_paths_screen_pressed(self):
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['deck_paths_screen'])

    def on_new_deck_pressed(self):
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['new_deck_creator_screen'])


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

