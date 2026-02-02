import sqlite3
import os
from backend.data_models import Verb
from backend.utilities import get_all_languages_with_tenses, get_all_deck_paths

all_languages = get_all_languages_with_tenses('backend/languages_tenses/tenses.json')

class DatabaseManager:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DB_PATH = os.path.abspath(os.path.join(self.BASE_DIR, "..", "database", "decks"))
        self.other_deck_paths = get_all_deck_paths()
        self.con = None
        self.cur = None
        self.current_db = None
        self.connected = False
        self.current_db_language = str()

        self.current_deck_data = {
            'deck_name': str(),
            'language': self.current_db_language,
            'verb_cards': list(),
        }
        self.current_verb_data = {
            'verb_id': int(),
            'original': str(),
            'infinitive': str(),
            'tenses': dict(),
        }

    def connect_to_db(self, db_name):
        if not os.path.isfile(os.path.join(self.DB_PATH, db_name+".db")):
            for path in self.other_deck_paths:
                if os.path.isfile(path):
                    self.con = sqlite3.connect(path)
                    break
        else:
            self.con = sqlite3.connect(os.path.join(self.DB_PATH, db_name+".db"))
        self.cur = self.con.cursor()
        self.current_db = db_name
        self.current_deck_data['deck_name'] = db_name
        self.current_deck_data['verb_cards'] = self.get_all_verbs()
        self.connected = True
        print(f"Connected to {self.current_db}")

    def change_connection(self, new_db_name):
        self.con.close()
        print("Changing connection")
        self.connect_to_db(new_db_name)

    def close_connection(self):
        self.con.close()
        self.connected = False
        self.current_db = None

    def is_database(self, db_name):
        return os.path.isfile(os.path.join(self.DB_PATH, db_name+".db"))

    def get_current_db_language(self) -> str:
        res = self.cur.execute("SELECT * FROM verbs")
        card_list = list(map(lambda x: x[0], res.description))
        for i in card_list:
            if i in all_languages.keys():
                self.current_db_language = i
                self.current_deck_data['language'] = i
                return i
        return "No language found."

    def change_db_name(self, new_name):
        if self.current_db == new_name: return
        old_name = self.current_db
        self.close_connection()
        os.rename(os.path.join(self.DB_PATH, old_name+".db"), os.path.join(self.DB_PATH, new_name+".db"))

    def remove_db(self):
        db_name = self.current_db
        self.close_connection()
        os.remove(os.path.join(self.DB_PATH, db_name+".db"))

    def create_deck_sql(self, verb_model : Verb, lang):
        self.cur.execute("PRAGMA foreign_keys = ON")
        tenses_template = []
        for tense in verb_model.tenses:
            tenses_template.append(f'"{tense}" TEXT')

        columns_sql = ", ".join(tenses_template)
        self.cur.execute(f"CREATE TABLE IF NOT EXISTS verbs ("
                       f"ID_VERB INTEGER PRIMARY KEY AUTOINCREMENT,"
                       f"{lang} TEXT,"
                       f"original TEXT,"
                       f"infinitive TEXT,"
                       f"{columns_sql})")

        for tense in verb_model.tenses:
            conjugation_template = []
            for conj in verb_model.tenses[tense]:
                conjugation_template.append(f'"{conj}" TEXT')

            conjugation_sql = ", ".join(conjugation_template)
            self.cur.execute(f'CREATE TABLE IF NOT EXISTS "{tense}" (ID INTEGER PRIMARY KEY AUTOINCREMENT, {conjugation_sql},verb_id INTEGER NOT NULL,FOREIGN KEY (verb_id) REFERENCES verbs (ID_VERB))')
        self.con.commit()
        self.current_deck_data['language'] = self.get_current_db_language()

    def insert_verb(self, verb):
        self.cur.execute("PRAGMA foreign_keys = ON")

        tenses = list(verb.tenses.keys())

        tense_columns = '", "'.join(tenses)
        full_input_data = [verb.original, verb.infinitive] + tenses
        verb_placeholders = ', '.join(['?'] * len(tenses))

        self.cur.execute(f'INSERT OR IGNORE INTO verbs (original, infinitive, "{tense_columns}") '
                         f''
                         f'VALUES (?, ?, {verb_placeholders})', full_input_data)

        verb_id = self.cur.lastrowid
        for tense in verb.tenses:
            input_tense = verb.tenses[tense]
            conjugation =  input_tense.keys()

            columns = '", "'.join(conjugation)
            placeholders = ', '.join(['?'] * len(conjugation))
            input_data = list(input_tense.values())
            input_data.append(verb_id)
            self.cur.execute(f'INSERT INTO "{tense}" ("{columns}", verb_id) VALUES ({placeholders}, ?)',
                        input_data)
        self.con.commit()
        self.current_deck_data['verb_cards'] = self.get_all_verbs()
        print("New Verb has been added")

    def get_all_db_files(self):
        dict_db_list = os.listdir(os.path.abspath(os.path.join(self.BASE_DIR, "..", "database", "decks")))
        return dict_db_list

    def get_db_file(self, filename) -> str:
        for root, dir, files in os.walk(os.path.join(self.BASE_DIR, "..", "database", "decks")):
            for file in files:
                if filename in str(file):
                    return os.path.join(self.BASE_DIR, "..", "database", "decks") + str(file)

    def get_table(self, table_name:str, verb:str) -> dict:
        try:
            self.get_current_db_language()
            self.cur.execute(f"SELECT ID_VERB FROM verbs WHERE infinitive =?", (verb, ))
            output = self.cur.fetchone()
            if output is None:
                print("Wrong verb")
                return {}
            verb_id = output

            self.cur.execute(f"SELECT * FROM {table_name} WHERE verb_id =?", (int(verb_id[0]), ))
            tense_output = self.cur.fetchone()[1:-1]
            if tense_output is None:
                print("Wrong tense")
                return {}

            table_dict = {}
            for conjug_ind in range(len(all_languages[self.current_db_language][table_name])):
                conjugation = all_languages[self.current_db_language][table_name][conjug_ind]
                table_dict[conjugation] = tense_output[conjug_ind]
            # print(table_dict)
            return table_dict
        except sqlite3.OperationalError as e:
            print(e)
            return {}

    def get_all_verb_info(self, verb_infinitive:str) -> dict:
        try:
            self.get_current_db_language()
            self.cur.execute(f"SELECT * FROM verbs WHERE infinitive =?", (str(verb_infinitive),))
            output = self.cur.fetchone()
            if output is None:
                print("This verb doesn't exist in this deck")
                return {}

            verb_data_output_list = list(output)

            verb_info_dict = {
                'verb_id': verb_data_output_list[0],
                'original': verb_data_output_list[2],
                'infinitive': verb_data_output_list[3],
                'tenses': dict()
            }

            for tense in verb_data_output_list[4:]:
                self.cur.execute(f'SELECT * FROM "{tense}" WHERE verb_id =?', (verb_info_dict['verb_id'], ))
                tense_list_output = self.cur.fetchone()[1:-1]

                conjugation_tense = {}
                for ind in range(len(all_languages[self.current_db_language][tense])):
                    current_conj = all_languages[self.current_db_language][tense][ind]
                    conjugation_tense[current_conj] = tense_list_output[ind]

                verb_info_dict['tenses'][tense] = conjugation_tense
            return verb_info_dict
        except sqlite3.OperationalError as e:
            print(e)
            return {}

    def get_some_info_from_verbs(self, *args) -> list:
        try:
            options_str = ', '.join(args)
            output = self.cur.execute(f"SELECT {options_str} FROM verbs").fetchall()
            return output
        except sqlite3.OperationalError as e:
            print(e)
            return []

    def get_all_verbs(self):
        try:
            output = self.cur.execute(f"SELECT * FROM verbs").fetchall()
            verbs_list = []
            for verb in output:
                # print(self.get_all_verb_info(verb[3]))
                verbs_list.append(self.get_all_verb_info(verb[3]))
            print(verbs_list)
            return verbs_list
        except sqlite3.OperationalError as e:
            print(e)
            return []

    def update_verb(self, verb_data, new_data):
        self.cur.execute(f"UPDATE verbs SET original = ?, infinitive = ? WHERE ID_VERB = ?",
                         (str(new_data["original"]), str(new_data['infinitive']), int(new_data['verb_id'])))
        
        verb_tenses = dict(list(verb_data['tenses'].items()))
        for tense in verb_tenses:
            argument_placeholders  = ""
            conjugations_arguments = []
            for conjugation in verb_tenses[tense]:
                argument_placeholders += f'"{conjugation}"=?, '
                conjugations_arguments.append(new_data[tense][conjugation])
            conjugations_arguments.append(new_data['verb_id'])
            self.cur.execute(f'UPDATE "{tense}" SET {argument_placeholders[:-2]} WHERE verb_id = ?',
                             conjugations_arguments)
        print("Verb data updated!")
        self.con.commit()
        self.current_deck_data['verb_cards'] = self.get_all_verbs()

    def delete_verb(self, verb_data:dict):
        for tense in dict(list(verb_data['tenses'].items())):
            self.cur.execute(f'DELETE from "{tense}" where verb_id=?', (verb_data['verb_id'], ))
        self.cur.execute("DELETE from verbs where ID_VERB=?", (verb_data['verb_id'], ))
        self.con.commit()
        self.current_deck_data['verb_cards'] = self.get_all_verbs()

def generate_new_tense_structure(tense_template : dict) -> Verb:
    tense_dict = {}
    for tense in tense_template:
        tense_dict[tense] = tense_template[tense]
    verb_structure = Verb("original", "Infinitive", tense_dict)
    return verb_structure
