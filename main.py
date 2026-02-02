import os

from kivy import Config
from kivy.core.text import LabelBase, DEFAULT_FONT

from GUI.card_screen import EditCardScreen, NewCardScreen
from GUI.deck_screen import NewDeckCreatorScreen, DeckScreen, EditDeckScreen
from GUI.exercise_screen import ExerciseScreen
from GUI.global_screen import GlobalScreenManager
from GUI.main_screen import MainScreen
from GUI.settings_screen import SettingsScreen
from backend.data_manager import DatabaseManager, all_languages
from kivy.app import App
from kivy.lang import Builder
# tense_options = ["Spanish"]

db_manager = DatabaseManager()
cwd = os.getcwd()

Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/MainScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/NewDeckScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/DeckScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/EditDeckScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/EditCardScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/NewCardScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/ExerciseScreen.kv'))
Builder.load_file(os.path.join(cwd, 'GUI/kv_scripts/SettingsScreen.kv'))


class MainApp(App):
    def build(self):
        return global_screen

LabelBase.register(DEFAULT_FONT, os.path.join(cwd, 'fonts/AtkinsonHyperlegibleMono.ttf'))

global_screen = GlobalScreenManager()

global_screen.add_new_screen('main_screen', MainScreen(name='main_screen', screen_manager=global_screen,
                                                       database_manager=db_manager))
global_screen.add_new_screen('new_deck_creator_screen', NewDeckCreatorScreen(name='new_deck_creator_screen',
    screen_manager=global_screen, database_manager=db_manager, languages_options=list(all_languages.keys())))
global_screen.add_new_screen('deck_screen', DeckScreen(name='deck_screen', screen_manager=global_screen,
    database_manager=db_manager))
global_screen.add_new_screen('edit_deck_screen', EditDeckScreen(name='edit_deck_screen', screen_manager=global_screen,
    database_manager=db_manager))
global_screen.add_new_screen('edit_card_screen', EditCardScreen(name='edit_card_screen', screen_manager=global_screen,
    database_manager=db_manager))
global_screen.add_new_screen('new_card_screen', NewCardScreen(name='new_card_screen', screen_manager=global_screen,
    database_manager=db_manager))
global_screen.add_new_screen('exercise_screen', ExerciseScreen(name='exercise_screen', screen_manager=global_screen,
    database_manager=db_manager))
global_screen.add_new_screen('settings_screen', SettingsScreen(name='settings_screen', screen_manager=global_screen,
    database_manager=db_manager))


if __name__ == '__main__':
    app = MainApp()
    app.run()