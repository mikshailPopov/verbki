import random
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.properties import ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from GUI.card_screen import NewTenseTableWidget
from GUI.global_screen import GlobalScreenManager
from backend.data_manager import DatabaseManager, all_languages


class ExerciseScreen(Screen):
    def __init__(self, screen_manager : GlobalScreenManager, database_manager : DatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.sm = screen_manager
        self.db_manager = database_manager
        self.tense = dict()
        self.tables_input_widgets = dict()
        self.total_verbs = list()
        self.current_verb = None

        self.default_colors = {
            "hint_text": (0.5, 0.5, 0.5, 1.0),
            "foreground_color": (0, 0, 0, 1),
        }
        self.correct_colors = {
            "hint_text": (0,1,0,1),
            "foreground_color": (0, 1, 0, 1),
        }
        self.incorrect_colors = {
            "hint_text": (.75, 0, 0, 1),
            "foreground_color": (.75, 0, 0, 1),
        }
        self.incomplete_colors = {
            "hint_text": (.6, .6, 0, 1),
            "foreground_color": (.6, .6, 0, 1),
        }

        self.correct_count = 0
        self.incorrect_count = 0

    def choose_random_verb(self):
        if len(self.total_verbs) == 0:
            self.create_popup()
            return
        self.current_verb = random.choice(self.total_verbs)
        self.ids['verb_title'].text = f"{self.current_verb['original']} | {self.current_verb['infinitive']}"
        for t in self.tables_input_widgets:
            for i in self.tables_input_widgets[t]:
                self.tables_input_widgets[t][i].text = ""

    def start_exercise(self):
        self.correct_count = 0
        self.incorrect_count = 0
        self.ids['correct_counter_label'].text = f'Correct: {self.correct_count}'
        self.ids['incorrect_counter_label'].text = f'Incorrect: {self.incorrect_count}'

        self.choose_random_verb()

    def next_verb(self):
        correct_tenses = []
        incomplete_tenses = []
        incorrect_tenses = []

        for tense in self.current_verb['tenses']:
            for conjugation in self.current_verb['tenses'][tense]:
                if (str(self.tables_input_widgets[tense][conjugation].text)
                        == str(self.current_verb['tenses'][tense][conjugation])):
                    correct_tenses.append(self.tables_input_widgets[tense][conjugation])
                elif not self.tables_input_widgets[tense][conjugation].text.strip():
                    incomplete_tenses.append(self.tables_input_widgets[tense][conjugation])
                else:
                    incorrect_tenses.append(self.tables_input_widgets[tense][conjugation])

        if len(incorrect_tenses) == 0 and len(incomplete_tenses) == 0:
            self.correct_count += 1
        elif len(incorrect_tenses) != 0:
            self.incorrect_count += 1

        self.ids['correct_counter_label'].text = f'Correct: {self.correct_count}'
        self.ids['incorrect_counter_label'].text = f'Incorrect: {self.incorrect_count}'
        self.change_input_widgets_color(correct_tenses, self.correct_colors)
        self.change_input_widgets_color(incomplete_tenses, self.incomplete_colors)
        self.change_input_widgets_color(incorrect_tenses, self.incorrect_colors)

        self.total_verbs.remove(self.current_verb)
        self.choose_random_verb()

    def change_input_widget_color(self, widget, colors):
        widget.foreground_color = colors['foreground_color']
        widget.hint_text_color = colors['hint_text']

    def change_input_widgets_color(self, widgets, colors):
        for wid in widgets:
            wid.foreground_color = colors['foreground_color']
            wid.hint_text_color = colors['hint_text']

    def on_text_input_focus(self, instance, value):
        if value:
            for t in self.tables_input_widgets:
                for i in self.tables_input_widgets[t]:
                    self.change_input_widget_color(self.tables_input_widgets[t][i], self.default_colors)
        else:
            pass

    def on_pre_enter(self):
        self.ids.tense_stack_layout.clear_widgets()
        self.db_manager.get_current_db_language()
        self.tense = all_languages[self.db_manager.current_db_language]
        for t in self.tense:
            new_tense_table = TenseTablesWidget(tense_data=[t, self.tense[t]])
            self.tables_input_widgets[new_tense_table.tense_name] = new_tense_table.text_inputs
            for conj in self.tables_input_widgets[new_tense_table.tense_name]:
                new_tense_table.text_inputs[conj].bind(focus=self.on_text_input_focus)
            self.ids.tense_stack_layout.add_widget(new_tense_table)
        self.ids.tense_stack_layout.height = self.ids.tense_stack_layout.minimum_height
        self.total_verbs = self.db_manager.current_deck_data['verb_cards'].copy()
        self.start_exercise()

    def create_popup(self):
        t_layout = BoxLayout(orientation="vertical")
        # p_label = Label(text="Finish!", size_hint=(1, .3))
        count_label = Label(text=f"You have {self.correct_count} correct out of {len(self.db_manager.current_deck_data['verb_cards'])}")
        p_button = Button(text='Go back.', size_hint=(1, .2))
        # t_layout.add_widget(p_label)
        t_layout.add_widget(count_label)
        t_layout.add_widget(p_button)

        warning_popup = Popup(title='Finish!', content=t_layout, size_hint=(None, None),
                                   size=(dp(400), dp(400)))
        warning_popup.bind(on_dismiss=self.on_exit)
        warning_popup.open()

        p_button.bind(on_press=warning_popup.dismiss)

    def on_exit(self, instance):
        self.sm.transition = SlideTransition(direction='right')
        self.sm.switch_to(self.sm.screens_dict['deck_screen'])


class TenseTablesWidget(BoxLayout):
    def __init__(self, tense_data, **kwargs):
        super(TenseTablesWidget, self).__init__(**kwargs)
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