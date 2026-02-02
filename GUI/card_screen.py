from kivy.graphics import Rectangle, Color
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from backend.data_manager import all_languages, DatabaseManager
from backend.data_models import Verb


class EditCardScreen(Screen):
    def __init__(self, database_manager : DatabaseManager, screen_manager,**kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.db_manager = database_manager
        self.card_data = None
        self.tense_text_input_widgets = {}

    def load_tense_widgets_and_card_data(self):
        self.ids.tense_stack.clear_widgets()
        self.ids.original_input.text = self.card_data['original']
        self.ids.infinitive_input.text = self.card_data['infinitive']

        for tense in dict(list(self.card_data['tenses'].items())):
            tense_table = TenseTableWidget(tense=tense, conjugation=self.card_data['tenses'][tense])
            self.tense_text_input_widgets[tense] = tense_table.text_inputs
            self.ids.tense_stack.add_widget(tense_table)
        self.ids.tense_stack.height = self.ids.tense_stack.minimum_height

    def delete_card(self):
        self.db_manager.delete_verb(self.card_data)
        self.on_exit()

    def save_new_data(self):
        new_card_data = dict()
        new_card_data['verb_id'] = self.card_data['verb_id']
        new_card_data['original'] = self.ids['original_input'].text
        new_card_data['infinitive'] = self.ids.infinitive_input.text

        tenses = dict(list(self.card_data['tenses'].items()))
        for tense in tenses:
            conjugation_dict = dict()
            for conjugation in tenses[tense]:
                conjugation_dict[conjugation] = self.tense_text_input_widgets[tense][conjugation].text
            new_card_data[tense] = conjugation_dict
        self.db_manager.update_verb(self.card_data, new_card_data)
        self.on_exit()

    def on_pre_enter(self, *args):
        print(self.db_manager.current_verb_data)
        self.card_data = self.db_manager.current_verb_data
        self.load_tense_widgets_and_card_data()

    def on_exit(self):
        self.card_data = None
        self.sm.transition = SlideTransition(direction='right')
        self.sm.switch_to(self.sm.screens_dict['deck_screen'])


class NewCardScreen(Screen):
    def __init__(self, screen_manager, database_manager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.db_manager = database_manager
        self.tense = None
        self.tables = {}

    def load_empty_tense_tables(self):
        self.ids.tense_stack_layout.clear_widgets()
        self.ids.original_textinput.text = ""
        self.ids.infinitive_textinput.text = ""

        self.db_manager.get_current_db_language()
        self.tense = all_languages[self.db_manager.current_db_language]
        for t in self.tense:
            new_tense_table = NewTenseTableWidget(tense_data=[t, self.tense[t]])
            self.tables[new_tense_table.tense_name] = new_tense_table.text_inputs
            self.ids.tense_stack_layout.add_widget(new_tense_table)
        self.ids.tense_stack_layout.height = self.ids.tense_stack_layout.minimum_height

    def on_create(self):
        tenses_dict = {}
        for tense in self.tables:
            conjugation_dict = {}
            for conjugation in self.tables[tense]:
                conjugation_dict[conjugation] = self.tables[tense][conjugation].text
            tenses_dict[tense] = conjugation_dict
        new_verb = Verb(self.ids.original_textinput.text, self.ids.infinitive_textinput.text, tenses_dict)
        self.db_manager.insert_verb(new_verb)
        self.on_exit()

    def on_exit(self):
        self.sm.transition = SlideTransition(direction='right')
        self.sm.switch_to(self.sm.screens_dict['deck_screen'])


class NewTenseTableWidget(BoxLayout):
    def __init__(self, tense_data, **kwargs):
        super(NewTenseTableWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.width = dp(200)
        self.bind(minimum_height=self.setter('height'))

        self.tense_name = str(tense_data[0])
        self.text_inputs = {}

        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos= lambda value, value2: self.update_bg(self.bg, self),
                  size=lambda value, value2: self.update_bg(self.bg, self))

        self.tense_label = Label(
            text=self.tense_name,
            size_hint=(1, None),
            height=dp(50),
            font_size=dp(14),
            color=(1,1,1,1),
            halign='center',
            valign='middle'
        )

        self.b1 = StackLayout(
            spacing=dp(1), size_hint_y=None, width=self.width, orientation = 'lr-tb'
        )
        self.b1.bind(minimum_height=self.b1.setter('height'))

        with self.b1.canvas.before:
            Color(.1,.1,.1,1)
            self.bg1 = Rectangle(pos=self.b1.pos, size=self.b1.size)
        self.b1.bind(pos=lambda value, value2: self.update_bg(self.bg1, self.b1),
                     size=lambda value, value2: self.update_bg(self.bg1, self.b1))
        self.add_widget(self.tense_label)
        self.add_widget(self.b1)

        for conjugation in tense_data[1]:
            self.b2 = BoxLayout(
                orientation='horizontal', size_hint=(1, None), height=dp(30)
            )
            self.b1.add_widget(self.b2)

            self.conjugation_label = Label(text=str(conjugation), color=(1,1,1,1),font_size=dp(14))
            self.conjugation_text_input = TextInput(hint_text="Type here...", write_tab=False, multiline=False, font_size=dp(14))

            self.text_inputs[self.conjugation_label.text] = self.conjugation_text_input

            self.b2.add_widget(self.conjugation_label)
            self.b2.add_widget(self.conjugation_text_input)



    @staticmethod
    def update_bg(*args):
        args[0].pos = args[1].pos
        args[0].size = args[1].size


class TenseTableWidget(BoxLayout):
    def __init__(self, tense, conjugation, **kwargs):
        super(TenseTableWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.width = dp(200)
        self.bind(minimum_height=self.setter('height'))

        self.text_inputs = {}

        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos= lambda value, value2: self.update_bg(self.bg, self),
                  size=lambda value, value2: self.update_bg(self.bg, self))

        self.tense_label = Label(
            text=str(tense),
            size_hint=(1, None),
            height=dp(50),
            font_size=dp(14),
            color=(1,1,1,1),
            halign='center',
            valign='middle'
        )

        self.b1 = StackLayout(
            spacing=dp(1), size_hint_y=None, width=self.width, orientation = 'lr-tb'
        )
        self.b1.bind(minimum_height=self.b1.setter('height'))

        with self.b1.canvas.before:
            Color(.1,.1,.1,1)
            self.bg1 = Rectangle(pos=self.b1.pos, size=self.b1.size)
        self.b1.bind(pos=lambda value, value2: self.update_bg(self.bg1, self.b1),
                     size=lambda value, value2: self.update_bg(self.bg1, self.b1))
        self.add_widget(self.tense_label)
        self.add_widget(self.b1)

        for con in conjugation:
            self.b2 = BoxLayout(
                orientation='horizontal', size_hint=(1, None), height=dp(30)
            )
            self.b1.add_widget(self.b2)

            self.conjugation_label = Label(text=str(con), color=(1,1,1,1),font_size=dp(14))
            self.conjugation_text_input = TextInput(hint_text="Type here...", write_tab=False, multiline=False, font_size=dp(14))

            self.conjugation_text_input.text = str(conjugation[con])
            self.text_inputs[self.conjugation_label.text] = self.conjugation_text_input

            self.b2.add_widget(self.conjugation_label)
            self.b2.add_widget(self.conjugation_text_input)

    @staticmethod
    def update_bg(*args):
        args[0].pos = args[1].pos
        args[0].size = args[1].size