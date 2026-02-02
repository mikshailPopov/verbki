from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.metrics import dp
from GUI.global_screen import GlobalScreenManager
from backend.data_manager import generate_new_tense_structure, all_languages, DatabaseManager


class NewDeckCreatorScreen(Screen):
    def __init__(self, screen_manager : GlobalScreenManager, database_manager : DatabaseManager, languages_options:list, **kwargs):
        self.sm = screen_manager
        self.languages_list = languages_options
        self.database_manager = database_manager
        self.selected_option = None
        super().__init__(**kwargs)

    def create_popup(self, warning_text:str):
        t_layout = BoxLayout(orientation="vertical")
        p_label = Label(text=warning_text)
        p_button = Button(text='close', size_hint=(1, .2))
        t_layout.add_widget(p_label)
        t_layout.add_widget(p_button)

        warning_popup = Popup(title='Warning', content=t_layout, size_hint=(None, None),
                                   size=(dp(400), dp(400)))
        warning_popup.open()
        p_button.bind(on_press=warning_popup.dismiss)

    def load_langauge_options(self):
        self.ids['language_dropdown'].clear_widgets()
        self.ids['new_deck_name_input'].text = "New Verb Deck"
        for option_ind in range(len(self.languages_list)):
            btn = LanguageTenseButton(self, text_arg=self.languages_list[option_ind])
            self.ids['language_dropdown'].add_widget(btn)

    def on_tense_select(self, opt_value):
        self.selected_option = opt_value

    def on_create_new_deck(self, text_input):
        if self.selected_option is None:
            self.create_popup("Select Language")
            return
        if self.database_manager.is_database(text_input.text):
            self.create_popup("Deck with that name already exists")
            return

        deck_template = generate_new_tense_structure(all_languages[self.selected_option.lower()])
        self.database_manager.connect_to_db(text_input.text)
        self.database_manager.create_deck_sql(deck_template, self.selected_option.lower())

        self.sm.screens_dict['main_screen'].update_database()

        self.sm.transition = SlideTransition(direction='right')
        self.sm.switch_to(self.sm.screens_dict['main_screen'])

    def on_exit(self):
        self.sm.transition = SlideTransition(direction='right')
        self.sm.switch_to(self.sm.screens_dict['main_screen'])


class DeckScreen(Screen):
    deck_name = StringProperty()
    def __init__(self, screen_manager, database_manager:DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_deck_connected')
        self.database_manager = database_manager
        self.sm = screen_manager
        self.buttons = []

    def on_deck_connected(self, values):
        self.dispatch('on_deck_connected', values)

    def connect_to_deck(self, *args):
        self.deck_name = str(self.database_manager.current_db)

    def load_cards(self):
        verb_list = self.database_manager.get_some_info_from_verbs("infinitive", "original")
        for ind in range(len(verb_list)):
            new_button = CardButton(text=f"{verb_list[ind][1]}/{verb_list[ind][0]}", verb_arg=verb_list[ind]
                                    , root=self)
            self.buttons.append(new_button)
            self.ids.verb_list_stack.add_widget(new_button)

    def switch_to_card(self, verb):
        self.database_manager.current_verb_data = self.database_manager.get_all_verb_info(verb[0])
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['edit_card_screen'])
    
    def on_pre_enter(self):
        self.ids.verb_list_stack.clear_widgets()
        self.load_cards()

    def on_new_card_screen_press(self):
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['new_card_screen'])

    def on_edit_deck_screen_press(self):
        self.sm.transition = SlideTransition(direction='down')
        self.sm.switch_to(self.sm.screens_dict['edit_deck_screen'])

    def create_popup(self):
        t_layout = BoxLayout(orientation="vertical")
        count_label = Label(text=f"The Deck is empty.")
        p_button = Button(text='Go back.', size_hint=(1, .2))
        t_layout.add_widget(count_label)
        t_layout.add_widget(p_button)
        warning_popup = Popup(title='Finish!', content=t_layout, size_hint=(None, None),
                                   size=(dp(400), dp(400)))
        warning_popup.open()
        p_button.bind(on_press=warning_popup.dismiss)

    def on_exercise_screen_press(self):
        if len(self.database_manager.current_deck_data['verb_cards']) == 0:
            self.create_popup()
            return
        self.sm.transition = SlideTransition(direction='left')
        self.sm.switch_to(self.sm.screens_dict['exercise_screen'])

    def on_exit(self):
            self.sm.transition = SlideTransition(direction='right')
            self.sm.switch_to(self.sm.screens_dict['main_screen'])


class EditDeckScreen(Screen):
    def __init__(self, screen_manager, database_manager : DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.database_manager = database_manager
        self.sm = screen_manager
        self.deck_data = None

    def load_deck_data(self):
        self.ids['language_dropdown'].clear_widgets()
        self.ids['deck_name_input'].text = self.deck_data['deck_name']
        self.ids['current_deck_language_button'].text = self.deck_data['language']

    def save_new_data(self):
        self.database_manager.change_db_name(self.ids["deck_name_input"].text)
        self.deck_data = None
        self.sm.transition = SlideTransition(direction='up')
        self.sm.switch_to(self.sm.screens_dict['main_screen'])
        self.sm.screens_dict['main_screen'].update_database()

    def delete_deck(self):
        self.deck_data = None
        self.sm.transition = SlideTransition(direction='up')
        self.sm.switch_to(self.sm.screens_dict['main_screen'])
        self.sm.screens_dict['main_screen'].on_remove_database()

    def on_pre_enter(self, *args):
        self.deck_data = self.database_manager.current_deck_data
        self.database_manager.get_current_db_language()
        self.load_deck_data()

    def on_exit(self):
        self.deck_data = None
        self.sm.transition = SlideTransition(direction='up')
        self.sm.switch_to(self.sm.screens_dict['deck_screen'])

class LanguageTenseButton(Button):
    def __init__(self, root, text_arg, **kwargs):
        super().__init__(**kwargs)
        self.text=str(text_arg)
        self.size_hint_y=None
        self.height=30
        self.bind(on_release=lambda value: root.ids['language_dropdown'].select(self.text))

class CardButton(Button):
    def __init__(self, text, verb_arg, root,**kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint=(1, None)
        self.height=dp(50)
        self.verb_arg = verb_arg
        self.root = root

    def on_press(self):
        self.root.switch_to_card(self.verb_arg)

